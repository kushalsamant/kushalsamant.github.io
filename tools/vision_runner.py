import os
import sys
import time
import base64
import logging
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Logging ────────────────────────────────────────────────
DEBUG = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# ── Env validation ─────────────────────────────────────────
REQUIRED_ENV_VARS = [
    "TOGETHER_API_KEY",
    "TOGETHER_API_URL",
    "TOGETHER_MODEL_ID",
]

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    log.error("Missing required environment variables: %s", ", ".join(missing_vars))
    log.error("Please check your .env file.")
    sys.exit(1)

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = os.getenv("TOGETHER_API_URL")
MODEL_ID = os.getenv("TOGETHER_MODEL_ID")
TIMEOUT = int(os.getenv("TOGETHER_TIMEOUT", "120"))
RETRIES = int(os.getenv("TOGETHER_RETRIES", "2"))

log.debug("API URL: %s", TOGETHER_API_URL)
log.debug("Model: %s", MODEL_ID)
log.debug("Timeout: %ss | Retries: %s", TIMEOUT, RETRIES)

HEADERS = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json",
}


def encode_image_to_base64(image_path: Path) -> tuple[str, str]:
    log.debug("Encoding image: %s", image_path.name)

    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    suffix = image_path.suffix.lower()

    if suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".png":
        mime = "image/png"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/jpeg"

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    log.debug("Encoded %s as %s (%d chars)", image_path.name, mime, len(encoded))
    return mime, encoded


def run_vision(image_path: Path, prompt: str) -> str:
    log.info("Analysing: %s", image_path.name)

    mime_type, encoded_image = encode_image_to_base64(Path(image_path))

    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{encoded_image}"
                        },
                    },
                ],
            }
        ],
    }

    log.debug("Payload size: ~%d chars", len(str(payload)))

    for attempt in range(1, RETRIES + 1):
        try:
            log.debug("API call attempt %d/%d", attempt, RETRIES)

            response = requests.post(
                TOGETHER_API_URL,
                headers=HEADERS,
                json=payload,
                timeout=TIMEOUT,
            )

            log.debug("HTTP %s", response.status_code)
            response.raise_for_status()

            data = response.json()
            result = data["choices"][0]["message"]["content"].strip()

            log.info("Done: %s", image_path.name)
            return result

        except requests.exceptions.Timeout:
            log.warning("Timeout after %ss (attempt %d/%d)", TIMEOUT, attempt, RETRIES)
            if attempt < RETRIES:
                time.sleep(5)
            else:
                raise

        except requests.exceptions.HTTPError as e:
            log.warning("HTTP error: %s (attempt %d/%d)", e, attempt, RETRIES)
            log.debug("Response body: %s", response.text)
            if attempt < RETRIES:
                time.sleep(5)
            else:
                raise

        except KeyError as e:
            log.error("Unexpected API response — missing key %s", e)
            log.debug("Full response: %s", response.text)
            raise

        except Exception as e:
            log.warning("Unexpected error: %s (attempt %d/%d)", e, attempt, RETRIES)
            if attempt < RETRIES:
                time.sleep(5)
            else:
                raise
