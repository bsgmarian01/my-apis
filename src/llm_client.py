import requests
import json
from typing import List, Dict, Any

class LLMClient:
    def __init__(self, endpoint: str = "https://t5ds0879r1rl3m-11434.proxy.runpod.net", model: str = "qwen2.5-coder:32b-instruct-q4_K_M"):
        self.endpoint = endpoint.rstrip('/')
        self.chat_url = f"{self.endpoint}/api/chat"
        self.generate_url = f"{self.endpoint}/api/generate"
        self.model = model

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None, json_mode: bool = False) -> str:
        """
        Sends a chat request to the Ollama server.
        """
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": True,
            "options": {
                "num_ctx": 16384
            }
        }
        if json_mode:
            payload["format"] = "json"

        try:
            response = requests.post(self.chat_url, json=payload, timeout=300, stream=True)
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    full_response += chunk.get("message", {}).get("content", "")
            return full_response
        except Exception as e:
            raise RuntimeError(f"Failed to communicate with LLM endpoint: {e}")

    def generate(self, prompt: str, system_prompt: str = None, json_mode: bool = False) -> str:
        """
        Sends a raw generation request to the Ollama server.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_ctx": 16384
            }
        }
        if system_prompt:
            payload["system"] = system_prompt
        if json_mode:
            payload["format"] = "json"

        try:
            response = requests.post(self.generate_url, json=payload, timeout=300, stream=True)
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    full_response += chunk.get("response", "")
            return full_response
        except Exception as e:
            raise RuntimeError(f"Failed to generate from LLM endpoint: {e}")

