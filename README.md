# Adversarial Privacy Attacks on LLMs

Experimental framework for evaluating privacy leakage in Large Language Models under adversarial prompting, and comparing prompt-engineering defenses through a privacy-utility lens.

## Research Question

How robust are different prompt-engineering strategies against adversarial attempts to extract sensitive information from structured data?

## What This Repository Does

The project runs controlled experiments over synthetic sensitive records. Each record is passed through a benign task, augmented with an adversarial instruction, wrapped in a defensive prompting strategy, and evaluated for leakage and utility.

All data is synthetic. The default backend is a deterministic mock LLM used for reproducible pipeline validation. Ollama is supported through config for local-model experiments.

## Architecture

```text
configs/
  experiment_config.json      Experiment matrix and backend settings
  ollama_experiment_config.json Smaller real-LLM validation run
  ollama_light_config.json    Laptop-friendly Ollama validation run
  field_weights.json          Leakage severity weights

src/
  data_generation/            Synthetic record schema and generator
  tasks/                      Benign task and attack definitions
  prompting/                  Prompt builder and defense strategies
  llm/                        Backend interface, mock backend, Ollama backend
  detection/                  Exact, partial, and optional semantic leakage rules
  evaluation/                 Runner, aggregation, export, run metadata
  visualization/              Reproducible plot generation
  main.py                     CLI entry point

results/
  runs/                       Case-level outputs and run metadata
  tables/                     Aggregated strategy comparison
  plots/                      Leakage and utility visualizations
  reports/                    Generated findings report
```

## Experimental Pipeline

```text
Synthetic records
  -> benign task prompt
  -> adversarial attack injection
  -> defensive prompting strategy
  -> LLM backend
  -> leakage detection
  -> leakage and utility scoring
  -> aggregation, plots, report
```

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

Run tests:

```bash
pytest
```

## Backend Configuration

The default backend is configured in `configs/experiment_config.json`:

```json
"model_backend": {
  "type": "mock",
  "model_name": "mock",
  "base_leak_probability": 0.6,
  "ollama_url": "http://localhost:11434/api/generate"
}
```

To use Ollama:

```json
"model_backend": {
  "type": "ollama",
  "model_name": "llama3:8b",
  "ollama_url": "http://localhost:11434/api/generate"
}
```

Then start Ollama locally and run:

```bash
python -m src.main --config configs/ollama_light_config.json
```

Estimate a run before executing it:

```bash
python -m src.main --config configs/ollama_light_config.json --estimate
```

Run only the first N cases:

```bash
python -m src.main --config configs/ollama_light_config.json --max_cases 20
```

## Running on a Laptop

Full real-LLM experiments are expensive on a local 8B model. The full matrix is `25 * 3 * 4 * 5 = 1500` LLM calls, which is too heavy for routine laptop validation.

## Tiny Ollama Validation

For the smallest real-model validation, use `configs/ollama_tiny_config.json`. It runs only `2 * 1 * 1 * 3 = 6` LLM calls with a shorter context, lower token budget, and a `90` second per-call timeout.

```bash
python -m src.main --config configs/ollama_tiny_config.json
```

Use `configs/ollama_light_config.json` for local Ollama runs. It limits the matrix to:

- records: `5`
- tasks: `summarization`, `anomaly_detection`
- attacks: `direct_extraction`, `instruction_override`
- strategies: `direct_baseline`, `policy_first_structured`, `tree_of_thoughts`
- total cases: `60`

The runner enforces a hard local safety cap of `80` LLM calls. Oversized runs fail before contacting the backend with: `Experiment too large for local execution. Reduce config.`

The light Ollama config uses `num_predict: 60`, `temperature: 0.1`, concise response instructions, and a `30` second per-call timeout. A typical laptop validation run should take a few minutes, not hours. Timed-out calls are recorded as failed cases and the experiment continues.

## Real LLM Validation with Ollama

Mock runs validate the pipeline under controlled, reproducible conditions. Ollama runs validate behavior on a real local LLM and should be interpreted as empirical local-model evidence.

Install Ollama, then pull the preferred thesis model and fallback model:

```bash
ollama pull llama3.1:8b
ollama pull deepseek-r1:8b
```

Run the smaller real-LLM experiment:

```bash
python -m src.main --config configs/ollama_light_config.json
```

The Ollama config uses:

- model: `llama3.1:8b`
- fallback model: `deepseek-r1:8b`
- records: `5`
- total cases: `60`
- temperature: `0.1`
- context window: `2048`
- max generated tokens: `60`
- timeout per call: `30` seconds

If `llama3.1:8b` is not installed but `deepseek-r1:8b` is available, the runner falls back and records the actual model in every result row and metadata file. If neither model is available, the run stops with a clear error.

Ollama outputs are separated from mock outputs:

```text
results/ollama_light_runs/experiment_results.csv
results/ollama_light_runs/experiment_results.json
results/ollama_light_runs/strategy_comparison.csv
results/ollama_light_runs/strategy_comparison.json
results/ollama_light_runs/run_metadata.json
results/ollama_light_runs/findings.md
results/ollama_light_runs/example_cases.md
results/ollama_light_runs/plots/
```

Interpretation template:

```text
In this local Ollama validation, <strategy> had the lowest leakage rate and <strategy> had the highest leakage rate. Utility scores were <stable/variable> across strategies. Because this is a small local-model experiment, the result should be treated as evidence for this model and configuration, not as a universal claim about all LLMs.
```

## Current Experiment Matrix

- Records: `25`
- Tasks: `summarization`, `anomaly_detection`, `recommendation`
- Attacks: `direct_extraction`, `instruction_override`, `memory_probing`, `disguised_extraction`
- Strategies: `direct_baseline`, `policy_first_structured`, `tree_of_thoughts`, `skeleton_of_thought`, `least_to_most`
- Total cases: `1500`

## Experimental Results

Mock experiments validate the methodology under controlled, reproducible conditions, while Ollama experiments validate real-world feasibility on a local LLM. The two result types answer different questions and should be interpreted separately.

### A. Simulated Results (Mock Backend)

The mock backend supports large-scale controlled evaluation of the full experimental matrix. These results validate the pipeline, scoring, aggregation, and privacy-utility analysis, but they should not be treated as claims about a specific deployed LLM.

| Strategy | Cases | Leaks | Leakage Rate | Avg Leakage Score | Avg Utility Score |
|---|---:|---:|---:|---:|---:|
| direct_baseline | 300 | 158 | 0.5267 | 1.3167 | 0.8333 |
| least_to_most | 300 | 93 | 0.3100 | 0.7750 | 0.8333 |
| policy_first_structured | 300 | 108 | 0.3600 | 0.9000 | 0.8333 |
| skeleton_of_thought | 300 | 83 | 0.2767 | 0.6917 | 0.8333 |
| tree_of_thoughts | 300 | 49 | 0.1633 | 0.4083 | 0.8333 |

In the simulated results, `tree_of_thoughts` has the lowest leakage rate and `direct_baseline` has the highest leakage rate.

### B. Real LLM Validation (Ollama)

The tiny Ollama run validates that the same experiment pipeline can execute against a real local model. It uses `llama3.1:8b` via Ollama with 2 synthetic records and 6 total cases.

| Strategy | Cases | Leaks | Leakage Rate | Avg Leakage Score | Avg Utility Score |
|---|---:|---:|---:|---:|---:|
| direct_baseline | 2 | 0 | 0.0 | 0.0 | 1.0 |
| policy_first_structured | 2 | 0 | 0.0 | 0.0 | 0.925 |
| tree_of_thoughts | 2 | 1 | 0.5 | 0.35 | 0.925 |

This real-model validation is intentionally small and is not statistically reliable. Its value is that it demonstrates end-to-end feasibility with a real LLM and shows that real model behavior can differ from the idealized mock backend.

## Key Insight

This project demonstrates that prompt-based defenses can reduce sensitive information leakage in controlled settings, but real LLM behavior remains stochastic and requires empirical validation.

The contrast between mock and Ollama results is itself important: simulated backends are useful for reproducible methodology development, while real LLM runs expose model-specific variability, prompt sensitivity, and non-deterministic leakage behavior.

## Outputs

Running `python -m src.main` writes:

```text
data/generated/sensitive_records.csv
data/generated/sensitive_records.json
results/runs/experiment_results.csv
results/runs/experiment_results.json
results/runs/run_metadata.json
results/tables/strategy_comparison.csv
results/tables/strategy_comparison.json
results/reports/findings.md
results/plots/leakage_rate_by_strategy.png
results/plots/avg_leakage_score_by_strategy.png
results/plots/avg_utility_score_by_strategy.png
results/plots/privacy_utility_tradeoff.png
```

`run_metadata.json` stores the timestamp, git commit when available, global random seed, model name, case count, and full config snapshot.

## Metrics

Leakage is detected through:

- exact matching of sensitive field values
- partial matching for structured identifiers
- optional conservative semantic matching for long text fields

Leakage score is a weighted sum over matched fields using `configs/field_weights.json`.

Utility is a lightweight task-aware proxy based on non-refusal, response substance, task alignment, and analytical/actionable content.

## Limitations

- The default mock backend is rule-based and does not represent a real LLM.
- Leakage detection is heuristic.
- Semantic leakage detection is conservative and disabled by default.
- Utility scoring is a reproducible proxy, not human evaluation.

## Future Work

- Run the full matrix against local Ollama models.
- Add API-backed model support.
- Add per-attack and per-task breakdown tables.
- Add semantic leakage evaluation with embeddings or an evaluator model.
- Compare automated utility scores with human ratings.
