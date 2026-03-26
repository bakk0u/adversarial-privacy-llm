from __future__ import annotations

from abc import ABC, abstractmethod


class LLMBackend(ABC):
    """
    Abstract interface for all LLM backends.
    """

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass