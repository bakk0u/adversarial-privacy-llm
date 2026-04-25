# Findings Summary

This document summarizes the current default experiment run. Results are generated with the deterministic mock backend and should be interpreted as validation of the framework rather than empirical claims about a real LLM.

## Run Scope

- Records: 25
- Tasks: summarization, anomaly detection, recommendation
- Attacks: direct extraction, instruction override, memory probing, disguised extraction
- Strategies: direct baseline, policy-first structured, tree of thoughts, skeleton of thought, least-to-most
- Total cases: 1500

## Strategy Results

| Strategy | Cases | Leaks | Leakage Rate | Avg Leakage Score | Avg Utility Score |
|---|---:|---:|---:|---:|---:|
| direct_baseline | 300 | 158 | 0.5267 | 1.3167 | 0.8333 |
| least_to_most | 300 | 93 | 0.3100 | 0.7750 | 0.8333 |
| policy_first_structured | 300 | 108 | 0.3600 | 0.9000 | 0.8333 |
| skeleton_of_thought | 300 | 83 | 0.2767 | 0.6917 | 0.8333 |
| tree_of_thoughts | 300 | 49 | 0.1633 | 0.4083 | 0.8333 |

## Main Observations

The direct baseline leaks most often and has the highest average leakage score. This is expected because it contains no explicit defensive framing.

`tree_of_thoughts` produces the lowest leakage rate and average leakage score in the current mock run. `skeleton_of_thought` is the next strongest strategy by privacy score.

Utility scores are equal across strategies in this run because the mock backend produces a consistent useful base response. Real-model runs are needed to evaluate whether stronger privacy prompts reduce useful task completion.

## Interpretation

The current result supports the internal validity of the framework:

- the experiment matrix expands correctly
- strategy-specific backend behavior is reflected in aggregate metrics
- leakage detection and weighted scoring produce interpretable differences
- generated reports, tables, plots, and metadata are reproducible

It does not establish that one strategy is universally safer for real LLMs. That requires running the same matrix against local or API-backed models.

## Interpreting Real Ollama Results

Real Ollama runs are empirical validation runs. They should be interpreted separately from mock runs:

- mock results show whether the framework, metrics, exports, and plots behave as expected under controlled simulated leakage
- Ollama results show how a concrete local model behaves under the same attack and defense matrix

When reporting Ollama results, include:

- actual model used from `run_metadata.json`
- requested model and fallback model, if fallback occurred
- number of completed cases
- best and worst privacy-performing strategies
- leakage-rate and average-leakage-score differences
- utility-score differences across strategies

Do not generalize one Ollama run to all LLMs. A 600-case local validation is useful evidence for the selected model and decoding settings, but final conclusions require multiple models, repeated runs or controlled decoding, and deeper qualitative analysis of leaked fields.

## Next Analysis Steps

- Run the smaller Ollama validation config with `llama3.1:8b` or fallback `deepseek-r1:8b`.
- Add per-attack and per-task breakdown tables.
- Compare exact and partial leakage patterns by field.
- Enable semantic matching in a separate sensitivity analysis.
- Add human or model-assisted utility evaluation for a subset of responses.
