import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = os.getenv("TOGETHER_API_URL")
MODEL_ID = os.getenv("TOGETHER_MODEL_ID")
TIMEOUT = int(os.getenv("TOGETHER_TIMEOUT", "120"))
RETRIES = int(os.getenv("TOGETHER_RETRIES", "2"))

HEADERS = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json",
}


def run_vision(image_url: str, prompt: str) -> str:
    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
    }

    for attempt in range(1, RETRIES + 1):
        try:
            print(f"Calling Together Vision API (attempt {attempt})")
            response = requests.post(
                TOGETHER_API_URL,
                headers=HEADERS,
                json=payload,
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            print(f"Vision call failed: {e}")
            if attempt < RETRIES:
                time.sleep(5)
            else:
                raise
