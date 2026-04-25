# Experimental Findings

## Overview
This report summarizes a synthetic adversarial privacy evaluation pipeline for LLM prompting strategies.

## Run Metadata
- Backend: **mock**
- Model used: **mock**
- Cases: **1500**
- Random seed: **42**

## Key Observations
- Lowest average leakage score: **tree_of_thoughts** (0.4083).
- Highest average leakage score: **direct_baseline** (1.3167).
- Highest average utility score: **direct_baseline** (0.8333).

## Strategy Table

| Strategy | Cases | Leaks | Leakage Rate | Avg Leakage Score | Avg Utility Score |
|---|---:|---:|---:|---:|---:|
| direct_baseline | 300 | 158 | 0.5267 | 1.3167 | 0.8333 |
| least_to_most | 300 | 93 | 0.31 | 0.775 | 0.8333 |
| policy_first_structured | 300 | 108 | 0.36 | 0.9 | 0.8333 |
| skeleton_of_thought | 300 | 83 | 0.2767 | 0.6917 | 0.8333 |
| tree_of_thoughts | 300 | 49 | 0.1633 | 0.4083 | 0.8333 |

## Interpretation
These results should be interpreted primarily as validation of the experimental pipeline under a synthetic mock backend.
Real-model conclusions should be based on Ollama or API-backed runs.

## Limitations
- Leakage detection is heuristic and may over- or under-estimate some cases.
- Utility is measured using a lightweight proxy rather than human judgment.
- Small local-model runs are useful validation, not final universal evidence.

## Next Steps
- Add per-attack and per-task breakdown plots.
- Compare exact, partial, and semantic leakage patterns by field.
- Add human or model-assisted utility evaluation for selected cases.