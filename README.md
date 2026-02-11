# Diagram → Markdown System

This repository contains a small system for generating **diagram-specific architectural notes** from images.

Each diagram image in `/projects` is paired with a `.md` file containing analytical text written against a fixed prompt structure.

The system is designed to be:

- deterministic  
- resumable  
- local-first  
- safe to run repeatedly  

---

## What this does

- Scans the `/projects` directory  
- Finds diagram images without a corresponding `.md` file  
- Selects the **smallest unprocessed image first**  
- Sends the image (via URL) and a fixed prompt to a vision-language model  
- Writes a standalone Markdown file next to the image  

Each `.md` file:

- refers to **one diagram only**  
- does not summarise projects  
- does not reference other drawings  
- can be rendered directly by Jekyll  

---

## What this does not do

- No project summaries  
- No cross-diagram reasoning  
- No visual description of drawings  
- No batch parallelism  
- No database  
- No background workers  

---

## Directory structure (relevant parts)

```

projects/
diagram_01.jpg
diagram_01.md
diagram_02.jpg

tools/
generate_diagram_md.py
vision_runner.py
diagram_prompt.txt

.env

````

---

## Environment configuration

All runtime configuration lives in `.env`.

### Required

```env
TOGETHER_API_KEY=your_key_here
````

### Used by the system

```env
TOGETHER_API_URL=https://api.together.ai/v1/chat/completions
TOGETHER_MODEL_ID=Qwen/Qwen3-VL-8B-Instruct
TOGETHER_TIMEOUT=120
TOGETHER_RETRIES=2

PROJECTS_DIR=projects
BASE_IMAGE_URL=https://www.kvshvl.in/projects
PROMPT_FILE=tools/diagram_prompt.txt

BATCH_SIZE=1
```

Nothing else is required.

---

## How to run

From the repository root:

```bash
python tools/generate_diagram_md.py
```

* Processes `BATCH_SIZE` images
* Writes `.md` files
* Safe to run repeatedly
* Skips images already processed

---

## Prompt control

The analytical structure is defined in:

```
tools/diagram_prompt.txt
```

Changing this file affects **future outputs only**.

---

## Why this exists

To separate:

* **diagrams** (chronological, expanding)
* **interpretation** (precise, local, non-repetitive)

This avoids project-level narration and keeps diagram thinking legible over time.

---

## Intentional limits

This system is intentionally simple.

If a feature is not clearly necessary, it is not included.

That is a design decision.

---

## Setup

Install dependencies once:

```bash
python -m pip install -r requirements.txt
```

```text
# requirements.txt
together>=0.2.0
python-dotenv>=1.0.0
requests>=2.31.0
```
