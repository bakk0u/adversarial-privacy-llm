# Experimental Findings

## Overview
This report summarizes the results of a synthetic adversarial privacy evaluation pipeline for LLM prompting strategies.

## Key Observations
- Lowest average leakage score: **tree_of_thoughts** (0.6583).
- Highest average leakage score: **direct_baseline** (1.3167).
- Highest average utility score: **direct_baseline** (0.9167).

## Strategy Table

| Strategy | Cases | Leaks | Leakage Rate | Avg Leakage Score | Avg Utility Score |
|---|---:|---:|---:|---:|---:|
| direct_baseline | 300 | 158 | 0.5267 | 1.3167 | 0.9167 |
| least_to_most | 300 | 93 | 0.31 | 0.775 | 0.9167 |
| policy_first_structured | 300 | 98 | 0.3267 | 0.8167 | 0.9167 |
| skeleton_of_thought | 300 | 90 | 0.3 | 0.75 | 0.9167 |
| tree_of_thoughts | 300 | 79 | 0.2633 | 0.6583 | 0.9167 |

## Interpretation
These results should be interpreted primarily as a validation of the experimental pipeline under a synthetic mock backend.
The current setup is useful for testing data flow, prompt construction, leakage detection, scoring, aggregation, and visualization.
Stronger scientific conclusions should be based on future runs with real local or API-backed LLMs.

## Limitations
- The backend used here is synthetic and rule-based.
- Leakage detection is heuristic and may over- or under-estimate some cases.
- Utility is measured using a lightweight proxy rather than human judgment.

## Next Steps
- Run the same framework against Ollama-backed local models.
- Refine leakage detection for semantic leakage.
- Add per-attack and per-task breakdown plots.