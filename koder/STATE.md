---
updated_at: "02 Jul 2026 | 02:49 PM IST"
---

# Koder State

## Past

- Koder-pattern thin operator scaffold was initialized and committed.
- Ornith performance, tough mixed-domain, and conversational-context eval harnesses/reports were added.
- Modular eval framework was added under `evals/` with special suites for convoluted conversation, math puzzles, difficult programming, hard facts, and Kerala core.

## Present

- Durable operator files live under `koder/`; root `AGENTS.md` and `.pi/skills/{open,close}` point into the scaffold.
- One-off harnesses remain at repo root; reusable suite runner is `evals/runner.py` with graders in `evals/graders.py` and suite JSON in `evals/suites/`.
- Reports and raw outputs live in `benchmark_results/`; modular suite smoke outputs are committed with `modular_eval_*` filenames.
- Current evidence shows strong local performance and conversational retention, with caveats around formatting, coding edge cases, and huge-context latency.

## Future

- Run full modular suites with `python3 evals/runner.py --suite <suite> --model ornith:latest` when more scores are needed.
- Add stricter graders or new JSON suite files as evaluation needs evolve.
- Keep caches ignored and commit future durable eval results/reports intentionally.
