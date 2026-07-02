# Ornith Local Model Evaluation

This repository contains practical benchmark/evaluation harnesses and reports for the local Ollama model `ornith:latest`.

The goal is not to produce a leaderboard score; it is to answer: **what is this model practically good for on this machine, how fast is it, and can it keep context across long conversations?**

## Target model and environment

| Dimension | Value |
|---|---|
| Model | `ornith:latest` |
| Ollama | `0.31.1` |
| Architecture | `qwen35` |
| Parameters | `9.0B` |
| Quantization | `Q4_K_M` |
| Model size | ~5.6 GB |
| Advertised context | `262,144` tokens |
| Capabilities | `completion`, `tools`, `thinking` |
| CPU | AMD Ryzen 7 3700X, 8 cores / 16 threads |
| RAM | 31 GiB |
| GPU | NVIDIA GeForce RTX 3060, 12 GiB VRAM |

## Executive verdict

`ornith:latest` is a capable local coding/chat assistant for this hardware profile.

Highlights:

- Short-context generation is comfortable at about **48 output tokens/s**.
- Cold start is about **4.6 s**; warm tiny prompts average about **0.66 s**.
- Tool calling through Ollama works for simple function invocation.
- Long-context retrieval works very well in synthetic tests, including a successful **207k-token** needle probe.
- Conversational memory was strong in the custom long-chat eval: **13/13** on a natural **1000-turn** test.
- Coding quality is useful but should be validated with tests; the model made a real bug in a meeting-rooms interval sweep implementation.
- Exact output formatting is imperfect unless constrained by API features such as Ollama JSON mode.

## Reports

| Report | Description |
|---|---|
| [`ORNITH_BENCHMARK_REPORT.md`](ORNITH_BENCHMARK_REPORT.md) | Performance, throughput, long-context, tools, and lightweight capability eval. |
| [`ORNITH_TOUGH_EVAL_REPORT.md`](ORNITH_TOUGH_EVAL_REPORT.md) | Tough mixed-domain eval across math, programming, science, logic, data, and security. |
| [`ORNITH_CONVERSATION_CONTEXT_EVAL_REPORT.md`](ORNITH_CONVERSATION_CONTEXT_EVAL_REPORT.md) | Long conversational context and memory eval, including the Tom/red-ball/yellow-ox scenario. |
| [`evals/README.md`](evals/README.md) | Modular eval framework and the new special-purpose suites. |

Raw run outputs are under [`benchmark_results/`](benchmark_results/).

## Key results

### Performance

From `bench_ornith.py`:

| Metric | Result |
|---|---:|
| Cold tiny prompt | ~4.62 s |
| Warm tiny prompt average | ~0.66 s |
| Short-context generation | ~48 tok/s |
| Mean long-context prompt ingest, tested cases | ~1,333 tok/s |
| Long-context needle retrieval | 5/5 in main run |
| 207k-token context probe | pass, but slow |

The max-context probe succeeded at **207,506 prompt tokens**, but it pushed the model into CPU/GPU offload and slowed output to about **2 tok/s**. For interactive work, `num_ctx` around **32k–64k** is a much better operating range.

### Capability and tool use

The initial capability harness scored **7/12** strictly. Most misses were format-control issues rather than semantic failures:

- correct arithmetic but with extra explanation despite “only integer”
- correct JSON wrapped in Markdown fences
- correct regex wrapped in Markdown fences
- semantically okay SQL that was not index-optimal

The more focused tough eval did better:

| Eval | Automated | Conservative/manual interpretation |
|---|---:|---:|
| Tough mixed-domain direct mode | 19/20 | 18/20 solid |
| Tough mixed-domain `think:true` probe | 11/20 | hidden thinking exhausted output budget on several tasks |

Tool calling worked in Ollama `/api/chat`: the model emitted a correct `add(a=17,b=25)` call and then answered from the tool result.

### Tough mixed-domain eval

The tough eval covered math, programming, science, logic, data extraction, and security.

Direct-mode result:

| Domain | Result |
|---|---:|
| Math / statistics | 6/6 |
| Science | 5/5 |
| Logic | 2/2 |
| Data extraction | 1/1 |
| Security | 1/1 |
| Programming / SQL | automated 4/5; manually 3/5 solid |

Notable pass examples:

- Chinese remainder theorem
- derangements / fixed points
- poker two-pair probability
- eigenvalues
- calculus integral
- Bayes posterior
- projectile angle
- circuit current
- buffer pH
- thermodynamics work
- LRU cache unit tests
- topological sort unit tests

Notable weaknesses:

- `min_meeting_rooms` implementation undercounted overlapping intervals.
- SQL response was verbose and truncated despite matching loose structural checks.

### Conversational context eval

A new eval was built specifically for long conversational memory, including the scenario:

> Tom was playing with his red ball, saw a yellow ox far away, and went home surprised.

Then after hundreds of distractor turns, the eval asks what color Tom’s ball was and related questions.

Natural 1000-turn run:

| Metric | Result |
|---|---:|
| Simulated turns | 1000 |
| Probes | 13 |
| Passed | 13 |
| Accuracy | 100% |
| Max prompt tokens evaluated | 39,857 |
| Mean probe latency | 3.31 s |
| Median probe latency | 1.64 s |
| Mean prompt ingest speed | ~13,961 tok/s |
| Mean output speed | ~54.9 tok/s |

Late-probe examples:

| Probe | Turn | Gap from source fact | Model response |
|---|---:|---:|---|
| Tom ball color | 340 | 338 turns | `Red.` |
| Tom ball ultra-late | 700 | 698 turns | `Red.` |
| Ultra-late composite | 1000 | 998 turns | `Red, yellow ox, 7305, green drawer, Priya, violet rook.` |

Controlled 340-turn run also scored **13/13**.

### Modular special-purpose suites

A reusable suite runner now lives under [`evals/`](evals/). It supports standard prompt/response suites and synthetic long-conversation suites.

Seed suites:

| Suite | Purpose |
|---|---|
| `deep_convoluted_conversation` | Corrections, rumors, similar entities, ownership transfers, multi-hop facts, and late probes. |
| `deep_math_puzzles` | Exact-answer math problem sets. |
| `difficult_programming` | Executable Python tasks with unit-test graders. |
| `hard_facts` | Difficult factual recall across systems, science, history, and computing. |
| `kerala_core` | Kerala-flavoured facts, Malayalam words, culture, geography, and social ideas. |

Run them with:

```bash
python3 evals/runner.py --list
python3 evals/runner.py --suite kerala_core --model ornith:latest
python3 evals/runner.py --suite deep_convoluted_conversation --model ornith:latest --num-ctx 65536
```

Smoke runs for all new suite families passed on limited subsets; outputs are in `benchmark_results/modular_eval_*.{json,md}`.

## Repository layout

```text
.
├── README.md
├── bench_ornith.py
├── tough_eval_ornith.py
├── conversation_context_eval_ornith.py
├── conversation_context_eval_natural_ornith.py
├── evals/
│   ├── README.md
│   ├── runner.py
│   ├── graders.py
│   └── suites/
├── ORNITH_BENCHMARK_REPORT.md
├── ORNITH_TOUGH_EVAL_REPORT.md
├── ORNITH_CONVERSATION_CONTEXT_EVAL_REPORT.md
├── benchmark_results/
│   ├── *.json
│   └── *.md
├── run.zsh
└── koder/
    ├── AGENTS.md
    ├── STATE.md
    ├── issues/
    └── skills/
```

The repo also includes a `koder/` durable operator scaffold for session handoff and future eval work tracking.

## How to rerun

Prerequisites:

- Python 3.12+
- Ollama running locally
- `ornith:latest` available in `ollama list`
- Python `requests` package available

Check model:

```bash
ollama list
ollama show ornith:latest
```

Run the general benchmark:

```bash
python3 bench_ornith.py --model ornith:latest
```

Run the tough mixed-domain eval:

```bash
python3 tough_eval_ornith.py --model ornith:latest
```

Run the controlled conversational context eval:

```bash
python3 conversation_context_eval_ornith.py --model ornith:latest --turns 340 --num-ctx 32768
```

Run the natural long-conversation eval:

```bash
python3 conversation_context_eval_natural_ornith.py --model ornith:latest --turns 1000 --num-ctx 65536
```

Run a modular suite:

```bash
python3 evals/runner.py --suite deep_math_puzzles --model ornith:latest
python3 evals/runner.py --suite difficult_programming --model ornith:latest
python3 evals/runner.py --suite hard_facts --model ornith:latest
python3 evals/runner.py --suite kerala_core --model ornith:latest
```

Use `--think` on the eval scripts to enable Ollama thinking mode. If using `--think`, increase `num_predict` or expect some answers to be truncated/empty because hidden thinking consumes the generation budget.

## Recommended operating profile

For day-to-day local coding/chat use:

```json
{
  "think": false,
  "options": {
    "temperature": 0,
    "num_ctx": 32768,
    "num_predict": 512
  },
  "keep_alive": "10m"
}
```

For structured extraction, prefer Ollama JSON mode:

```json
{
  "format": "json",
  "think": false,
  "options": {
    "temperature": 0
  }
}
```

For very long documents or chats:

- `32k–64k` context is the best interactive range on this RTX 3060 setup.
- `131k+` and `262k` can work, but latency rises substantially and CPU/GPU offload may occur.
- Use chunking/RAG when responsiveness matters.

## Caveats

- These are practical local evals, not standardized benchmark suites like HumanEval, MMLU, SWE-bench, or GPQA.
- The conversational eval keeps the full transcript in context; it does not test external memory or summarization.
- The long-chat filler assistant replies are synthetic short acknowledgements, so those tests isolate memory retrieval rather than full interactive generation every turn.
- Graders are lightweight and mostly deterministic; some results were manually reviewed where automated checks were too loose.
- Always validate generated code with tests and validate structured output with JSON/schema checks.

## Bottom line

`ornith:latest` looks very useful as a local model for coding assistance, structured extraction, long-context chat recall, and tool-driven workflows. The strongest setup is to wrap it with validation: tests for code, JSON mode for structured data, tool calls for deterministic work, and moderate context sizes for speed.
