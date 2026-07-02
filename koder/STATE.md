---
updated_at: "02 Jul 2026 | 02:20 PM IST"
---

# Koder State

## Past

- Koder-pattern thin operator scaffold was initialized and committed.
- Ornith evaluation harnesses, raw benchmark outputs, and reports were added.
- Root `README.md` now summarizes performance, tough mixed-domain evals, and long conversational-context evals.

## Present

- Durable operator files live under `koder/`; root `AGENTS.md` and `.pi/skills/{open,close}` point into the scaffold.
- Evaluation scripts: `bench_ornith.py`, `tough_eval_ornith.py`, `conversation_context_eval_ornith.py`, and `conversation_context_eval_natural_ornith.py`.
- Reports: `ORNITH_BENCHMARK_REPORT.md`, `ORNITH_TOUGH_EVAL_REPORT.md`, and `ORNITH_CONVERSATION_CONTEXT_EVAL_REPORT.md`; raw outputs live in `benchmark_results/`.
- Current results show strong local performance and conversational retention, with caveats around exact formatting, coding edge cases, and huge-context latency.

## Future

- Rerun eval scripts when the model, Ollama version, hardware, or prompt templates change.
- Add standardized benchmark suites or stricter graders if leaderboard-style comparison is needed.
- Keep generated caches ignored and commit future durable eval results/reports intentionally.
