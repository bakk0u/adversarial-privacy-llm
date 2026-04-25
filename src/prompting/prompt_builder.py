from __future__ import annotations

from typing import Dict

from src.data_generation.schema import SensitiveRecord
from src.prompting.attack_generator import build_attack_prompt
from src.prompting.strategies import STRATEGY_SPECS, StrategyType
from src.tasks.attack_tasks import AttackType
from src.tasks.benign_tasks import BENIGN_TASKS, BenignTaskType


def format_record(record: SensitiveRecord) -> str:
    """Convert a synthetic record into structured text for the LLM."""
    fields = record.to_dict()

    formatted = "\n".join(
        f"{key}: {value}" for key, value in fields.items()
    )

    return f"RECORD:\n{formatted}"


def build_prompt(
    record: SensitiveRecord,
    task_type: BenignTaskType,
    attack_type: AttackType,
    strategy_type: StrategyType,
) -> Dict[str, str]:
    """Build the system and user prompt for one experiment case."""

    strategy = STRATEGY_SPECS[strategy_type]
    task = BENIGN_TASKS[task_type]

    system_instruction = strategy.system_instruction
    task_instruction = task.instruction_template
    attack_prompt = build_attack_prompt(attack_type)

    record_block = format_record(record)

    user_prompt = (
        f"{record_block}\n\n"
        f"TASK:\n{task_instruction}\n\n"
        "Respond concisely in 2-3 sentences.\n\n"
        f"{attack_prompt}"
    )

    return {
        "system": system_instruction,
        "user": user_prompt,
    }
