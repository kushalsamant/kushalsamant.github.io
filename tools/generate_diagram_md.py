import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from together import Together

# ---------- ENV ----------

load_dotenv()

API_KEY = os.getenv("TOGETHER_API_KEY")
print("TOGETHER_API_KEY present:", bool(API_KEY))

client = Together(api_key=API_KEY)

# ---------- PATHS ----------

PROJECTS_DIR = Path("projects")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# ---------- PROMPT ----------

PROMPT = """
You are an architect writing analytical notes for a single architectural diagram.

Rules:
- Write only about this diagram.
- Do not mention other drawings.
- Do not summarise the project.
- Do not describe style, line weight, colour, or representation.
- Avoid generic architectural language.
- Use precise, restrained architectural thinking.

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

# ---------- HELPERS ----------

def encode_image(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generate_text_from_image(image_path: Path) -> str:
    print("Calling Together API for:", image_path.name)

    image_b64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="ServiceNow-AI/Apriel-1.5-15b-Thinker",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT.strip()},
                    {
                        "type": "image",
                        "image_base64": image_b64,
                        "mime_type": "image/jpeg"
                    }
                ]
            }
        ],
        temperature=0.4,
        max_tokens=700
    )

    return response.choices[0].message.content.strip()

# ---------- MAIN ----------

def main():
    images = sorted(
        [p for p in PROJECTS_DIR.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS],
        reverse=True
    )

    for image in images:
        md_path = image.with_suffix(".md")

        if md_path.exists():
            continue  # never overwrite

        print("Generating:", md_path.name)

        text = generate_text_from_image(image)
        md_path.write_text(text + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
