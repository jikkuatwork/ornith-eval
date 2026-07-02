# Modular Eval: `deep_convoluted_conversation` on `ornith:latest`

Deep, convoluted long-conversation memory with corrections, rumors, ownership transfers, and distractors.

## Summary

- Result: **11/11** (**100.0%**) 
- Total wall time: **52.7s**
- Mean/median latency: **4.79s / 5.60s**
- Max prompt tokens: **50158**
- Mean prompt ingest speed: **7715.1 tok/s**
- Mean output speed: **52.1 tok/s**

## By category

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| container_reasoning | 1 | 1 | 100.0% |
| decoy_resistance | 1 | 1 | 100.0% |
| early_story_binding | 1 | 1 | 100.0% |
| instruction_memory | 1 | 1 | 100.0% |
| late_composite | 1 | 1 | 100.0% |
| multi_attribute_update | 1 | 1 | 100.0% |
| multi_hop_relation | 1 | 1 | 100.0% |
| numeric_update | 1 | 1 | 100.0% |
| ownership_transfer | 1 | 1 | 100.0% |
| state_update | 1 | 1 | 100.0% |
| ultra_late_coreference | 1 | 1 | 100.0% |

## Per-item results

| ID | Category | Turn | Gap | Result | Wall s | Prompt tokens | Response |
|---|---|---:|---:|---:|---:|---:|---|
| `tom_ball_after_many_decoys` | early_story_binding | 150 | 148 | PASS | 7.71 | 6116 | Red. |
| `maya_key_after_correction` | state_update | 230 | 99 | PASS | 2.94 | 9417 | In the green drawer. |
| `compass_current_holder` | ownership_transfer | 260 | 47 | PASS | 1.54 | 10675 | Priya. |
| `map_owner_from_box` | container_reasoning | 330 | 53 | PASS | 2.69 | 13581 | Omar. |
| `monsoon_gate_phrase` | instruction_memory | 380 | 68 | PASS | 2.26 | 15643 | coconut lamp |
| `vault_current_code` | numeric_update | 540 | 30 | PASS | 5.60 | 22310 | 9134. |
| `archive_token_current_combo` | multi_attribute_update | 610 | 48 | PASS | 3.33 | 25237 | Hexagonal, copper, 7 grams, under the orchid pot. |
| `mentor_codeword_multihop` | multi_hop_relation | 760 | 601 | PASS | 5.83 | 31523 | Glacier. |
| `tom_animal_after_false_ox` | decoy_resistance | 930 | 928 | PASS | 6.73 | 38593 | Yellow ox. |
| `late_composite_all` | late_composite | 1030 | 1028 | PASS | 6.52 | 42786 | - **Tom's ball**: Red - **Tom's animal**: Yellow ox - **Vault code**: 9134 - **Maya's brass key**: Green drawer - **Compass holder**: Priya - **Monsoon-gate phrase**: Coconut lamp  |
| `ferry_coreference_ultralate` | ultra_late_coreference | 1200 | 1163 | PASS | 7.53 | 50158 | Dev. |
