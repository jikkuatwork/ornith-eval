# Modular Eval: `deep_math_puzzles` on `ornith:latest`

Deep math puzzle/problem-set suite with exact deterministic graders.

## Summary

- Result: **9/10** (**90.0%**) 
- Total wall time: **147.4s**
- Mean/median latency: **14.74s / 14.22s**
- Max prompt tokens: **145**
- Mean prompt ingest speed: **892.2 tok/s**
- Mean output speed: **46.2 tok/s**

## By category

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| algebra | 1 | 1 | 100.0% |
| combinatorics | 2 | 2 | 100.0% |
| counting | 0 | 1 | 0.0% |
| graph_theory | 1 | 1 | 100.0% |
| number_theory | 2 | 2 | 100.0% |
| probability | 2 | 2 | 100.0% |
| recurrences | 1 | 1 | 100.0% |

## Per-item results

| ID | Category | Result | Wall s | Eval tokens | Detail |
|---|---|---:|---:|---:|---|
| `catalan_lattice_paths` | combinatorics | PASS | 14.25 | 449 | values=[429.0]; expected=429.0; best_abs_err=0.0 |
| `linear_recurrence_a10` | recurrences | PASS | 10.83 | 480 | values=[60073.0]; expected=60073.0; best_abs_err=0.0 |
| `coin_until_hh` | probability | PASS | 11.07 | 479 | values=[6.0]; expected=6.0; best_abs_err=0.0 |
| `spanning_trees_complete_bipartite` | graph_theory | PASS | 3.55 | 131 | values=[432.0]; expected=432.0; best_abs_err=0.0 |
| `crt_four_constraints` | number_theory | PASS | 19.30 | 850 | values=[985.0]; expected=985.0; best_abs_err=0.0 |
| `inclusion_exclusion_divisibility` | number_theory | PASS | 14.85 | 637 | values=[200.0]; expected=200.0; best_abs_err=0.0 |
| `bayes_without_replacement_urn` | probability | PASS | 14.20 | 606 | got_fraction='1/3' in final; expected=1/3 |
| `polynomial_remainder_fibonacci` | algebra | PASS | 22.14 | 965 | missing_slots=[]; response="Let $P(x) = x^{20}$ and $D(x) = x^2 - x - 1$. We want to find $R(x)$ such that:\n\n$$x^{20} \\equiv R(x) \\pmod{x^2 - x - 1}$$\n\nSince the divisor is d |
| `digit_sum_divisible_by_7` | counting | FAIL | 25.15 | 1100 | values=[448.0, 4.0]; expected=9.0; best_abs_err=5.0 |
| `fixed_points_permutations_9` | combinatorics | PASS | 12.02 | 507 | values=[5544.0]; expected=5544.0; best_abs_err=0.0 |

## Failures

### `digit_sum_divisible_by_7`

Detail: `values=[448.0, 4.0]; expected=9.0; best_abs_err=5.0`

```text
Let me solve this step by step.

**Step 1: Find all three-digit numbers divisible by 7.**
Three-digit numbers range from 100 to 999.
- Smallest three-digit multiple of 7: ⌈100/7⌉ × 7 = 15 × 7 = 105
- Largest three-digit multiple of 7: ⌊999/7⌋ × 7 = 142 × 7 = 994

**Step 2: Find all such numbers with digit sum 12.**
I need to find n where n ≡ 0 (mod 7) and the sum of digits of n equals 12.

Let me list multiples of 7 from 105 upward and check their digit sums:

- 105: 1+0+5 = 6 ❌
- 112: 1+1+2 = 4 ❌
- 119: 1+1+9 = 11 ❌
- 126: 1+2+6 = 9 ❌
- 133: 1+3+3 = 7 ❌
- 140: 1+4+0 = 5 ❌
- 147: 1+4+7 = 12 ✅
- 154: 1+5+4 = 10 ❌
- 161: 1+6+1 = 8 ❌
- 168: 1+6+8 = 15 ❌
- 175: 1+7+5 = 13 ❌
- 182: 1+8+2 = 11 ❌
- 189: 1+8+9 = 18 ❌
- 196: 1+9+6 = 16 ❌
- 203: 2+0+3 = 5 ❌
- 210: 2+1+0 = 3 ❌
- 217: 2+1+7 = 10 ❌
- 224: 2+2+4 = 8 ❌
- 231: 2+3+1 = 6 ❌
- 238: 2+3+8 = 13 ❌
- 245: 2+4+5 = 11 ❌
- 252: 2+5+2 = 9 ❌
- 259: 2+5+9 = 16 ❌
- 266: 2+6+6 = 14 ❌
- 273: 2+7+3 = 12 ✅
- 280: 2+8+0 = 10 ❌
- 287: 2+8+7 = 17 ❌
- 294: 2+9+4 = 15 ❌
- 301: 3+0+1 = 4 ❌
- 308: 3+0+8 = 11 ❌
- 315: 3+1+5 = 9 ❌
- 322: 3+2+2 = 7 ❌
- 329: 3+2+9 = 14 ❌
- 336: 3+3+6 = 12 ✅
- 343: 3+4+3 = 10 ❌
- 350: 3+5+0 = 8 ❌
- 357: 3+5+7 = 15 ❌
- 364: 3+6+4 = 13 ❌
- 371: 3+7+1 = 11 ❌
- 378: 3+7+8 = 18 ❌
- 385: 3+8+5 = 16 ❌
- 392: 3+9+2 = 14 ❌
- 399: 3+9+9 = 21 ❌
- 406: 4+0+6 = 10 ❌
- 413: 4+1+3 = 8 ❌
- 420: 4+2+0 = 6 ❌
- 427: 4+2+7 = 13 ❌
- 434: 4+3+4 = 11 ❌
- 441: 4+4+1 = 9 ❌
- 448: 4+
```

