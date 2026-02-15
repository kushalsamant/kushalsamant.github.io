import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Validate required environment variables
REQUIRED_ENV_VARS = [
    "TOGETHER_API_KEY",
    "TOGETHER_API_URL",
    "TOGETHER_MODEL_ID",
]

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file.")
    sys.exit(1)

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
    """Call Together AI Vision API to analyze an architectural diagram.
    
    Args:
        image_url: Public URL to the diagram image
        prompt: Instruction prompt for the vision model
        
    Returns:
        Generated text analysis from the model
        
    Raises:
        requests.HTTPError: If API returns error status
        Exception: If all retry attempts fail
    """
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
            print(f"Calling Together Vision API (attempt {attempt}/{RETRIES})")
            response = requests.post(
                TOGETHER_API_URL,
                headers=HEADERS,
                json=payload,
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

        except requests.exceptions.Timeout:
            print(f"Request timeout after {TIMEOUT}s")
            if attempt < RETRIES:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise
                
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            if attempt < RETRIES:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise
                
        except KeyError as e:
            print(f"Unexpected API response format: missing key {e}")
            raise
            
        except Exception as e:
            print(f"Vision call failed: {e}")
            if attempt < RETRIES:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise
