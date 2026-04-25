from __future__ import annotations

from pathlib import Path
from typing import Any, List

from src.config import PROJECT_ROOT, load_experiment_config
from src.data_generation.generator import (
    SyntheticRecordGenerator,
    export_records_to_csv,
    export_records_to_json,
)
from src.data_generation.schema import ExperimentResult
from src.detection.leakage_rules import detect_leakage
from src.detection.scoring import compute_leakage_score, leakage_detected
from src.detection.utility import compute_utility_score
from src.evaluation.aggregator import aggregate_by_strategy
from src.evaluation.export import export_rows_to_csv, export_rows_to_json
from src.evaluation.metadata import build_run_metadata
from src.llm.factory import build_backend
from src.prompting.prompt_builder import build_prompt
from src.prompting.strategies import StrategyType
from src.tasks.attack_tasks import AttackType
from src.tasks.benign_tasks import BenignTaskType
from src.utils import write_json

MAX_LLM_CALLS = 80
LOCAL_SECONDS_PER_CALL_ESTIMATE = 5


def _parse_task_types(config: dict[str, Any]) -> List[BenignTaskType]:
    """Parse configured benign task names into enum values."""
    return [BenignTaskType(value) for value in config["task_types"]]


def _parse_attack_types(config: dict[str, Any]) -> List[AttackType]:
    """Parse configured attack names into enum values."""
    return [AttackType(value) for value in config["attack_types"]]


def _parse_strategy_types(config: dict[str, Any]) -> List[StrategyType]:
    """Parse configured prompting strategy names into enum values."""
    return [StrategyType(value) for value in config["strategy_types"]]


def estimate_experiment_calls(config: dict[str, Any], max_cases: int | None = None) -> int:
    """Estimate the number of LLM calls implied by an experiment config."""
    configured_calls = (
        int(config.get("dataset_size", 25))
        * len(config["task_types"])
        * len(config["attack_types"])
        * len(config["strategy_types"])
    )
    if max_cases is None:
        return configured_calls
    return min(configured_calls, max_cases)


def estimate_runtime_minutes(num_calls: int) -> float:
    """Estimate local runtime in minutes for concise Ollama responses."""
    return round((num_calls * LOCAL_SECONDS_PER_CALL_ESTIMATE) / 60, 1)


def _validate_case_limit(config: dict[str, Any], num_calls: int) -> None:
    """Protect local runs from accidentally launching oversized experiments."""
    backend_config = dict(config.get("model_backend", {}))
    backend_type = str(backend_config.get("type", config.get("default_model_name", "mock"))).lower()
    if backend_type == "ollama" and num_calls > MAX_LLM_CALLS:
        raise ValueError("Experiment too large for local execution. Reduce config.")


def run_experiment(
    config_path: str | Path | None = None,
    max_cases: int | None = None,
) -> tuple[list[dict], list[dict], dict]:
    """Run the full adversarial privacy evaluation pipeline."""
    config = load_experiment_config(config_path)

    seed = int(config.get("random_seed", 42))
    dataset_size = int(config.get("dataset_size", 25))
    output_paths = config["output_paths"]
    run_case_limit = estimate_experiment_calls(config, max_cases=max_cases)
    _validate_case_limit(config, run_case_limit)
    if config_path:
        resolved_config_path = Path(config_path)
        if not resolved_config_path.is_absolute():
            resolved_config_path = PROJECT_ROOT / resolved_config_path
    else:
        resolved_config_path = PROJECT_ROOT / "configs" / "experiment_config.json"
    config["resolved_config_path"] = str(resolved_config_path.resolve())
    detection_config = dict(config.get("detection", {}))
    enable_semantic_matching = bool(detection_config.get("enable_semantic_matching", False))

    task_types = _parse_task_types(config)
    attack_types = _parse_attack_types(config)
    strategy_types = _parse_strategy_types(config)

    generator = SyntheticRecordGenerator(seed=seed)
    records = generator.generate_dataset(size=dataset_size)

    backend_spec = build_backend(config=config, seed=seed)
    llm = backend_spec.backend

    result_objects: List[ExperimentResult] = []
    case_counter = 1

    for record in records:
        for task_type in task_types:
            for attack_type in attack_types:
                for strategy_type in strategy_types:
                    if len(result_objects) >= run_case_limit:
                        break
                    prompt = build_prompt(
                        record=record,
                        task_type=task_type,
                        attack_type=attack_type,
                        strategy_type=strategy_type,
                    )
                    print(
                        f"[{case_counter}/{run_case_limit}] Running: "
                        f"strategy={strategy_type.value} | attack={attack_type.value} | task={task_type.value}"
                    )

                    generation_failed = False
                    error_message = ""
                    try:
                        response_text = llm.generate(
                            system_prompt=prompt["system"],
                            user_prompt=prompt["user"],
                        )
                    except TimeoutError as exc:
                        generation_failed = True
                        error_message = str(exc)
                        response_text = f"[FAILED: {error_message}]"
                        print(f"Case C-{case_counter:06d} failed: {error_message}")

                    matches = detect_leakage(
                        record=record,
                        response_text=response_text,
                        enable_semantic_matching=enable_semantic_matching,
                    )
                    leak_score = compute_leakage_score(matches)
                    leak_flag = leakage_detected(matches)
                    utility_score = compute_utility_score(task_type, response_text)

                    result = ExperimentResult(
                        case_id=f"C-{case_counter:06d}",
                        record_id=record.record_id,
                        task_type=task_type.value,
                        attack_type=attack_type.value,
                        strategy_name=strategy_type.value,
                        model_name=backend_spec.model_name,
                        prompt_text=prompt["system"] + "\n\n" + prompt["user"],
                        response_text=response_text,
                        leakage_score=leak_score,
                        utility_score=utility_score,
                        leakage_detected=leak_flag,
                        matches=matches,
                        generation_failed=generation_failed,
                        error_message=error_message,
                    )
                    result_objects.append(result)
                    case_counter += 1
                if len(result_objects) >= run_case_limit:
                    break
            if len(result_objects) >= run_case_limit:
                break
        if len(result_objects) >= run_case_limit:
            break

    result_rows = [obj.to_dict() for obj in result_objects]
    strategy_rows = aggregate_by_strategy(result_rows)

    generated_csv = PROJECT_ROOT / Path(output_paths["generated_data_csv"])
    generated_json = PROJECT_ROOT / Path(output_paths["generated_data_json"])
    runs_csv = PROJECT_ROOT / Path(output_paths["run_results_csv"])
    runs_json = PROJECT_ROOT / Path(output_paths.get("run_results_json", "results/runs/experiment_results.json"))
    strategy_csv = PROJECT_ROOT / Path(output_paths["aggregated_results_csv"])
    strategy_json = PROJECT_ROOT / Path(
        output_paths.get("aggregated_results_json", "results/tables/strategy_comparison.json")
    )
    metadata_json = PROJECT_ROOT / Path(output_paths.get("run_metadata_json", "results/runs/run_metadata.json"))

    export_records_to_csv(records, generated_csv)
    export_records_to_json(records, generated_json)
    export_rows_to_csv(result_rows, runs_csv)
    export_rows_to_json(result_rows, runs_json)
    export_rows_to_csv(strategy_rows, strategy_csv)
    export_rows_to_json(strategy_rows, strategy_json)
    metadata = build_run_metadata(
        config=config,
        project_root=PROJECT_ROOT,
        seed=seed,
        num_records=len(records),
        num_cases=len(result_rows),
        backend_type=backend_spec.backend_type,
        model_name=backend_spec.model_name,
        requested_model_name=backend_spec.requested_model_name,
        fallback_model_name=backend_spec.fallback_model_name,
    )
    write_json(metadata_json, metadata)

    return result_rows, strategy_rows, metadata
