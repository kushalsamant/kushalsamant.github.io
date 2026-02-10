from dotenv import load_dotenv
load_dotenv()

from transformers import AutoProcessor
from transformers.models.llava import LlavaForConditionalGeneration

MODEL_ID = "llava-hf/llava-1.5-7b-hf"
CACHE_DIR = "tools/models"

print("Downloading processor...")
AutoProcessor.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR)

print("Downloading model...")
LlavaForConditionalGeneration.from_pretrained(
    MODEL_ID,
    cache_dir=CACHE_DIR,
    torch_dtype="auto"
)

print("Done.")
