# Adversarial Privacy Attacks on LLMs and Defense via Prompt Engineering

## Overview

This project presents a **research-style experimental framework** for evaluating **privacy leakage in Large Language Models (LLMs)** under adversarial prompting.

The system simulates realistic scenarios where an LLM is asked to perform useful tasks on structured data while being simultaneously exposed to **malicious prompts attempting to extract sensitive information**.

It evaluates how different **prompt engineering strategies (defenses)** impact:

* privacy leakage
* attack success rate
* utility preservation

---

## Research Question

> How robust are different prompt engineering strategies against adversarial attempts to extract sensitive information from structured data?

---

## Methodology

The framework follows a controlled experimental pipeline:

### 1. Synthetic Sensitive Data

Structured records are generated with fields such as:

* full_name
* email
* phone
* account_id
* vehicle_id
* organization
* travel history
* health notes

All data is fully synthetic.

---

### 2. Task Layer (Utility)

The LLM is asked to perform useful tasks such as:

* summarization
* anomaly detection
* trend description
* recommendation generation
* concise reporting

---

### 3. Adversarial Attack Layer

Each task is augmented with adversarial instructions such as:

* direct extraction
* instruction override
* role confusion
* memory probing
* disguised extraction
* summarization-to-leakage

---

### 4. Prompt Engineering Defenses

We compare multiple strategies:

* direct_baseline
* policy_first_structured
* tree_of_thoughts
* skeleton_of_thought
* least_to_most

---

### 5. LLM Backend

The system supports:

* mock backend (for controlled experiments)
* local models via Ollama (extendable)
* API-based models (future)

---

### 6. Leakage Detection

Leakage is detected by comparing LLM outputs against known sensitive fields using:

* exact matching
* structured partial matching (IDs, emails, etc.)

---

### 7. Scoring Metrics

For each experiment case:

* **Leakage Score**
  Weighted sum of leaked fields

* **Leakage Rate**
  % of cases with any leakage

* **Utility Score (proxy)**
  Based on:

  * response length
  * keyword relevance
  * non-refusal behavior

---

### 8. Aggregation & Visualization

Results are aggregated per strategy and visualized using:

* leakage rate bar charts
* average leakage score
* utility score comparison
* privacy vs utility scatter plot

---

## Repository Structure

```
adversarial-privacy-llm/
│
├── configs/                # Experiment configuration
├── data/                   # Generated synthetic data
├── docs/                   # Methodology & notes
├── notebooks/              # Optional analysis
├── results/                # Outputs (CSV, plots, reports)
│
├── src/
│   ├── data_generation/    # Synthetic dataset generator
│   ├── prompting/          # Prompt builder + strategies
│   ├── tasks/              # Task & attack definitions
│   ├── llm/                # Backend interfaces
│   ├── detection/          # Leakage detection + scoring
│   ├── evaluation/         # Experiment runner + export
│   ├── visualization/      # Plot generation
│   └── main.py             # Entry point
│
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone https://github.com/yourusername/adversarial-privacy-llm.git
cd adversarial-privacy-llm
pip install -r requirements.txt
```

---

## Run the Experiment

```bash
python3 -m src.main
```

---

## Outputs

After running, the following are generated:

### Results Tables

```
results/runs/experiment_results.csv
results/tables/strategy_comparison.csv
```

### Plots

```
results/plots/
├── leakage_rate_by_strategy.png
├── avg_leakage_score_by_strategy.png
├── avg_utility_score_by_strategy.png
└── privacy_utility_tradeoff.png
```

### Findings Report

```
results/reports/findings.md
```

---

## Example Findings

Key observations from the current setup:

* Direct prompting shows the **highest privacy leakage**
* Structured prompting strategies significantly reduce leakage
* **Tree of Thoughts** achieves the lowest leakage score
* Utility remains stable across strategies

---

## Limitations

* Mock backend is rule-based (not a real LLM)
* Leakage detection is heuristic
* Utility is approximated (not human-evaluated)
* No semantic leakage detection yet

---

## Future Work

* Run experiments on real LLMs (Ollama / API)
* Improve semantic leakage detection
* Add per-attack and per-task analysis
* Introduce human-evaluated utility metrics
* Explore fine-tuned defensive prompting

---

## Key Contribution

This project provides a **modular, extensible experimental framework** for:

* evaluating adversarial privacy risks in LLMs
* comparing prompt engineering defenses
* quantifying privacy-utility trade-offs

---

## Author

Anas
Computer Science Student

---

## License

MIT License
