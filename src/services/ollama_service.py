import logging
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class OllamaService:
    """Service to interact with local Ollama instance"""
    
    def __init__(self, base_url: str, request_timeout: int = 120):
        self.base_url = base_url.rstrip('/')
        self.request_timeout = request_timeout
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a shared HTTP session with retry/backoff."""
        session = requests.Session()
        retry = Retry(
            total=2,
            connect=2,
            read=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET", "POST"]),
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
        
    def get_models(self) -> List[str]:
        """Fetch available models from Ollama"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except Exception as e:
            logger.warning("Error fetching models from Ollama: %s", e)
            return []

    def health_check(self) -> bool:
        """Check whether Ollama is reachable and responding."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def _sanitize_options(self, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate generation options before sending to Ollama."""
        if not isinstance(options, dict):
            return {}

        sanitized: Dict[str, Any] = {}

        def _coerce_float(key: str, lower: float, upper: float):
            value = options.get(key)
            if isinstance(value, (int, float)):
                sanitized[key] = max(lower, min(upper, float(value)))

        def _coerce_int(key: str, lower: int, upper: int):
            value = options.get(key)
            if isinstance(value, int):
                sanitized[key] = max(lower, min(upper, value))

        _coerce_float("temperature", 0.0, 2.0)
        _coerce_float("top_p", 0.0, 1.0)
        _coerce_int("top_k", 1, 200)
        _coerce_int("num_predict", 16, 2048)
        _coerce_float("repeat_penalty", 0.5, 2.0)

        return sanitized
            
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Send chat messages and get response"""
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            safe_options = self._sanitize_options(options)
            if safe_options:
                payload["options"] = safe_options

            response = self.session.post(url, json=payload, timeout=self.request_timeout)
            if response.status_code != 200:
                logger.error("Ollama API error (%s): %s", response.status_code, response.text)
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "").strip()
        except requests.exceptions.ConnectionError:
            logger.error("Connection error: Ollama not reachable at %s", self.base_url)
            return None
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out for model '%s'", model)
            return None
        except Exception as e:
            logger.exception("Error calling Ollama API: %s", e)
            return None
            
    def generate_embeddings(self, text: str, model: str = "all-minilm") -> List[float]:
        """Generate embeddings for text (useful for future improvements)"""
        try:
            url = f"{self.base_url}/api/embeddings"
            payload = {
                "model": model,
                "prompt": text
            }
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("embedding", [])
        except Exception as e:
            logger.warning("Error generating embeddings: %s", e)
            return []
