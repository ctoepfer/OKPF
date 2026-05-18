from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAIBackend(ABC):
    name: str = "base"

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: str | None = None,
        schema: dict[str, Any] | None = None,
        temperature: float = 0.1,
        model: str | None = None,
    ) -> str:
        """Send prompt to the AI backend and return the raw response string."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
