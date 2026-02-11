import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from vision_runner import run_vision

# ==============================
# SETUP
# ==============================

load_dotenv()

DIAGRAMS_DIR = Path(os.getenv("DIAGRAMS_DIR", "diagrams"))
BASE_IMAGE_URL = os.getenv("BASE_IMAGE_URL")
PROMPT_FILE = Path(os.getenv("PROMPT_FILE"))

IMAGE_EXTENSIONS = set(
    ext.strip() for ext in os.getenv("IMAGE_EXTENSIONS", "").split(",")
)

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1"))

PROMPT = PROMPT_FILE.read_text(encoding="utf-8")

OUTPUT_DIR = Path("_diagrams")
OUTPUT_DIR.mkdir(exist_ok=True)

FRONT_MATTER = """---
layout: none
---
"""

print("✓ TOGETHER_API_KEY loaded\n")

# ==============================
# HELPERS
# ==============================

def get_unprocessed_images():
    images = [
        p for p in DIAGRAMS_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
        and not (OUTPUT_DIR / p.with_suffix(".md").name).exists()
    ]
    images.sort(key=lambda p: p.stat().st_size)
    return images[:BATCH_SIZE]


# ==============================
# MAIN
# ==============================

def main():
    print("==============================")
    print(" Diagram → Markdown Generator ")
    print("==============================\n")

    images = get_unprocessed_images()

    if not images:
        print("✓ No diagrams left to process.")
        return

    for idx, image in enumerate(images, 1):
        print(f"[{idx}/{len(images)}] Processing {image.name}")

        image_url = f"{BASE_IMAGE_URL}/{image.name}"
        md_path = OUTPUT_DIR / image.with_suffix(".md").name

        try:
            body = run_vision(image_url, PROMPT)
        except Exception as e:
            print("✗ Vision inference failed.")
            print(e)
            sys.exit(1)

        md_path.write_text(
            FRONT_MATTER + "\n" + body.strip() + "\n",
            encoding="utf-8"
        )

        print(f"✓ Written {md_path.name}\n")

    print("✓ Done.")


if __name__ == "__main__":
    main()
