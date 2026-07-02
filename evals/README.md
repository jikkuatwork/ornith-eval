# Modular Eval Suites

This directory contains a reusable eval framework for `ornith:latest` and other Ollama models.

The framework is intentionally lightweight:

- suite definitions live in JSON files under `evals/suites/`
- `evals/runner.py` runs standard or conversation suites through Ollama
- `evals/graders.py` provides deterministic graders for exact text, numeric answers, fractions, JSON, regex, slot/term matching, and executable Python tasks
- results are written to `benchmark_results/modular_eval_<suite>_<model>_<timestamp>.{json,md}`

## Suites

| Suite | Kind | Size | Purpose |
|---|---|---:|---|
| `deep_convoluted_conversation` | conversation | 11 probes | Long-context memory with corrections, rumors, ownership transfers, multi-hop facts, and distractors. |
| `deep_math_puzzles` | standard | 10 cases | Exact-answer math puzzles across combinatorics, recurrence, probability, graph theory, number theory, and algebra. |
| `difficult_programming` | standard | 8 cases | Executable Python coding tasks with unit-test graders. |
| `hard_facts` | standard | 12 cases | Hard factual recall across systems, networking, Unicode, biology, databases, history, and physics. |
| `kerala_core` | standard | 15 cases | Kerala-flavoured facts, Malayalam words, geography, culture, and social ideas. |

## Quick start

List suites:

```bash
python3 evals/runner.py --list
```

Run one suite:

```bash
python3 evals/runner.py --suite kerala_core --model ornith:latest
```

Run a smoke subset:

```bash
python3 evals/runner.py --suite difficult_programming --limit 1 --model ornith:latest
```

Run all suites with a small limit per suite:

```bash
python3 evals/runner.py --suite all --limit 2 --model ornith:latest
```

Run the deep conversation suite at the intended context size:

```bash
python3 evals/runner.py \
  --suite deep_convoluted_conversation \
  --model ornith:latest \
  --num-ctx 65536
```

Override context size for any suite:

```bash
python3 evals/runner.py --suite deep_math_puzzles --num-ctx 32768
```

Enable Ollama thinking mode:

```bash
python3 evals/runner.py --suite deep_math_puzzles --think
```

If using `--think`, consider increasing suite `num_predict` values or editing the suite defaults; hidden thinking tokens can exhaust output budgets.

## Suite format

### Standard suite

```json
{
  "id": "example_suite",
  "title": "Example suite",
  "kind": "standard",
  "defaults": {
    "think": false,
    "num_ctx": 8192,
    "num_predict": 512,
    "temperature": 0,
    "seed": 123
  },
  "cases": [
    {
      "id": "case_id",
      "category": "math",
      "prompt": "Solve. End with FINAL: <answer>.",
      "grader": {"type": "numeric", "value": 42, "tolerance": 0}
    }
  ]
}
```

### Conversation suite

```json
{
  "id": "conversation_suite",
  "kind": "conversation",
  "turns": 1200,
  "system": "Remember facts and answer briefly.",
  "events": [
    {"turn": 2, "text": "Tom had a red ball."}
  ],
  "probes": [
    {
      "id": "tom_ball_late",
      "after_turn": 900,
      "fact_turn": 2,
      "question": "What color was Tom's ball?",
      "grader": {"type": "exact", "value": "red"}
    }
  ]
}
```

Conversation suites synthesize filler turns between explicit events and use short synthetic assistant acknowledgements. The model is called only for probes, which isolates context retention and speed.

## Grader types

Available grader types:

- `exact`
- `contains_all`
- `contains_any`
- `combo`
- `numeric`
- `fraction`
- `json_equals`
- `regex_fullmatch`
- `python_unittest`
- `choice`

`python_unittest` extracts Python code from Markdown fences if needed, appends the suite's tests, and runs the candidate in a temporary directory with a timeout. Treat these as local trusted evals; do not add tests that access secrets, networks, or destructive filesystem paths.

## Smoke validation performed

The framework was smoke-tested against `ornith:latest` with limited runs:

| Suite | Limit | Result |
|---|---:|---:|
| `kerala_core` | 3 | 3/3 |
| `deep_math_puzzles` | 2 | 2/2 |
| `difficult_programming` | 1 | 1/1 |
| `deep_convoluted_conversation` | 2 probes | 2/2 |
| `hard_facts` | 3 | 3/3 |

Raw smoke outputs are in `benchmark_results/` with `modular_eval_...` filenames.
