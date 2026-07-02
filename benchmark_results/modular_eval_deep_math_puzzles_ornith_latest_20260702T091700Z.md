# Modular Eval: `deep_math_puzzles` on `ornith:latest`

Deep math puzzle/problem-set suite with exact deterministic graders.

## Summary

- Result: **2/2** (**100.0%**) 
- Total wall time: **20.8s**
- Mean/median latency: **10.39s / 10.39s**
- Max prompt tokens: **119**
- Mean prompt ingest speed: **902.0 tok/s**
- Mean output speed: **48.4 tok/s**

## By category

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| combinatorics | 1 | 1 | 100.0% |
| recurrences | 1 | 1 | 100.0% |

## Per-item results

| ID | Category | Result | Wall s | Eval tokens | Detail |
|---|---|---:|---:|---:|---|
| `catalan_lattice_paths` | combinatorics | PASS | 10.12 | 449 | values=[429.0]; expected=429.0; best_abs_err=0.0 |
| `linear_recurrence_a10` | recurrences | PASS | 10.66 | 480 | values=[60073.0]; expected=60073.0; best_abs_err=0.0 |
