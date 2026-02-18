# Diagram → Markdown System

This repository contains a small system for generating **diagram-specific architectural notes** from images.

Each image in `/diagrams` is paired with a `.md` file in `/_diagrams` containing analytical text written against a fixed prompt structure.

The system is designed to be:

- deterministic  
- resumable  
- local-first  
- safe to run repeatedly  

## What this does

- Scans the `/diagrams` directory  
- Finds images without a corresponding `.md` file in `/_diagrams`  
- Selects the **smallest unprocessed image first**  
- Encodes the image as base64 and sends it with a fixed prompt to a vision-language model  
- Writes a standalone Markdown file to `/_diagrams`  

Each `.md` file:

- refers to **one diagram only**  
- does not summarise projects  
- does not reference other drawings  
- can be rendered directly by Jekyll  

## What this does not do

- No project summaries  
- No cross-diagram reasoning  
- No visual description of drawings  
- No batch parallelism  
- No database  
- No background workers  

## Directory structure (relevant parts)

```
diagrams/
  2023_STW__DIAGRAM_PLAN_A.jpg
  2024_YRTH__DIAGRAM_SECTION_A.jpg
  2025_PJCH__DIAGRAM_PLAN_A.jpg

_diagrams/
  2023_STW__DIAGRAM_PLAN_A.md
  2024_YRTH__DIAGRAM_SECTION_A.md
  2025_PJCH__DIAGRAM_PLAN_A.md

tools/
  generate_markdown.py
  vision_runner.py
  diagram_prompt.txt

.env
env.example
```

## Naming Convention

All diagrams must follow this pattern:
```
YYYY_PROJECT-SLUG__TYPE_DESCRIPTOR.ext
```

**Components:**
- `YYYY` — Year (4 digits)
- `PROJECT-SLUG` — Short project code (e.g., STW, YRTH, PJCH)
- `TYPE` — Content type (DIAGRAM, RENDER, PHOTO, etc.)
- `DESCRIPTOR` — Specific view or detail (PLAN_A, SECTION_AXON, etc.)
- `ext` — File extension (.jpg, .jpeg, .png for images; .md for markdown)

**Examples:**
- `2023_STW__DIAGRAM_PLAN_A.jpg`
- `2024_YRTH__DIAGRAM_SECTION_AXON.jpg`
- `2025_PJCH__DIAGRAM_CROSS_AXON.jpg`

## Environment configuration

All runtime configuration lives in `.env`.

Copy `env.example` to `.env` and configure:

### Required

```env
TOGETHER_API_KEY=your_key_here
TOGETHER_API_URL=https://api.together.ai/v1/chat/completions
TOGETHER_MODEL_ID=Qwen/Qwen3-VL-8B-Instruct
PROMPT_FILE=tools/diagram_prompt.txt
IMAGE_EXTENSIONS=.jpg,.jpeg,.png
```

### Optional (with defaults)

```env
TOGETHER_TIMEOUT=120
TOGETHER_RETRIES=2
DIAGRAMS_DIR=diagrams
BATCH_SIZE=1
DEBUG=false
```

## Setup

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Create `.env` from template:

```bash
cp env.example .env
```

3. Edit `.env` and add your `TOGETHER_API_KEY`

## How to run

From the repository root:

```bash
python tools/generate_markdown.py
```

- Processes `BATCH_SIZE` images per run  
- Writes `.md` files to `_diagrams/`  
- Safe to run repeatedly — skips already-processed images  

## Prompt control

The analytical structure is defined in:

```
tools/diagram_prompt.txt
```

Changing this file affects **future outputs only**.

## Why this exists

To separate:

- **diagrams** (chronological, expanding)
- **interpretation** (precise, local, non-repetitive)

This avoids project-level narration and keeps diagram thinking legible over time.

## Intentional limits

This system is intentionally simple.

If a feature is not clearly necessary, it is not included.

That is a design decision.
