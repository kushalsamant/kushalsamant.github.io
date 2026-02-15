import os
import sys
import time
import base64
from pathlib import Path
import requests
from dotenv import load_dotenv

print("Loading environment variables...")
load_dotenv()

print("Validating required environment variables...")

REQUIRED_ENV_VARS = [
    "TOGETHER_API_KEY",
    "TOGETHER_API_URL",
    "TOGETHER_MODEL_ID",
]

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing_vars:
    print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file.")
    sys.exit(1)

print("Environment variables validated successfully.")

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = os.getenv("TOGETHER_API_URL")
MODEL_ID = os.getenv("TOGETHER_MODEL_ID")

TIMEOUT = int(os.getenv("TOGETHER_TIMEOUT", "120"))
RETRIES = int(os.getenv("TOGETHER_RETRIES", "2"))

print(f"Using Together endpoint: {TOGETHER_API_URL}")
print(f"Using model: {MODEL_ID}")
print(f"Timeout: {TIMEOUT}s | Retries: {RETRIES}")

HEADERS = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json",
}


def encode_image_to_base64(image_path: Path) -> tuple[str, str]:
    print(f"Encoding image to base64: {image_path}")

    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    suffix = image_path.suffix.lower()
    print(f"Detected file extension: {suffix}")

    if suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".png":
        mime = "image/png"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/jpeg"

    print(f"Using MIME type: {mime}")

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    print(f"Encoding complete. Encoded length: {len(encoded)} characters")

    return mime, encoded


def run_vision(image_path: Path, prompt: str) -> str:
    print("=" * 60)
    print(f"Starting vision analysis for: {image_path}")
    print("=" * 60)

    mime_type, encoded_image = encode_image_to_base64(Path(image_path))

    print("Constructing payload for Together API...")

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

    print("Payload constructed successfully.")
    print(f"Payload size (approx): {len(str(payload))} characters")

    for attempt in range(1, RETRIES + 1):
        try:
            print(f"\nCalling Together Vision API (attempt {attempt}/{RETRIES})")

            response = requests.post(
                TOGETHER_API_URL,
                headers=HEADERS,
                json=payload,
                timeout=TIMEOUT,
            )

            print(f"HTTP status code received: {response.status_code}")

            response.raise_for_status()

            print("Parsing JSON response...")
            data = response.json()

            print("Response parsed successfully.")
            print("Extracting model output...")

            result = data["choices"][0]["message"]["content"].strip()

            print("Vision analysis completed successfully.")
            print("=" * 60)

            return result

        except requests.exceptions.Timeout:
            print(f"ERROR: Request timeout after {TIMEOUT}s")

            if attempt < RETRIES:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("All retries exhausted due to timeout.")
                raise

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            print(f"Response body: {response.text}")

            if attempt < RETRIES:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("All retries exhausted due to HTTP error.")
                raise

        except KeyError as e:
            print(f"Unexpected API response format: missing key {e}")
            print(f"Full response: {response.text}")
            raise

        except Exception as e:
            print(f"Unexpected error during vision call: {e}")

            if attempt < RETRIES:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("All retries exhausted due to unexpected error.")
                raise
