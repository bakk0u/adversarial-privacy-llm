from __future__ import annotations

import random
import re
from typing import Dict, List

from src.llm.base import LLMBackend
from src.prompting.strategies import StrategyType


STRATEGY_LEAK_MULTIPLIERS: Dict[StrategyType, float] = {
    StrategyType.DIRECT_BASELINE: 1.0,
    StrategyType.POLICY_FIRST_STRUCTURED: 0.55,
    StrategyType.TREE_OF_THOUGHTS: 0.35,
    StrategyType.SKELETON_OF_THOUGHT: 0.45,
    StrategyType.LEAST_TO_MOST: 0.5,
}


class MockLLMBackend(LLMBackend):
    """Deterministic simulation of strategy-aware privacy leakage.

    The mock backend is not intended to model real language behavior. It exists
    to validate the experiment pipeline while preserving reproducible, controlled
    differences between prompt-defense strategies.
    """

    def __init__(self, base_leak_probability: float = 0.6, seed: int = 42) -> None:
        self.random = random.Random(seed)
        self.base_leak_probability = base_leak_probability

    def _extract_sensitive_fields(self, prompt: str) -> List[str]:
        """Extract structured identifiers that the mock may leak."""
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

    def _infer_strategy(self, system_prompt: str) -> StrategyType:
        """Infer the prompting strategy from its system instruction."""
        system_prompt = system_prompt.lower()

        if "tree" in system_prompt or "multiple possible reasoning paths" in system_prompt:
            return StrategyType.TREE_OF_THOUGHTS

        if "skeleton" in system_prompt or "high-level structure" in system_prompt:
            return StrategyType.SKELETON_OF_THOUGHT

        if "least sensitive" in system_prompt or "least" in system_prompt:
            return StrategyType.LEAST_TO_MOST

        if "minimum information necessary" in system_prompt or "policy" in system_prompt:
            return StrategyType.POLICY_FIRST_STRUCTURED

        return StrategyType.DIRECT_BASELINE

    def _leak_probability(self, system_prompt: str) -> float:
        """Return the strategy-specific leakage probability."""
        strategy = self._infer_strategy(system_prompt)
        multiplier = STRATEGY_LEAK_MULTIPLIERS[strategy]
        return max(0.0, min(1.0, self.base_leak_probability * multiplier))

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a deterministic synthetic response."""

        base_response = (
            "The record indicates moderate mobility activity with consistent usage patterns. "
            "There are no critical anomalies, but some operational monitoring may be beneficial."
        )

        leak_probability = self._leak_probability(system_prompt)

        if self.random.random() < leak_probability:
            sensitive_values = self._extract_sensitive_fields(user_prompt)
            if sensitive_values:
                leak_sample = ", ".join(sensitive_values[:2])
                return base_response + f"\n\nAdditional details: {leak_sample}"

        return base_response
