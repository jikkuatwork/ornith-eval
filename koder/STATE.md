---
updated_at: "02 Jul 2026 | 03:22 PM IST"
---

# Koder State

## Past

- Koder-pattern thin operator scaffold was initialized and committed.
- Ornith performance, tough mixed-domain, conversational-context, and modular special-suite eval harnesses/reports were added.
- Full modular suite run was completed and recorded: combined `47/56` across deep conversation, math puzzles, programming, hard facts, and Kerala core.

## Present

- Durable operator files live under `koder/`; root `AGENTS.md` and `.pi/skills/{open,close}` point into the scaffold.
- Reusable suite runner is `evals/runner.py`; graders are in `evals/graders.py`; suite JSON lives in `evals/suites/`.
- Latest modular report is `ORNITH_MODULAR_EVAL_REPORT.md`; latest raw outputs use `benchmark_results/modular_eval_*20260702T094*.{json,md}`.
- Current evidence: strong long-context conversation and hard facts; good math; weak one-shot difficult programming; Kerala Malayalam transliteration words need caution.

## Future

- For more scores, run `python3 evals/runner.py --suite <suite> --model ornith:latest` or `--suite all`.
- Consider iterative repair evals for programming, and stricter Kerala/Malayalam suites if local-language performance matters.
- Keep caches ignored and commit future durable eval results/reports intentionally.
