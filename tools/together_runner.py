import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from together import Together

# Load environment variables from .env (local) or system (prod)
load_dotenv()

# Debug: confirm key presence (safe – does not print the key)
print("TOGETHER_API_KEY present:", bool(os.getenv("TOGETHER_API_KEY")))

client = Together()

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

def image_to_markdown(image_path: Path) -> str:
    # 🔍 DEBUG: confirm per-image API call
    print("Calling Together API for:", image_path.name)

    image_bytes = image_path.read_bytes()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-VL-7B-Instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    }
                ]
            }
        ],
        temperature=0.2,
        max_tokens=400,
    )

    return response.choices[0].message.content.strip()
