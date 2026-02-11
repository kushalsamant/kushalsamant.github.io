import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from vision_runner import run_vision

load_dotenv()

PROJECTS_DIR = Path(os.getenv("PROJECTS_DIR", "projects"))
BASE_IMAGE_URL = os.getenv("BASE_IMAGE_URL")
PROMPT_FILE = os.getenv("PROMPT_FILE")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1"))

if not BASE_IMAGE_URL:
    raise RuntimeError("BASE_IMAGE_URL not set in .env")

if not PROMPT_FILE:
    raise RuntimeError("PROMPT_FILE not set in .env")

PROMPT = Path(PROMPT_FILE).read_text(encoding="utf-8")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def get_unprocessed_images(limit: int):
    images = [
        p for p in PROJECTS_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
        and not p.with_suffix(".md").exists()
    ]
    images.sort(key=lambda p: p.stat().st_size)
    return images[:limit]

def main():
    print("Diagram → Markdown Generator")
    print(f"Batch size: {BATCH_SIZE}\n")

    images = get_unprocessed_images(BATCH_SIZE)

    if not images:
        print("No images left to process.")
        return

    for idx, image in enumerate(images, start=1):
        md_path = image.with_suffix(".md")
        image_url = f"{BASE_IMAGE_URL}/{image.name}"

        print(f"[{idx}/{len(images)}] Processing: {image.name}")
        print(f"Image URL: {image_url}")

        try:
            text = run_vision(image_url, PROMPT)
        except Exception as e:
            print("Vision inference failed")
            print(e)
            sys.exit(1)

        md_path.write_text(text + "\n", encoding="utf-8")
        print(f"Generated: {md_path.name}\n")

    print("Batch complete.")

if __name__ == "__main__":
    main()
