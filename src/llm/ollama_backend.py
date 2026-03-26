from __future__ import annotations

import requests

from src.llm.base import LLMBackend


class OllamaBackend(LLMBackend):
    """
    Uses local Ollama server.
    """

    def __init__(self, model_name: str = "llama3:8b"):
        self.model_name = model_name
        self.url = "http://localhost:11434/api/generate"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
        }

        response = requests.post(self.url, json=payload)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")