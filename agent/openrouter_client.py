import os

import httpx

from config import OPENROUTER_API_URL, REQUEST_TIMEOUT


class OpenRouterClient:
    def __init__(self, model):
        self.model = model
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set in environment variables")

    def complete(self, messages, tools=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools

        response = httpx.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        return response.json()["choices"][0]["message"]
