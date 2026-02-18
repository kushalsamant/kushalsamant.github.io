import os
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from vision_runner import run_vision

load_dotenv()

# Validate required environment variables
REQUIRED_ENV_VARS = [
    "TOGETHER_API_KEY",
    "PROMPT_FILE",
    "IMAGE_EXTENSIONS",
]

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file.")
    sys.exit(1)

DIAGRAMS_DIR = Path(os.getenv("DIAGRAMS_DIR", "diagrams"))
PROMPT_FILE = Path(os.getenv("PROMPT_FILE"))
IMAGE_EXTENSIONS = set(
    ext.strip() if ext.strip().startswith('.') else f".{ext.strip()}"
    for ext in os.getenv("IMAGE_EXTENSIONS", "").split(",")
)
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1"))

if not PROMPT_FILE.exists():
    print(f"ERROR: Prompt file not found: {PROMPT_FILE}")
    sys.exit(1)

PROMPT = PROMPT_FILE.read_text(encoding="utf-8")

OUTPUT_DIR = Path("_diagrams")
OUTPUT_DIR.mkdir(exist_ok=True)

LOG_FILE = Path("generation.log")

FRONT_MATTER = """---
layout: none
---
"""


def log(message: str, level: str = "INFO"):
    """Write to log file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}\n"

    print(message)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)


def fix_encoding(text: str) -> str:
    """Fix UTF-8 mojibake from API responses.

    These patterns occur when UTF-8 text is incorrectly decoded as Latin-1
    and then re-encoded as UTF-8.
    """
    replacements = {
        'ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢': "'",
        'ÃƒÂ¢Ã¢â€šÂ¬Ã…"': '"',
        'ÃƒÂ¢Ã¢â€šÂ¬': '"',
        'ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å"': '—',
        'ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬"': '–',
        'ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦': '…',
    }

    for wrong, right in replacements.items():
        text = text.replace(wrong, right)

    return text


def clean_output(text: str) -> str:
    """Enforce typographic cleanliness and remove unwanted formatting."""
    text = fix_encoding(text)

    lines = text.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()

        # Preserve blank lines
        if not line:
            cleaned.append("")
            continue

        # Remove all section headings (any line starting with #)
        if line.startswith("#"):
            continue

        cleaned.append(line)

    return "\n".join(cleaned).strip()


def get_unprocessed_images():
    """Find images that don't have corresponding markdown files."""
    if not DIAGRAMS_DIR.exists():
        log(f"Diagrams directory not found: {DIAGRAMS_DIR}", "ERROR")
        sys.exit(1)

    images = [
        p for p in DIAGRAMS_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
        and not (OUTPUT_DIR / p.with_suffix(".md").name).exists()
    ]

    # Process smallest files first for faster feedback
    images.sort(key=lambda p: p.stat().st_size)
    return images[:BATCH_SIZE]


def main():
    log("=" * 50)
    log("Diagram -> Markdown Generator")
    log("=" * 50)

    images = get_unprocessed_images()

    if not images:
        log("No diagrams left to process.")
        return

    log(f"Found {len(images)} unprocessed image(s)")

    success_count = 0
    fail_count = 0
    total_time = 0

    for idx, image in enumerate(images, 1):
        log(f"[{idx}/{len(images)}] Processing {image.name}")

        md_path = OUTPUT_DIR / image.with_suffix(".md").name

        start_time = time.time()

        try:
            raw_body = run_vision(image, PROMPT)
            body = clean_output(raw_body)

            md_path.write_text(
                FRONT_MATTER + "\n" + body + "\n",
                encoding="utf-8"
            )

            elapsed = time.time() - start_time
            total_time += elapsed

            log(f"OK Written {md_path.name} ({elapsed:.2f}s)")
            success_count += 1

        except Exception as e:
            elapsed = time.time() - start_time
            log(f"FAIL {image.name}: {str(e)} ({elapsed:.2f}s)", "ERROR")
            fail_count += 1

    log("=" * 50)
    log(f"Success: {success_count} | Failed: {fail_count}")
    log(f"Total time: {total_time:.2f}s | Avg: {total_time / len(images):.2f}s per image")
    log("=" * 50)

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
