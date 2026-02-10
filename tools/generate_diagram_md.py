from pathlib import Path
from together_runner import image_to_markdown

PROJECTS_DIR = Path("projects")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

def main():
    images = [
        p for p in PROJECTS_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    for image in images:
        md_path = image.with_suffix(".md")

        if md_path.exists():
            continue  # never overwrite

        print(f"Generating: {md_path.name}")

        text = image_to_markdown(image)
        md_path.write_text(text + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
