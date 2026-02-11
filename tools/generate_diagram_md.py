import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from vision_runner import run_vision

# ==============================
# SETUP
# ==============================

load_dotenv()

PROJECTS_DIR = Path(os.getenv("PROJECTS_DIR", "projects"))
BASE_IMAGE_URL = os.getenv("BASE_IMAGE_URL", "https://www.kvshvl.in/projects")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

PROMPT_FILE = Path(os.getenv("PROMPT_FILE", "tools/diagram_prompt.txt"))
PROMPT = PROMPT_FILE.read_text(encoding="utf-8")

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1"))

FRONT_MATTER = """---
layout: none
---
"""

print("✔ TOGETHER_API_KEY loaded")
print(f"✔ Batch size: {BATCH_SIZE}\n")

# ==============================
# HELPERS
# ==============================

def get_pending_images():
    images = [
        p for p in PROJECTS_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
        and not Path("_projects", p.with_suffix(".md").name).exists()
    ]
    images.sort(key=lambda p: p.stat().st_size)
    return images


# ==============================
# MAIN
# ==============================

def main():
    print("==============================")
    print(" Diagram → Markdown Generator ")
    print("==============================\n")

    print(" Scanning /projects directory...\n")

    images = get_pending_images()

    if not images:
        print(" No images left to process.")
        return

    diagrams_dir = Path("_projects")
    diagrams_dir.mkdir(exist_ok=True)

    to_process = images[:BATCH_SIZE]

    print(f" Processing {len(to_process)} image(s)\n")

    for index, image in enumerate(to_process, start=1):
        print("--------------------------------")
        print(f" [{index}/{len(to_process)}] {image.name}")

        md_path = diagrams_dir / image.with_suffix(".md").name
        image_url = f"{BASE_IMAGE_URL}/{image.name}"

        print(f" Image size: {image.stat().st_size // 1024} KB")
        print(f" Image URL: {image_url}")
        print(" Calling Together Vision API...")

        try:
            body = run_vision(image_url, PROMPT)
        except Exception as e:
            print(" Vision inference failed.")
            print(e)
            sys.exit(1)

        md_path.write_text(
            FRONT_MATTER + "\n" + body.strip() + "\n",
            encoding="utf-8"
        )

        print(f" Markdown written: {md_path.name}\n")

    print(" Batch complete.")
    print(" Run again to continue.\n")


if __name__ == "__main__":
    main()
