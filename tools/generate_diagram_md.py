from pathlib import Path
from llava_runner import run_llava

# -------- CONFIG --------

PROJECTS_DIR = Path("projects")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

PROMPT = """
You are an architect writing analytical notes for a single architectural diagram.

Rules:
- Write only about this diagram.
- Do not mention other drawings.
- Do not summarise the project.
- Do not describe style, line weight, colour, or representation.
- Do not repeat generic boilerplate language.
- Use restrained architectural language.

Output exactly in this Markdown structure:

## Diagram role
<single line>

## Spatial focus
- <item>
- <item>
- <item>

## Diagrammatic ideas
- <idea>
- <idea>

## Reading
<3–5 sentence analytical paragraph>
"""

# -------- GENERATION --------

def generate_text_from_image(image_path: Path) -> str:
    return run_llava(str(image_path), PROMPT)

# -------- MAIN --------

def main():
    if not PROJECTS_DIR.exists():
        print("Error: /projects directory not found.")
        return

    images = [
        p for p in PROJECTS_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    if not images:
        print("No images found in /projects.")
        return

    for image in images:
        md_path = image.with_suffix(".md")

        if md_path.exists():
            continue  # do not overwrite existing files

        print(f"Generating: {md_path.name}")

        text = generate_text_from_image(image)
        md_path.write_text(text.strip() + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()