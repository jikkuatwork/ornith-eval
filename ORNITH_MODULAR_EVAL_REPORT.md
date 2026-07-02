# Ornith Modular Special-Suite Eval Report

Target: `ornith:latest` via Ollama.

This report covers the full run of the modular eval framework added under `evals/`.

Run command:

```bash
python3 evals/runner.py --suite all --model ornith:latest
```

Full-run artifacts:

- `benchmark_results/modular_eval_deep_convoluted_conversation_ornith_latest_20260702T094449Z.json`
- `benchmark_results/modular_eval_deep_convoluted_conversation_ornith_latest_20260702T094449Z.md`
- `benchmark_results/modular_eval_deep_math_puzzles_ornith_latest_20260702T094716Z.json`
- `benchmark_results/modular_eval_deep_math_puzzles_ornith_latest_20260702T094716Z.md`
- `benchmark_results/modular_eval_difficult_programming_ornith_latest_20260702T094825Z.json`
- `benchmark_results/modular_eval_difficult_programming_ornith_latest_20260702T094825Z.md`
- `benchmark_results/modular_eval_hard_facts_ornith_latest_20260702T094857Z.json`
- `benchmark_results/modular_eval_hard_facts_ornith_latest_20260702T094857Z.md`
- `benchmark_results/modular_eval_kerala_core_ornith_latest_20260702T094950Z.json`
- `benchmark_results/modular_eval_kerala_core_ornith_latest_20260702T094950Z.md`

## Executive summary

Overall full-suite result: **47/56** passed, **83.9%**.

| Suite | Result | Accuracy | Total wall time | Mean latency | Notes |
|---|---:|---:|---:|---:|---|
| `deep_convoluted_conversation` | 11/11 | 100.0% | 52.7s | 4.79s | Excellent long-context conversational memory to 50k prompt tokens. |
| `deep_math_puzzles` | 9/10 | 90.0% | 147.4s | 14.74s | Strong; one counting problem failed/truncated. |
| `difficult_programming` | 3/8 | 37.5% | 68.7s | 8.59s | Main weak area; several executable-code tasks failed unit tests. |
| `hard_facts` | 12/12 | 100.0% | 32.2s | 2.68s | Strong factual recall on this sample. |
| `kerala_core` | 12/15 | 80.0% | 53.0s | 3.54s | Good culture/geography; weak on simple Malayalam transliteration words. |

Combined wall time: about **354 seconds** / **5.9 minutes**.

## Suite details

### Deep convoluted conversation

Result: **11/11**.

The suite contains a 1200-turn synthetic conversation with corrections, rumors, ownership transfers, false decoys, and late probes. The hardest probe reached **50,158 prompt tokens**.

Key late answers:

| Probe | Turn | Prompt tokens | Result | Response |
|---|---:|---:|---:|---|
| Tom ball after decoys | 150 | 6,116 | PASS | `Red.` |
| Current vault code | 540 | 22,310 | PASS | `9134.` |
| Tom animal after false ox story | 930 | 38,593 | PASS | `Yellow ox.` |
| Late composite all | 1030 | 42,786 | PASS | Included red, yellow ox, 9134, green drawer, Priya, coconut lamp, and archive-token details. |
| Ferry coreference ultra-late | 1200 | 50,158 | PASS | `Dev.` |

Interpretation: context tracking and decoy resistance remain strong at ~50k tokens in this cached conversational path.

### Deep math puzzles

Result: **9/10**.

Passed:

- Catalan lattice paths: `429`
- Linear recurrence: `60073`
- Expected tosses until HH: `6`
- Spanning trees of `K_{3,4}`: `432`
- CRT constraints: `985`
- Inclusion/exclusion divisibility count: `200`
- Urn posterior/without-replacement probability: `1/3`
- Polynomial remainder: `6765x + 4181`
- Fixed points in permutations of 9: `5544`

Failed:

- `digit_sum_divisible_by_7`: expected `9`. The model enumerated multiples and hit `num_predict` length before finishing, with no correct final answer. This is partly a reasoning/eval-budget failure: it used a brute-force listing strategy instead of a compact modular/counting strategy.

### Difficult programming

Result: **3/8**.

Passed executable tests:

- `dijkstra_path_reconstruction`
- `sliding_window_median`
- `tarjan_scc`

Failed executable tests:

- `expression_parser`: `IndexError` from unsafe `peek()` at end of string.
- `json_patch_subset`: list-index handling bug when adding `/a/1`.
- `word_ladder_length`: neighbor generation bug using `startswith(pattern)`/`endswith(pattern)` incorrectly.
- `min_window_subsequence`: incorrect DP/reconstruction logic.
- `weighted_interval_scheduling`: incorrect predecessor lookup / DP indexing.

Interpretation: Ornith can produce useful code for some hard tasks, but difficult algorithm/data-structure implementations need tests and probably iterative repair. One-shot pass rate on this suite is low.

### Hard facts

Result: **12/12**.

Passed factual probes across:

- x86-64 SysV ABI argument registers
- IPv6 loopback
- HTTP 429
- Unicode replacement character `U+FFFD`
- Gödel's second incompleteness theorem
- CAP theorem
- p53 tumor suppressor role
- CRISPR guide RNA
- PostgreSQL `xmin`/`xmax`
- Apollo 11 landing date
- TCP `FIN`
- Mercury perihelion precession

Interpretation: strong on this small hard-facts sample, though answers were often verbose when the prompt did not demand strict brevity.

### Kerala core

Result: **12/15**.

Strong areas:

- Kerala capital: Thiruvananthapuram
- Malayalam as primary official language
- 14 districts
- Onam/Mahabali/Maveli
- Pookkalam and sadya
- Vallam Kali
- Sree Narayana Guru
- Vembanad Lake
- Munnar in Idukki
- Kalaripayattu
- Kudumbashree
- Vishukkani

Failed Malayalam word/phrase probes:

- `vellam`: expected water; model answered morning/dawn.
- `nanni`: expected thanks/thank you; model answered good/well.
- `sukhamano?`: expected roughly “how are you / are you well”; model did not recognize it as the standard phrase.

Interpretation: Kerala culture/geography recall is decent, but Malayalam transliteration/basic-word handling is a weakness.

## Overall interpretation

The modular full run sharpens the earlier picture:

- **Very strong:** long conversational context, hard factual recall, many math puzzles.
- **Good but uneven:** Kerala-flavoured local knowledge; culture/geography strong, Malayalam words weak.
- **Weakest:** difficult one-shot programming, especially parser/DP/string/patch algorithms under executable tests.

Recommended use:

- Use Ornith for long-context chat recall and factual/cultural QA, with verification for specialized language details.
- For math, encourage compact methods and give enough output budget; watch for enumeration/truncation.
- For programming, use an iterative loop: generate → run tests → feed failures back → repair. Do not rely on one-shot correctness for complex algorithms.
