# Ollama Tiny Run Findings

## Experimental Setup

This run evaluates the privacy-leakage pipeline against a real local LLM backend.

- Backend: Ollama
- Model: `llama3.1:8b`
- Dataset: 2 synthetic records
- Total cases: 6 model calls
- Task: `summarization`
- Attack: `direct_extraction`
- Strategies: `direct_baseline`, `policy_first_structured`, `tree_of_thoughts`
- Random seed: `42`

The configuration was intentionally reduced for local hardware constraints. It uses a tiny record set, short responses, and a small strategy subset so the experiment can validate real-model execution without running a full benchmark.

## Key Observations

| Strategy | Cases | Leaks | Leakage Rate | Avg Leakage Score | Avg Utility Score |
|---|---:|---:|---:|---:|---:|
| direct_baseline | 2 | 0 | 0.0 | 0.0 | 1.0 |
| policy_first_structured | 2 | 0 | 0.0 | 0.0 | 0.925 |
| tree_of_thoughts | 2 | 1 | 0.5 | 0.35 | 0.925 |

- `direct_baseline` produced no detected leakage in this run.
- `policy_first_structured` also produced no detected leakage in this run.
- `tree_of_thoughts` produced detected leakage in 1 of 2 cases.
- The leaked field in the detected case was `mobility_summary`, where the response reproduced sensitive record content closely enough to trigger exact leakage detection.

## Interpretation

These results should not be interpreted as evidence that `tree_of_thoughts` is worse than the other strategies. The sample contains only two records and two cases per strategy, so a single leaked response changes the leakage rate from `0.0` to `0.5`.

The main interpretation is that real LLM behavior is stochastic and prompt-sensitive even under a small, controlled local configuration. Unlike the mock backend, the Ollama model can produce incomplete answers, paraphrases, or unexpectedly specific text depending on the prompt framing and generation path.

This makes the tiny run useful as a real-model validation check, but not as a statistically reliable ranking of defense strategies.

## Comparison with Simulated Results

The larger mock-backend experiment showed a clear controlled ordering:

- `tree_of_thoughts` had the lowest leakage rate in the simulated results.
- `direct_baseline` had the highest leakage rate in the simulated results.

The tiny Ollama run shows inconsistent ordering:

- `direct_baseline` and `policy_first_structured` had no detected leakage.
- `tree_of_thoughts` had one detected leakage case.

This contrast is an important research signal. The mock backend encodes idealized behavior and is useful for validating methodology, scoring, aggregation, and reproducibility. A real LLM introduces stochasticity, prompt sensitivity, decoding artifacts, and model-specific behavior. Therefore, simulated experiments can support controlled pipeline validation, but real-model experiments are required before making empirical claims about privacy defenses.

## Limitations

- The sample size is extremely small: 2 records and 6 total cases.
- Each strategy is evaluated on only 2 cases.
- The run is constrained by local hardware and uses a reduced configuration.
- Only one model, `llama3.1:8b`, is tested.
- Leakage detection is heuristic and may miss semantic leakage or over-count close textual reuse.
- Utility is measured with an automated proxy rather than human judgment.
- No statistical significance should be inferred from this run.

## Conclusion

This run validates that the project can execute end-to-end privacy experiments against a real local LLM through Ollama, produce case-level outputs, detect leakage, aggregate results, and generate report artifacts.

It should be treated as a functionality and feasibility validation, not as a final benchmark. Larger real-model runs are needed before drawing conclusions about strategy effectiveness.

## Future Work

- Run larger Ollama experiments with 300-600 cases.
- Test multiple local models, including DeepSeek and Mistral variants.
- Improve semantic leakage detection beyond exact and partial matching.
- Add human evaluation of response utility and privacy judgments.
- Compare strategy behavior across tasks, attack types, and model families.
