from __future__ import annotations

import logging
import time
from typing import Any

from .base import BaseAIBackend

log = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1:8b"
DEFAULT_TIMEOUT = 120.0
# Caps worst-case generation length regardless of timeout — local instruct
# models asked for open-ended JSON extraction can otherwise ramble well
# past what a single training-pack chunk needs. Bounded enough to fail
# fast on a runaway/repetitive generation instead of consuming a full
# timeout window; generous enough to let a legitimate response finish
# without truncating mid-string.
#
# History (measured on llama3.1:8b Q4_K_M, 8/33-layer CPU/GPU split, 4GB
# GTX 1650, ~5.2 tokens/sec): 1024 was tried first and reliably completed
# in ~197s — but that was measured against a single giant ~12000-char
# chunk covering most of a 24-page table, which legitimately needed more
# than 1024 tokens to describe everything in view, so it looked
# insufficient. Raising to 1536 made that specific (since-fixed) case
# marginal — 295-296s of a 300s budget, occasionally truncating anyway.
# With chunking.py's table-aware batching (~900 chars/chunk) and
# prompts.py's explicit per-chunk record caps now bounding how much a
# single call is ever asked to produce, the actual required output per
# call is far smaller than either giant-chunk measurement — so 1024 is
# restored as the default, now with real margin (~100s) instead of being
# the tight constraint it was against unbounded per-call scope.
DEFAULT_NUM_PREDICT = 1024


class OllamaBackend(BaseAIBackend):
    name = "ollama"

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_URL,
        default_model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
        num_predict: int | None = DEFAULT_NUM_PREDICT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout
        self.num_predict = num_predict

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
        options: dict[str, Any] = {"temperature": temperature}
        if self.num_predict is not None:
            options["num_predict"] = self.num_predict
        payload: dict[str, Any] = {
            "model": resolved_model,
            "prompt": prompt,
            "stream": False,
            "options": options,
        }
        if system:
            payload["system"] = system
        if schema:
            payload["format"] = schema

        prompt_chars = len(prompt) + len(system or "")
        url = f"{self.base_url}/api/generate"
        started = time.monotonic()

        def _log(level: int, status: str, **extra: Any) -> None:
            elapsed = time.monotonic() - started
            fields = {
                "model": resolved_model,
                "status": status,
                "timeout_s": self.timeout,
                "prompt_chars": prompt_chars,
                "elapsed_s": round(elapsed, 2),
            }
            fields.update(extra)
            log.log(level, "ollama generate: %s", fields)

        try:
            response = httpx.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
        except httpx.ConnectError as exc:
            _log(logging.WARNING, "connection_error")
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Is Ollama running?"
            ) from exc
        except httpx.TimeoutException as exc:
            _log(logging.WARNING, "timeout")
            raise TimeoutError(
                f"Ollama request timed out after {self.timeout}s for model '{resolved_model}'."
            ) from exc
        except httpx.HTTPStatusError as exc:
            _log(logging.WARNING, "http_error", http_status=exc.response.status_code)
            raise RuntimeError(
                f"Ollama returned HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc

        data = response.json()
        # Ollama's own timing/token metadata (nanoseconds -> seconds), safe to
        # log: no prompt or generated content, just counts and durations.
        _log(
            logging.INFO,
            "ok",
            total_duration_s=_ns_to_s(data.get("total_duration")),
            load_duration_s=_ns_to_s(data.get("load_duration")),
            prompt_eval_count=data.get("prompt_eval_count"),
            prompt_eval_duration_s=_ns_to_s(data.get("prompt_eval_duration")),
            eval_count=data.get("eval_count"),
            eval_duration_s=_ns_to_s(data.get("eval_duration")),
        )
        return data.get("response", "")


def _ns_to_s(value: Any) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    return round(value / 1_000_000_000, 3)
