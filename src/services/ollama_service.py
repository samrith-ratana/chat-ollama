import requests
import json
from typing import List, Dict, Optional, Any
import os

class OllamaService:
    """Service to interact with local Ollama instance"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    def get_models(self) -> List[str]:
        """Fetch available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []
            
    def chat(self, messages: List[Dict[str, str]], model: str) -> Optional[str]:
        """Send chat messages and get response"""
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code != 200:
                print(f"Ollama API Error ({response.status_code}): {response.text}")
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
        except requests.exceptions.ConnectionError:
            print(f"Connection Error: Ollama not reachable at {self.base_url}")
            return None
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            return None
            
    def generate_embeddings(self, text: str, model: str = "all-minilm") -> List[float]:
        """Generate embeddings for text (useful for future improvements)"""
        try:
            url = f"{self.base_url}/api/embeddings"
            payload = {
                "model": model,
                "prompt": text
            }
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("embedding", [])
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []
