# Natural Long-Conversation Context Eval: `ornith:latest`

Turns: **350**; probes: **11**; mode: `think:false`

## Summary

- Accuracy: **11/11** (**100.0%**)
- Total probe wall time: **18.1s**
- Mean/median probe latency: **1.65s / 1.65s**
- Max prompt tokens evaluated: **14009**
- Mean prompt ingest speed: **15979.7 tok/s**
- Mean output speed: **56.5 tok/s**

## Per-probe results

| Probe | Category | After turn | Gap | Result | Wall s | Prompt tokens | Response |
|---|---|---:|---:|---:|---:|---:|---|
| `natural_tom_ball_mid` | early_story | 70 | 68 | PASS | 2.61 | 2771 | Red. |
| `natural_key_current` | update | 92 | 13 | PASS | 1.23 | 3642 | In the green drawer. |
| `natural_code_current` | numeric_update | 121 | 20 | PASS | 1.41 | 4810 | 7305. |
| `natural_compass_holder` | ownership_transfer | 156 | 24 | PASS | 1.59 | 6223 | Priya. |
| `natural_map_holder` | object_container_reasoning | 170 | 27 | PASS | 1.07 | 6769 | Omar. |
| `natural_lantern` | instruction_memory | 210 | 29 | PASS | 1.82 | 8415 | violet rook |
| `natural_multi_hop` | multi_hop | 245 | 192 | PASS | 1.77 | 9880 | glacier. |
| `natural_archive_combo` | multi_attribute | 268 | 44 | PASS | 1.67 | 10844 | Hexagonal, copper, 7 grams, under the orchid pot. |
| `natural_composite_late` | late_composite | 306 | 304 | PASS | 2.12 | 12400 | Red, 7305, green drawer, Priya. |
| `natural_tom_ball_very_late` | very_late_consistency | 340 | 338 | PASS | 1.65 | 13794 | Red. |
| `natural_tom_surprise` | late_event_reason | 345 | 343 | PASS | 1.21 | 14009 | Because he saw a yellow ox far away while playing with his red ball. |

No failed probes.


## Method note

This version uses natural phrasing rather than explicit CANON/UPDATE labels. It still uses synthetic short assistant acknowledgements for filler turns and calls the model only at probe points.
