from __future__ import annotations

from abc import ABC, abstractmethod


class LLMBackend(ABC):
    """Abstract interface for all LLM backends."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a model response for a system and user prompt.

        Args:
            system_prompt: Instruction that defines model behavior.
            user_prompt: Experiment prompt containing the record, task, and attack.

        Returns:
            Model response text.
        """
        pass
