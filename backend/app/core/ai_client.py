import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL")

if not OLLAMA_URL:
    raise RuntimeError("OLLAMA_URL environment variable is not set")

def call_llm(prompt: str, model: str = "llama3") -> dict:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=120
    )
    response.raise_for_status()

    return response.json()
