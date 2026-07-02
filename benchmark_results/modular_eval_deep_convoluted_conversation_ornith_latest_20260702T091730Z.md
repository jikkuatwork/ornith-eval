# Modular Eval: `deep_convoluted_conversation` on `ornith:latest`

Deep, convoluted long-conversation memory with corrections, rumors, ownership transfers, and distractors.

## Summary

- Result: **2/2** (**100.0%**) 
- Total wall time: **11.4s**
- Mean/median latency: **5.68s / 5.68s**
- Max prompt tokens: **9417**
- Mean prompt ingest speed: **2948.6 tok/s**
- Mean output speed: **57.0 tok/s**

## By category

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| early_story_binding | 1 | 1 | 100.0% |
| state_update | 1 | 1 | 100.0% |

## Per-item results

| ID | Category | Turn | Gap | Result | Wall s | Prompt tokens | Response |
|---|---|---:|---:|---:|---:|---:|---|
| `tom_ball_after_many_decoys` | early_story_binding | 150 | 148 | PASS | 8.44 | 6116 | Red. |
| `maya_key_after_correction` | state_update | 230 | 99 | PASS | 2.92 | 9417 | In the green drawer. |
