from __future__ import annotations

import json
from typing import Any

from .base import BaseAIBackend

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1:8b"
DEFAULT_TIMEOUT = 120.0


class OllamaBackend(BaseAIBackend):
    name = "ollama"

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_URL,
        default_model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        schema: dict[str, Any] | None = None,
        temperature: float = 0.1,
        model: str | None = None,
    ) -> str:
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx is required for OllamaBackend. Install: pip install httpx")

        resolved_model = model or self.default_model
        payload: dict[str, Any] = {
            "model": resolved_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system
        if schema:
            payload["format"] = schema

        url = f"{self.base_url}/api/generate"
        try:
            response = httpx.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
        except httpx.ConnectError as exc:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Is Ollama running?"
            ) from exc
        except httpx.TimeoutException as exc:
            raise TimeoutError(
                f"Ollama request timed out after {self.timeout}s for model '{resolved_model}'."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Ollama returned HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc

        data = response.json()
        return data.get("response", "")
