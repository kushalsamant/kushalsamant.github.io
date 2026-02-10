import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from together import Together

# -------------------------------------------------
# ENV
# -------------------------------------------------

load_dotenv()
API_KEY = os.getenv("TOGETHER_API_KEY")

if not API_KEY:
    print("ERROR: TOGETHER_API_KEY not found")
    sys.exit(1)

print("✔ TOGETHER_API_KEY loaded")

client = Together(api_key=API_KEY)

# -------------------------------------------------
# PATHS
# -------------------------------------------------

PROJECTS_DIR = Path("projects")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

SITE_BASE_URL = "https://www.kvshvl.in"  # required for URL-based images

# -------------------------------------------------
# PROMPT (LOCKED)
# -------------------------------------------------

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

# -------------------------------------------------
# IMAGE SELECTION LOGIC
# -------------------------------------------------

def find_next_image():
    print("\n🔍 Scanning /projects directory...")

    candidates = []

    for img in PROJECTS_DIR.iterdir():
        if img.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        md = img.with_suffix(".md")
        if md.exists():
            continue  # already processed

        size_kb = img.stat().st_size / 1024
        candidates.append((size_kb, img))

    if not candidates:
        return None

    # smallest image first (4G-friendly)
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]

# -------------------------------------------------
# API CALL
# -------------------------------------------------

def generate_md(image_path: Path):
    image_url = f"{SITE_BASE_URL}/projects/{image_path.name}"

    print("\n📷 Selected image:", image_path.name)
    print(f"📦 Image size: {image_path.stat().st_size // 1024} KB")
    print("🌐 Image URL:", image_url)
    print("🚀 Calling Together API...")

    response = client.chat.completions.create(
        model="ServiceNow-AI/Apriel-1.5-15b-Thinker",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT.strip()},
                    {
                        "type": "image",
                        "image_url": image_url
                    }
                ]
            }
        ],
        temperature=0.4,
        max_tokens=700
    )

    print("✅ API response received")

    return response.choices[0].message.content.strip()

# -------------------------------------------------
# MAIN (ONE IMAGE ONLY)
# -------------------------------------------------

def main():
    print("\n==============================")
    print(" Diagram → Markdown Generator ")
    print("==============================")

    image = find_next_image()

    if not image:
        print("\n🎉 All images already processed.")
        return

    md_path = image.with_suffix(".md")

    try:
        text = generate_md(image)
    except Exception as e:
        print("\n❌ API call failed:")
        print(e)
        return

    md_path.write_text(text + "\n", encoding="utf-8")

    print(f"\n📝 Markdown written: {md_path.name}")
    print("⏭ Run again to process the next image.")

# -------------------------------------------------

if __name__ == "__main__":
    main()
