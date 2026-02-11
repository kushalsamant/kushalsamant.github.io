import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TOGETHER_API_KEY")
API_URL = os.getenv("TOGETHER_API_URL")
MODEL_ID = os.getenv("TOGETHER_MODEL_ID")
TIMEOUT = int(os.getenv("TOGETHER_TIMEOUT", "120"))
RETRIES = int(os.getenv("TOGETHER_RETRIES", "2"))

assert API_KEY, "TOGETHER_API_KEY not set"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def run_vision(image_url: str, prompt: str) -> str:
    payload = {
        "model": MODEL_ID,
        "prompt": prompt,
        "image_url": image_url,
        "max_tokens": 600,
        "temperature": 0.3,
    }

    for attempt in range(1, RETRIES + 1):
        try:
            print(f"Calling Together Vision API (attempt {attempt})")

            response = requests.post(
                API_URL,
                headers=HEADERS,
                json=payload,
                timeout=TIMEOUT,
            )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["text"].strip()

        except Exception as e:
            if attempt >= RETRIES:
                raise
            time.sleep(5)
