import os
import sys
import re
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
# FORMATTING HELPERS
# ==============================

def format_markdown(text):
    """
    Post-process markdown to ensure world-class formatting.
    """
    lines = text.split('\n')
    formatted_lines = []
    in_reading_section = False
    
    for i, line in enumerate(lines):
        # Track if we're in the Reading section
        if line.strip() == "## Reading":
            in_reading_section = True
            formatted_lines.append(line)
            continue
        elif line.strip().startswith("## ") and in_reading_section:
            in_reading_section = False
        
        # Skip empty lines
        if not line.strip():
            formatted_lines.append(line)
            continue
        
        # Handle headers (leave as-is)
        if line.strip().startswith("##"):
            formatted_lines.append(line)
            continue
        
        # Handle bullet points
        if line.strip().startswith("-"):
            # Clean up bullet point
            content = line.strip()[1:].strip()
            
            # Ensure sentence case (first letter capitalized)
            if content and content[0].islower():
                content = content[0].upper() + content[1:]
            
            # Ensure ends with period
            if content and not content.endswith(('.', '!', '?')):
                content += '.'
            
            # Fix double periods
            content = re.sub(r'\.+$', '.', content)
            
            formatted_lines.append(f"- {content}")
            continue
        
        # Handle "Diagram role" content (single line, no period)
        if i > 0 and lines[i-1].strip() == "## Diagram role":
            content = line.strip()
            # Ensure sentence case
            if content and content[0].islower():
                content = content[0].upper() + content[1:]
            # Remove trailing period if present
            content = content.rstrip('.')
            formatted_lines.append(content)
            continue
        
        # Handle Reading section (ensure proper paragraph formatting)
        if in_reading_section and line.strip() and not line.strip().startswith("##"):
            content = line.strip()
            
            # Ensure sentence case
            if content and content[0].islower():
                content = content[0].upper() + content[1:]
            
            # Ensure ends with period
            if content and not content.endswith(('.', '!', '?')):
                content += '.'
            
            formatted_lines.append(content)
            continue
        
        # Default: keep line as-is
        formatted_lines.append(line)
    
    # Join lines and clean up excessive whitespace
    result = '\n'.join(formatted_lines)
    
    # Ensure consistent spacing around headers (blank line before and after)
    result = re.sub(r'\n(## [^\n]+)\n', r'\n\n\1\n\n', result)
    
    # Clean up multiple consecutive blank lines
    result = re.sub(r'\n\n\n+', '\n\n', result)
    
    # Ensure blank line before bullet lists
    result = re.sub(r'\n(- [^\n]+)', r'\n\n\1', result)
    
    # Clean up spacing at start and end
    result = result.strip()
    
    return result


def validate_markdown(text):
    """
    Validate the markdown structure and content quality.
    Returns (is_valid, error_message).
    """
    # Check for required sections
    required_sections = ["## Diagram role", "## Spatial focus", "## Diagrammatic ideas", "## Reading"]
    for section in required_sections:
        if section not in text:
            return False, f"Missing required section: {section}"
    
    # Check for bullet points in Spatial focus
    spatial_section = re.search(r'## Spatial focus\n\n((?:- .+\n?)+)', text)
    if not spatial_section:
        return False, "Spatial focus section missing bullet points"
    
    spatial_items = spatial_section.group(1).strip().split('\n')
    if len(spatial_items) < 2:
        return False, f"Spatial focus should have at least 2 items, found {len(spatial_items)}"
    
    # Check for bullet points in Diagrammatic ideas
    ideas_section = re.search(r'## Diagrammatic ideas\n\n((?:- .+\n?)+)', text)
    if not ideas_section:
        return False, "Diagrammatic ideas section missing bullet points"
    
    # Check Reading section has substantial content
    reading_section = re.search(r'## Reading\n\n(.+)', text, re.DOTALL)
    if not reading_section:
        return False, "Reading section is empty"
    
    reading_content = reading_section.group(1).strip()
    if len(reading_content) < 100:  # Arbitrary minimum length
        return False, "Reading section is too short (should be 3-5 sentences)"
    
    return True, ""


# ==============================
# MAIN HELPERS
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
            # Get raw output from vision model
            body = run_vision(image_url, PROMPT)
            
            # Format the markdown
            formatted_body = format_markdown(body.strip())
            
            # Validate the output
            is_valid, error_msg = validate_markdown(formatted_body)
            if not is_valid:
                print(f"⚠ Warning: {error_msg}")
                print("  Proceeding anyway, but output may need manual review.")
            
            # Write to file with front matter
            final_content = FRONT_MATTER + "\n" + formatted_body + "\n"
            md_path.write_text(final_content, encoding="utf-8")
            
            print(f"✓ Written {md_path.name}")
            
            # Show preview of first few lines
            preview_lines = formatted_body.split('\n')[:8]
            print("  Preview:")
            for line in preview_lines:
                if line.strip():
                    print(f"    {line}")
            print()

        except Exception as e:
            print("✗ Vision inference failed.")
            print(e)
            sys.exit(1)

    print("✓ Done.")


if __name__ == "__main__":
    main()
