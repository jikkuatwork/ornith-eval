# Ornith Tough Mixed-Domain Eval

Target: `ornith:latest` through Ollama on local machine.

Artifacts:

- Eval harness: `tough_eval_ornith.py`
- Main direct run JSON: `benchmark_results/tough_eval_ornith_latest_direct_20260702T064624Z.json`
- Main direct run Markdown: `benchmark_results/tough_eval_ornith_latest_direct_20260702T064624Z.md`
- Thinking-mode probe JSON: `benchmark_results/tough_eval_ornith_latest_think_20260702T063732Z.json`
- Thinking-mode probe Markdown: `benchmark_results/tough_eval_ornith_latest_think_20260702T063732Z.md`

## Executive summary

I ran a 20-question mixed eval across math, programming, science, logic, data extraction, and security. The main run used deterministic direct generation:

```json
{
  "think": false,
  "temperature": 0,
  "seed": 123,
  "num_ctx": 8192
}
```

Automated score: **19/20 passed**.

Manual/semantic adjustment: **18/20 solid passes**, because the SQL item was structurally detected as a pass by the loose checker but the model response hit the generation limit and included a truncated/incomplete final query. Treat SQL as **partial**, not a clean pass.

High-level result: `ornith` did very well on this small tough mixed set. It handled all math items, all science items, both logic items, JSON extraction, security reasoning, and 3/4 executable Python programming tasks. The main clear implementation bug was an interval-sweep/meeting-rooms solution that undercounted rooms.

## Scores

### Automated direct run

| Domain | Passed | Total |
|---|---:|---:|
| Math / statistics | 6 | 6 |
| Programming / SQL | 4 | 5 |
| Science | 5 | 5 |
| Logic | 2 | 2 |
| Data extraction | 1 | 1 |
| Security | 1 | 1 |
| **Overall** | **19** | **20** |

### Manual adjusted view

| Domain | Solid passes | Total | Notes |
|---|---:|---:|---|
| Math / statistics | 6 | 6 | Strong. |
| Programming / SQL | 3 | 5 | One Python bug; one SQL partial/truncated. |
| Science | 5 | 5 | Strong on these quantitative/conceptual questions. |
| Logic | 2 | 2 | Strong. |
| Data extraction | 1 | 1 | Correct minified JSON. |
| Security | 1 | 1 | Correct password-hashing guidance. |
| **Overall** | **18** | **20** | Best conservative reading. |

Performance during direct run:

- Total wall time: **188.4 s**
- Mean wall time/question: **9.4 s**
- Mean output throughput: **43.5 tok/s**

## Question set and outcomes

| ID | Domain | Result | Expected / tested behavior |
|---|---|---:|---|
| `math_number_theory_crt` | Math | PASS | CRT answer `212`. |
| `math_combinatorics_derangements` | Math | PASS | Exactly 3 fixed points in permutations of 8: `2464`. |
| `math_probability_cards` | Math | PASS | Exactly two pairs probability: `198/4165`. |
| `math_linear_algebra_eigenvalues` | Math | PASS | Eigenvalue multiset `[1,3,3]`. |
| `math_calculus_integral` | Math | PASS | Integral `∫_0^1 x² ln x dx = -1/9`. |
| `math_bayes_medical_test` | Statistics | PASS | Posterior `1/6`, about `16.7%`. |
| `programming_lru_cache` | Programming | PASS | Executable `LRUCache`, passed unit tests. |
| `programming_topological_sort_cycle` | Programming | PASS | Topological sort with cycle detection, passed unit tests. |
| `programming_interval_sweep` | Programming | FAIL | Meeting-rooms implementation undercounted overlapping intervals. |
| `programming_json_transform` | Programming/data | PASS | Aggregated paid order totals correctly. |
| `programming_sql_window` | SQL | PARTIAL | Started toward a solution but response was verbose/truncated; checker was too loose. |
| `physics_projectile_angle` | Physics | PASS | Lower projectile angle about `11.54°`. |
| `physics_circuit_current` | Physics | PASS | Circuit current `2 A`. |
| `chemistry_buffer_ph` | Chemistry | PASS | Buffer pH about `5.06`. |
| `biology_central_dogma_exception` | Biology | PASS | Reverse transcriptase, RNA → DNA exception. |
| `thermo_isothermal_work` | Thermodynamics | PASS | Isothermal expansion work about `5743 J`. |
| `logic_knights_knaves` | Logic | PASS | `A` knave, `B` knight. |
| `logic_scheduling` | Scheduling logic | PASS | Minimum completion time `9`. |
| `data_extraction_tricky_json` | Data extraction | PASS | `{"user_id":42,"action":"deploy","success":false}`. |
| `security_hashing_passwords` | Security | PASS | Plain SHA-256 inadequate; salt and slow/adaptive/memory-hard hashing needed. |

## Failure details

### `programming_interval_sweep`

The generated solution used sorted starts/ends, but initialized `end_idx = 1` instead of `0` and updated the active-room count incorrectly. It failed this basic test:

```python
assert min_meeting_rooms([[0,30], [5,10], [15,20]]) == 2
```

This is a real coding robustness issue: the idea was close, but implementation details were wrong.

### `programming_sql_window`

The automated checker counted this as pass because it saw SQL-ish structure: `SELECT`, window functions, `events`, `2025`, etc. Manual review showed the response was not a clean final answer:

- It included a first draft that was invalid or semantically questionable.
- Then it started revising itself.
- It hit `done_reason: length` at 1200 generated tokens.
- The final intended query was truncated.

So I would treat this as **partial/fail for production use**, not a clean pass.

## Thinking-mode probe

I also ran the same suite with Ollama `think:true` and the original per-question token budgets.

Result: **11/20 automated pass**.

This was not necessarily because the model reasoned worse. Several failures had empty visible responses because hidden thinking consumed the entire `num_predict` budget and ended with `done_reason: length`. Examples: CRT, poker probability, SQL, projectile angle.

Operational takeaway:

- For this model, `think:true` needs a much larger `num_predict` budget on hard questions.
- For concise answer/code generation, `think:false` was substantially more reliable in this eval.
- If using `think:true`, monitor `done_reason` and rerun when the visible answer is empty or truncated.

## Interpretation

`ornith` appears strong for a local 9B quantized model on this mixed challenge set:

- Math: good symbolic/numeric reasoning on this sample.
- Science: good formula use and conceptual recall.
- Python: useful, but still needs tests; one standard interval algorithm was wrong.
- SQL: needs stricter prompting and validation; verbose self-correction can exceed generation budget.
- Structured data: worked well on the JSON extraction case.
- Security: answered with sound password-storage guidance.

Recommended use pattern remains: **let it draft, then validate**. For programming, run tests. For SQL, run against fixtures or at least lint/parse. For exact structured outputs, use JSON mode or schema validation. For tough reasoning, either keep `think:false` with visible derivations or increase `num_predict` substantially for `think:true`.
