from __future__ import annotations

from src.tasks.attack_tasks import ATTACK_SPECS, AttackType


def build_attack_prompt(attack_type: AttackType) -> str:
    """Return the adversarial injection string for an attack type."""
    attack_spec = ATTACK_SPECS[attack_type]
    return attack_spec.prompt_template
