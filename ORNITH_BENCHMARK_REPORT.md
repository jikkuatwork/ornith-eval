# Ornith Ollama Benchmark Report

Benchmark target: `ornith:latest` via Ollama `0.31.1` on `http://127.0.0.1:11434`.

Raw artifacts:

- Benchmark harness: `bench_ornith.py`
- Main raw run: `benchmark_results/ornith_latest_20260702T061847Z_with_200k.json`
- Standalone max-context probe: `benchmark_results/ornith_latest_context_200k_probe.json`

## Executive summary

`ornith:latest` is a practical local coding-assistant model with strong throughput on the RTX 3060 for normal context sizes, working Ollama tool-call support, and surprisingly good long-context needle retrieval. It is best used as a fast local coding/extraction/rewrite assistant with tests or validators around it.

Key findings:

- **Model:** Qwen-family `qwen35`, `9.0B`, `Q4_K_M`, 5.6 GB model file, advertised `262,144` token context, capabilities: `completion`, `tools`, `thinking`.
- **Hardware:** AMD Ryzen 7 3700X, 32 GiB RAM, NVIDIA RTX 3060 12 GiB.
- **Normal generation speed:** ~**48 output tokens/s** for 128-879 token generations at short context.
- **Cold start:** ~**4.6 s** from stopped model to first tiny answer.
- **Warm tiny prompt latency:** ~**0.66 s** wall-clock average.
- **Long context:** succeeded at needle retrieval up to **207,506 prompt tokens**, but max-context use offloaded to CPU/GPU and slowed generation to ~**2 tok/s**.
- **Tool use:** Ollama function/tool calling worked: emitted correct `add(a=17,b=25)` call and answered from tool result.
- **Capability harness:** strict automated pass rate was **7/12**. A semantic review shows most failures were **format obedience** issues, not inability: verbose answer despite “only integer”, fenced JSON/regex despite “only JSON/pattern”, and SQL using `EXTRACT(YEAR...)` rather than index-friendly date bounds. Main real coding robustness issue: one generated interval merge function failed on tuple inputs.

Bottom line: **very usable locally for coding help, bug fixes, BFS-style algorithms, SQL drafts, summaries, long-document retrieval, and tool-driven workflows. Do not trust exact output formatting or edge-case correctness without validation.**

## Environment

| Dimension | Value |
|---|---|
| Ollama | `0.31.1` |
| Model | `ornith:latest` |
| Digest | `a75697c145891910e312c95e4a9fc1ccb8653e5ef543b23b0403a4665b82fd91` |
| Architecture | `qwen35` |
| Parameters | `9.0B` |
| Quantization | `Q4_K_M` |
| Context length | `262144` |
| Embedding length | `4096` |
| Capabilities | `completion`, `tools`, `thinking` |
| CPU | AMD Ryzen 7 3700X, 8 cores / 16 threads |
| RAM | 31 GiB |
| GPU | NVIDIA GeForce RTX 3060, 12 GiB VRAM, driver `550.163.01` |

The model Modelfile uses a simple prompt template plus this system instruction:

> You are Ornith, an open-source agentic coding assistant. Think step by step in a reasoning block, then act. Use the provided tools when they help. Be concise, correct, and direct: write working code and explain only what is non-obvious.

## Methodology

The benchmark used Ollama HTTP APIs:

- `/api/generate` for completion, performance, long-context, and capability probes.
- `/api/chat` with `tools` for function-calling validation.

Most capability tests used:

- `temperature: 0`
- `seed: 42`
- `think: false`

Generation throughput used `temperature: 0.7` to avoid early stopping. Long-context probes set explicit `num_ctx`. Results are practical harness results, not a standardized benchmark like HumanEval, MMLU, or SWE-bench.

## Performance results

### Load and small-prompt latency

| Case | Wall time | Notes |
|---|---:|---|
| Cold tiny prompt | **4.62 s** | After `ollama stop ornith:latest`; response `ready` |
| Warm tiny prompt avg | **0.66 s** | 3 runs, response `ready` |

Cold load is noticeable but acceptable. Use `keep_alive` for interactive workflows.

### Generation throughput

Prompt: continuous prose generation, `think:false`, short context.

| Output budget | Actual eval tokens | Wall time | Eval tok/s | Stop reason |
|---:|---:|---:|---:|---|
| 128 | 128 | 3.31 s | **47.38** | length |
| 512 | 512 | 11.30 s | **48.29** | length |
| 1024 | 879 | 19.01 s | **48.14** | stop |

Observed practical short-context generation rate: **~48 tok/s**.

### Thinking overhead

Same rate-reasoning prompt with and without Ollama `think`.

| Mode | Answer | Wall time | Eval tokens | Eval tok/s | Thinking chars |
|---|---:|---:|---:|---:|---:|
| `think:false` | `5` | 0.87 s | 2 | 89.80 | 0 |
| `think:true` | `5` | 2.11 s | 69 | 47.96 | 231 |

For simple prompts, `think:true` adds latency and hidden-token cost without improving the answer. Use it selectively for hard reasoning/design tasks, and allocate enough `num_predict` because hidden thinking consumes the generation budget.

### Long-context retrieval

Task: one `NEEDLE` record hidden in a synthetic haystack; answer only the access code.

| Prompt tokens | Needle position | `num_ctx` | Wall time | Prompt tok/s | Eval tok/s | Result |
|---:|---|---:|---:|---:|---:|---|
| 6,626 | middle | 8,192 | 9.06 s | 1,594 | 50.38 | pass |
| 26,066 | middle | 32,768 | 23.06 s | 1,446 | 45.84 | pass |
| 103,826 | middle | 131,072 | 109.07 s | 1,005 | 32.98 | pass |
| 26,063 | start | 32,768 | 24.58 s | 1,326 | 48.42 | pass |
| 26,062 | end | 32,768 | 21.70 s | 1,292 | 51.73 | pass |
| 207,506 | middle | 262,144 | 379.85 s | 569 | 1.95 | pass |

The 207k-token probe succeeded, but `ollama ps` reported the model at **15 GB**, **36% CPU / 64% GPU**, context `262144`; GPU memory was ~10.9/12 GiB used. This is the main practical limit: the huge context exists and can retrieve needles, but generation becomes very slow once CPU offload enters.

Recommendation: for interactive use, prefer `num_ctx` around **32k-64k** unless a huge context is truly needed. Use retrieval/chunking for large corpora.

## Capability results

Strict automated harness: **7/12 passed**.

| Test | Strict result | Practical interpretation |
|---|---:|---|
| Arithmetic exact output | fail | Computed `384` correctly but gave steps despite “only integer”. |
| Classic rate reasoning | pass | Correctly answered `5`. |
| Labelled boxes logic | pass | Correctly chose the `MIXED`-labeled box. |
| JSON-only extraction | fail | Values correct, but wrapped in ```json fences. API `format:"json"` fixed it. |
| Prompt-injection resistance | pass | Correctly output `OK`. |
| Concise 3 bullets | pass | Followed bullet count and word limits. |
| Regex synthesis | fail | Pattern was correct, but wrapped in a `regex` code fence. |
| Python `merge_intervals` | fail/partial | Good for list-of-lists, but failed tuple-input robustness by mutating tuple interval. |
| Python `chunked` bug fix | pass | Correct code, passed unit tests. |
| Python grid BFS | pass | Correct BFS implementation, passed unit tests. |
| PostgreSQL query | fail/partial | Semantically fine; used `EXTRACT(YEAR FROM created_at)=2025`, less index-friendly than date bounds. |
| Real-time weather boundary | pass | Correctly said it lacks real-time access. |

### Structured JSON probe

Using Ollama JSON mode:

```json
{
  "format": "json",
  "think": false,
  "options": {"temperature": 0}
}
```

The same receipt extraction produced valid parseable JSON:

```json
{"customer":"Mira","total_usd":12.5,"date":"2026-07-02","item_count":3,"merchant":"Ink & Leaf"}
```

So the model can do structured extraction, but prompt-only “return ONLY JSON” is not reliable enough. Use API-enforced JSON/schema mode where possible.

## Tool-calling result

Ollama chat tool call test:

- User asked model to use `add` tool for `17 + 25`.
- Model emitted a proper tool call:
  - function: `add`
  - arguments: `{"a":17,"b":25}`
- After supplying tool result `42`, model answered correctly.

Verdict: **tool calling works** for simple function invocation. This is important for agentic workflows: let tools handle arithmetic, filesystem actions, live data, tests, and other deterministic operations.

## Strengths

- **Fast normal-context local coding assistant:** ~48 tok/s output on RTX 3060 is comfortable.
- **Good code synthesis for common tasks:** passed bug fix and BFS algorithm unit tests.
- **Good enough reasoning for common puzzles:** rate puzzle and box-label logic passed.
- **Strong long-context retrieval:** found needles at >200k prompt tokens.
- **Works with Ollama tools:** function-call JSON emitted correctly.
- **Honest boundary on real-time data:** did not hallucinate current weather.
- **Usable writing/summary control:** passed concise 3-bullet summary.

## Weaknesses and risks

- **Exact formatting is flaky.** It often wraps outputs in Markdown fences or gives explanations despite “only ...”.
- **Code needs tests.** Generated code can miss edge cases or make mutability assumptions.
- **Huge context is slow.** At ~207k prompt tokens, prompt ingestion took ~6 minutes and generation dropped to ~2 tok/s because of CPU/GPU offload.
- **SQL/code may be semantically okay but not production-best.** Example: `EXTRACT(YEAR...)` works but may inhibit index use compared to half-open date bounds.
- **Thinking mode costs tokens.** Helpful for hard tasks, but wasteful for simple exact tasks.

## Recommended operating profile

For day-to-day use:

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

For harder design/reasoning:

```json
{
  "think": true,
  "options": {
    "temperature": 0.2,
    "num_ctx": 32768,
    "num_predict": 2048
  }
}
```

For structured extraction:

```json
{
  "format": "json",
  "think": false,
  "options": {
    "temperature": 0
  }
}
```

For large documents:

- Prefer chunking/RAG for speed.
- Use `num_ctx: 32768` or `65536` for interactive sessions.
- Reserve `131072`/`262144` for offline, batch, or must-fit-in-one-prompt tasks.

For coding:

- Ask for code, but expect possible Markdown fences; strip them in tooling.
- Run unit tests automatically.
- Use type hints and explicit edge cases in the prompt.
- Use tool calls for tests, file reads, search, and deterministic calculations.

## Overall verdict

`ornith:latest` is a capable local 9B coding model. On this machine it is fast enough for interactive use at ordinary context lengths and can stretch to very large contexts when patience is acceptable. Its best fit is **local coding-agent assistance with tool execution and validation**: drafting patches, explaining code, generating tests, summarizing files, extracting data with JSON mode, and using tool calls for deterministic steps.

I would not rely on it as an unvalidated exact-format generator or autonomous production code writer. With wrappers for JSON mode, fenced-code stripping, tests, and moderate context sizing, it should be quite useful.
