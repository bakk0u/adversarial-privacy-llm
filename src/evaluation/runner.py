from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import List

from src.config import PROJECT_ROOT, load_experiment_config
from src.data_generation.generator import SyntheticRecordGenerator
from src.data_generation.schema import ExperimentResult
from src.detection.leakage_rules import detect_leakage
from src.detection.scoring import compute_leakage_score, leakage_detected
from src.detection.utility import compute_utility_score
from src.evaluation.aggregator import aggregate_by_strategy
from src.evaluation.export import export_rows_to_csv, export_rows_to_json
from src.llm.mock_backend import MockLLMBackend
from src.prompting.prompt_builder import build_prompt
from src.prompting.strategies import StrategyType
from src.tasks.attack_tasks import AttackType
from src.tasks.benign_tasks import BenignTaskType


def _parse_task_types(config: dict) -> List[BenignTaskType]:
    return [BenignTaskType(value) for value in config["task_types"]]


def _parse_attack_types(config: dict) -> List[AttackType]:
    return [AttackType(value) for value in config["attack_types"]]


def _parse_strategy_types(config: dict) -> List[StrategyType]:
    return [StrategyType(value) for value in config["strategy_types"]]


def run_experiment() -> tuple[list[dict], list[dict]]:
    config = load_experiment_config()

    seed = int(config.get("random_seed", 42))
    dataset_size = int(config.get("dataset_size", 25))
    model_name = str(config.get("default_model_name", "mock"))
    output_paths = config["output_paths"]

    task_types = _parse_task_types(config)
    attack_types = _parse_attack_types(config)
    strategy_types = _parse_strategy_types(config)

    generator = SyntheticRecordGenerator(seed=seed)
    records = generator.generate_dataset(size=dataset_size)

    # deterministic mock backend for reproducibility
    llm = MockLLMBackend(base_leak_probability=0.6, seed=seed)

    result_objects: List[ExperimentResult] = []
    case_counter = 1

    for record in records:
        for task_type in task_types:
            for attack_type in attack_types:
                for strategy_type in strategy_types:
                    prompt = build_prompt(
                        record=record,
                        task_type=task_type,
                        attack_type=attack_type,
                        strategy_type=strategy_type,
                    )

                    response_text = llm.generate(
                        system_prompt=prompt["system"],
                        user_prompt=prompt["user"],
                    )

                    matches = detect_leakage(record, response_text)
                    leak_score = compute_leakage_score(matches)
                    leak_flag = leakage_detected(matches)
                    utility_score = compute_utility_score(task_type, response_text)

                    result = ExperimentResult(
                        case_id=f"C-{case_counter:06d}",
                        record_id=record.record_id,
                        task_type=task_type.value,
                        attack_type=attack_type.value,
                        strategy_name=strategy_type.value,
                        model_name=model_name,
                        prompt_text=prompt["system"] + "\n\n" + prompt["user"],
                        response_text=response_text,
                        leakage_score=leak_score,
                        utility_score=utility_score,
                        leakage_detected=leak_flag,
                        matches=matches,
                    )
                    result_objects.append(result)
                    case_counter += 1

    result_rows = [obj.to_dict() for obj in result_objects]
    strategy_rows = aggregate_by_strategy(result_rows)

    runs_csv = PROJECT_ROOT / Path(output_paths["run_results_csv"])
    runs_json = PROJECT_ROOT / Path("results/runs/experiment_results.json")
    strategy_csv = PROJECT_ROOT / Path(output_paths["aggregated_results_csv"])
    strategy_json = PROJECT_ROOT / Path("results/tables/strategy_comparison.json")

    export_rows_to_csv(result_rows, runs_csv)
    export_rows_to_json(result_rows, runs_json)
    export_rows_to_csv(strategy_rows, strategy_csv)
    export_rows_to_json(strategy_rows, strategy_json)

    return result_rows, strategy_rows