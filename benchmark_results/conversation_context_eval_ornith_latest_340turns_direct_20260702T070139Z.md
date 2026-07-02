# Long Conversational Context Eval: `ornith:latest`

Mode: `think:false`; simulated turns: **340**; probes: **13**

## Summary

- Accuracy: **13/13** (**100.0%**) 
- Total probe wall time: **22.2s**
- Mean / median probe latency: **1.71s / 1.30s**
- P95 probe latency: **2.39s**
- Max prompt tokens evaluated on a probe: **13908**
- Mean prompt ingest speed: **11779.0 tok/s**
- Mean output speed: **61.8 tok/s**

## Results by retention gap

| Gap from fact/update to probe | Passed | Total |
|---|---:|---:|
| 0-75 turns | 8 | 8 |
| 76-150 turns | 1 | 1 |
| 151-250 turns | 1 | 1 |
| 251+ turns | 3 | 3 |

## Per-probe results

| Probe | Category | After turn | Gap | Result | Wall s | Prompt tokens | Eval tokens | Response |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `tom_ball_mid` | early_fact_recall | 55 | 52 | PASS | 6.60 | 2319 | 2 | Red |
| `tom_ox_mid` | entity_attribute_binding | 75 | 72 | PASS | 1.06 | 3154 | 3 | Yellow ox |
| `key_after_update` | state_update | 90 | 8 | PASS | 0.84 | 3783 | 3 | Green drawer |
| `train_coreference` | coreference | 104 | 86 | PASS | 0.83 | 4380 | 3 | Priya |
| `cabinet_code_current` | state_update_numeric | 118 | 10 | PASS | 0.90 | 5009 | 5 | 7305 |
| `compass_current_holder` | state_update_entity | 150 | 26 | PASS | 1.27 | 6264 | 3 | Priya |
| `map_holder_box_reasoning` | multi_step_object_reasoning | 176 | 39 | PASS | 1.16 | 7338 | 3 | Omar |
| `lantern_instruction` | instruction_memory | 205 | 36 | PASS | 1.30 | 8501 | 5 | Violet rook |
| `multi_hop_codeword` | multi_hop_relation | 235 | 177 | PASS | 1.31 | 9741 | 3 | Glacier |
| `archive_token_combo` | multi_attribute_recall | 255 | 44 | PASS | 1.39 | 10575 | 15 | Hexagonal, copper, 7 grams, under the orchid pot |
| `composite_late_json` | late_composite_reasoning | 285 | 282 | PASS | 2.39 | 11814 | 50 | ```json {   "ball_color": "red",   "current_code": "7305",   "key_location": "green drawer",   "compass_holder": "Priya" } ``` |
| `tom_ball_very_late_consistency` | very_late_consistency | 320 | 317 | PASS | 1.67 | 13284 | 2 | Red |
| `tom_surprise_late` | late_event_reason | 335 | 332 | PASS | 1.53 | 13908 | 16 | Because he saw a yellow ox far away while playing with his red ball. |

No failed probes.

## Notes

This eval uses synthetic assistant `OK` replies for filler turns and calls the model only for probe questions. That isolates long-conversation context tracking from the model's tendency to produce verbose filler replies. Probe answers are appended to the conversation before later turns, so late consistency can be affected by the model's own earlier answers.
