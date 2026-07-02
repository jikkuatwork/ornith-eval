# Ornith Conversational Context / Memory Eval

Target: `ornith:latest` via Ollama.

Artifacts:

- Controlled/labeled eval harness: `conversation_context_eval_ornith.py`
- Natural-language eval harness: `conversation_context_eval_natural_ornith.py`
- Controlled 340-turn run: `benchmark_results/conversation_context_eval_ornith_latest_340turns_direct_20260702T070139Z.json`
- Controlled 340-turn report: `benchmark_results/conversation_context_eval_ornith_latest_340turns_direct_20260702T070139Z.md`
- Natural 1000-turn run: `benchmark_results/conversation_context_eval_natural_ornith_latest_1000turns_direct_20260702T070429Z.json`
- Natural 1000-turn report: `benchmark_results/conversation_context_eval_natural_ornith_latest_1000turns_direct_20260702T070429Z.md`

## Executive summary

I built and ran a new conversational-context eval designed around exactly the kind of case you described: early facts like “Tom was playing with his red ball, saw a yellow ox, and went home surprised,” followed by hundreds of later chat turns, then late questions about the old details.

Result: **ornith kept context very well in these synthetic long-chat tests.**

Main natural-language stress run:

- **1000 simulated chat turns**
- **13 memory/reasoning probes**
- Max prompt size on a probe: **39,857 prompt tokens**
- Result: **13/13 passed**
- Very late probe after a **998-turn gap** correctly answered:
  - Tom ball color: `red`
  - animal/color Tom saw: `yellow ox`
  - current lab code: `7305`
  - Maya key location: `green drawer`
  - compass holder: `Priya`
  - lantern-check phrase: `violet rook`

So for the specific question “can it remember Tom’s red ball after hundreds of turns?” the answer in this eval is: **yes, consistently.**

## Methodology

I made two variants.

### 1. Controlled/labeled long-chat eval

Script: `conversation_context_eval_ornith.py`

This version explicitly labels important facts as `CANON`, corrections as `UPDATE`, and distractors as `CHATTER`, `RUMOR`, or `JOKE`.

It tests:

- early fact recall
- entity-attribute binding
- state updates
- numeric updates
- coreference
- object/container reasoning
- instruction memory
- multi-hop relation lookup
- multi-attribute recall
- late composite reasoning
- very-late consistency

### 2. Natural-language long-chat eval

Script: `conversation_context_eval_natural_ornith.py`

This version removes the explicit `CANON`/`UPDATE` labels and uses natural phrasing:

- “I want to tell you a tiny story for later…”
- “Correction about Maya…”
- “Small update…”
- “A joke during the chat…”
- “Side note…”

This is closer to a real conversation, though still synthetic.

For both versions, filler assistant replies are synthetic short acknowledgements like `OK` / `Got it.`. The model is called only at probe points. This isolates context tracking and speed from the model’s tendency to produce verbose filler replies.

Probe answers are appended to the transcript before later turns, so late probes include the model’s previous answers too.

## Main results

### Natural 1000-turn run

File: `benchmark_results/conversation_context_eval_natural_ornith_latest_1000turns_direct_20260702T070429Z.md`

| Metric | Value |
|---|---:|
| Simulated turns | 1000 |
| Probes | 13 |
| Passed | 13 |
| Accuracy | 100% |
| Total probe wall time | 43.0 s |
| Mean probe latency | 3.31 s |
| Median probe latency | 1.64 s |
| Max prompt tokens evaluated | 39,857 |
| Mean prompt ingest speed | 13,960.7 tok/s |
| Mean output speed | 54.9 tok/s |

Per-probe highlights:

| Probe | Turn | Gap from source fact | Result | Response |
|---|---:|---:|---:|---|
| Tom ball mid-chat | 70 | 68 turns | PASS | `Red.` |
| Maya key after correction | 92 | 13 turns | PASS | `In the green drawer.` |
| Current lab code | 121 | 20 turns | PASS | `7305.` |
| Current compass holder | 156 | 24 turns | PASS | `Priya.` |
| Map holder via box reasoning | 170 | 27 turns | PASS | `Omar.` |
| Lantern-check phrase | 210 | 29 turns | PASS | `violet rook` |
| Multi-hop mentor codeword | 245 | 192 turns | PASS | `glacier.` |
| Archive token attributes | 268 | 44 turns | PASS | `Hexagonal, copper, 7 grams, under the orchid pot.` |
| Late composite | 306 | 304 turns | PASS | `Red, 7305, green drawer, Priya.` |
| Tom ball very late | 340 | 338 turns | PASS | `Red.` |
| Tom surprise reason | 345 | 343 turns | PASS | `Because he saw a yellow ox far away while playing with his red ball.` |
| Tom ball ultra-late | 700 | 698 turns | PASS | `Red.` |
| Ultra-late composite | 1000 | 998 turns | PASS | `Red, yellow ox, 7305, green drawer, Priya, violet rook.` |

### Controlled 340-turn run

File: `benchmark_results/conversation_context_eval_ornith_latest_340turns_direct_20260702T070139Z.md`

| Metric | Value |
|---|---:|
| Simulated turns | 340 |
| Probes | 13 |
| Passed | 13 |
| Accuracy | 100% |
| Total probe wall time | 22.2 s |
| Mean probe latency | 1.71 s |
| Median probe latency | 1.30 s |
| P95 probe latency | 2.39 s |
| Max prompt tokens evaluated | 13,908 |
| Mean prompt ingest speed | 11,779 tok/s |
| Mean output speed | 61.8 tok/s |

Retention gap breakdown:

| Gap from fact/update to probe | Passed | Total |
|---|---:|---:|
| 0–75 turns | 8 | 8 |
| 76–150 turns | 1 | 1 |
| 151–250 turns | 1 | 1 |
| 251+ turns | 3 | 3 |

## Speed observations

Latency stayed low for short/medium chat histories and rose at very long histories.

From the 1000-turn natural run:

| Probe point | Prompt tokens | Wall time |
|---:|---:|---:|
| turn 70 | 2,771 | 6.40 s |
| turn 170 | 6,769 | 1.08 s |
| turn 306 | 12,400 | 2.05 s |
| turn 345 | 14,009 | 1.21 s |
| turn 700 | 28,068 | 10.72 s |
| turn 1000 | 39,857 | 10.72 s |

The first probe includes some cold/warmup overhead. Later large-context probes around 28k–40k tokens took about **10.7 s** each. Output was short, so most time was prompt/context handling rather than generation.

The prompt-token speeds here are faster than the standalone long-context ingestion benchmark because these probes happen sequentially with a shared growing prefix, so Ollama likely benefits from context/KV caching. For one-off fresh 40k-token prompts, expect slower behavior than this conversational cached path.

## What this eval says Ornith can do

In this setup, `ornith` can reliably:

- remember an early story detail after hundreds of turns
- bind the right attribute to the right entity despite many distractors
- keep updated mutable state, e.g. old code `4192` → current code `7305`
- follow ownership transfers, e.g. Nora → Jules → Priya
- do object/container reasoning, e.g. red box contains map; Omar has red box; therefore Omar has map
- recall an instruction phrase after long delay
- answer multi-hop relationship questions
- produce compact composite answers late in a long conversation

## Caveats

This is a useful synthetic eval, not a complete proof of robust memory in all real chats.

Important limitations:

- Filler assistant replies are synthetic short acks. The model was not asked to generate every turn of chatter.
- The eval keeps the full conversation in the prompt. It does not test external memory or summarization beyond the context window.
- The conversation is long in turns, but still only about **40k prompt tokens** in the 1000-turn run. The model advertises 262k context, but very large contexts are slower and were separately benchmarked.
- The probes are answerable from explicit text. They do not test subtle emotional inference, deception, or ambiguous human conversation at high depth.
- The answer grading is mostly value-presence based, not a human judge.

## Bottom line

For long-context conversational memory up to roughly **1000 short turns / 40k prompt tokens**, `ornith` performed very well: **13/13 on the natural stress run and 13/13 on the controlled run**.

The “Tom red ball / yellow ox” scenario worked exactly as desired, including after hundreds of distractor turns. The model also handled state updates and multi-hop conversational facts, with late-probe latency around **10–11 seconds** at ~40k prompt tokens on this machine.
