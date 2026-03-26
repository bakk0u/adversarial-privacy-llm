from __future__ import annotations

import random
import re

from src.llm.base import LLMBackend


class MockLLMBackend(LLMBackend):
    """
    Simulates an LLM with strategy-aware leakage behavior.
    """

    def __init__(self, base_leak_probability: float = 0.6, seed: int = 42):
        self.random = random.Random(seed)
        self.base_leak_probability = base_leak_probability

    def _extract_sensitive_fields(self, prompt: str):
        patterns = {
            "email": r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
            "phone": r"\+49-[0-9\-]+",
            "account_id": r"ACC-\d+",
            "vehicle_id": r"VH-\d+",
        }

        found = []
        for pattern in patterns.values():
            matches = re.findall(pattern, prompt)
            found.extend(matches)

        return found

    def _adjust_probability(self, system_prompt: str) -> float:
        """
        Reduce leakage probability for stronger strategies.
        """
        system_prompt = system_prompt.lower()

        if "privacy-aware" in system_prompt:
            return self.base_leak_probability * 0.5

        if "least" in system_prompt:
            return self.base_leak_probability * 0.6

        if "tree" in system_prompt:
            return self.base_leak_probability * 0.7

        if "skeleton" in system_prompt:
            return self.base_leak_probability * 0.65

        return self.base_leak_probability  # baseline

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        base_response = (
            "The record indicates moderate mobility activity with consistent usage patterns. "
            "There are no critical anomalies, but some operational monitoring may be beneficial."
        )

        leak_probability = self._adjust_probability(system_prompt)

        if self.random.random() < leak_probability:
            sensitive_values = self._extract_sensitive_fields(user_prompt)
            if sensitive_values:
                leak_sample = ", ".join(sensitive_values[:2])
                return base_response + f"\n\nAdditional details: {leak_sample}"

        return base_response