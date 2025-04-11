from typing import Any, Dict
import requests

class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.gemini.com/v1"

    def query_gemini(self, prompt: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "max_tokens": 150
        }
        response = requests.post(f"{self.base_url}/query", headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_model_info(self) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        response = requests.get(f"{self.base_url}/model_info", headers=headers)
        response.raise_for_status()
        return response.json()