from dotenv import load_dotenv
load_dotenv()

import torch
from PIL import Image
from transformers import AutoProcessor
from transformers.models.llava import LlavaForConditionalGeneration

MODEL_ID = "llava-hf/llava-1.5-7b-hf"
CACHE_DIR = "C:/Users/ADMIN/.ollama/models"

processor = AutoProcessor.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR)
model = LlavaForConditionalGeneration.from_pretrained(
    MODEL_ID,
    cache_dir=CACHE_DIR,
    torch_dtype=torch.float32
).to("cpu")

def run_llava(image_path: str, prompt: str) -> str:
    image = Image.open(image_path).convert("RGB")

    inputs = processor(
        prompt,
        image,
        return_tensors="pt"
    )

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False,
            num_beams=1
        )

    return processor.decode(output[0], skip_special_tokens=True)
