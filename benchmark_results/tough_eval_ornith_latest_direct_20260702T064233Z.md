# Tough Mixed-Domain Eval: `ornith:latest`

Mode: `think:false`

## Summary

- Overall: **17/20** passed (**85.0%**) 
- Total wall time: **183.1s**
- Mean wall time/test: **9.2s**
- Mean eval throughput: **44.6 tok/s**

## By domain

| Domain | Passed | Total | Accuracy |
|---|---:|---:|---:|
| data | 1 | 1 | 100.0% |
| logic | 2 | 2 | 100.0% |
| math | 4 | 6 | 66.7% |
| programming | 4 | 5 | 80.0% |
| science | 5 | 5 | 100.0% |
| security | 1 | 1 | 100.0% |

## Per-question results

| ID | Domain | Result | Wall s | Eval tokens | Notes |
|---|---|---:|---:|---:|---|
| `math_number_theory_crt` | math | PASS | 15.9 | 713 | values=[212.0], expected=212, best_abs_err=0.0 |
| `math_combinatorics_derangements` | math | FAIL | 15.4 | 659 | values=[2464.0], expected=1176, best_abs_err=1288.0 |
| `math_probability_cards` | math | FAIL | 24.1 | 1024 | values=[123552.0, 48.0, 13.0, 123552.0, 624.0, 198.0], expected=0.0475390156062425 |
| `math_linear_algebra_eigenvalues` | math | PASS | 4.0 | 137 | values=[1, 3, 3], expected multiset=[1,3,3] |
| `math_calculus_integral` | math | PASS | 6.7 | 265 | got_fraction='-1/9', expected=-1/9 |
| `math_bayes_medical_test` | math/statistics | PASS | 8.8 | 352 | got_fraction='1/6', expected=1/6 |
| `programming_lru_cache` | programming | PASS | 3.8 | 135 | OK |
| `programming_topological_sort_cycle` | programming | PASS | 5.2 | 197 | OK |
| `programming_interval_sweep` | programming | FAIL | 4.7 | 170 | Traceback (most recent call last):   File "/tmp/tmp9yrtmmiz/candidate.py", line 24, in <module>     assert min_meeting_rooms([[0,30],[5,10],[15,20]]) == 2 AssertionError |
| `programming_json_transform` | programming/data | PASS | 2.4 | 70 | OK |
| `programming_sql_window` | programming/sql | PASS | 28.3 | 1200 | checks={'select': True, 'window': True, 'lag_or_row_number': True, 'cte_or_subquery': True, 'event': True, 'date_filter': True} |
| `physics_projectile_angle` | science/physics | PASS | 19.6 | 828 | values=[11.5], expected≈11.540 deg |
| `physics_circuit_current` | science/physics | PASS | 5.7 | 212 | values=[2.0], need 2 A |
| `chemistry_buffer_ph` | science/chemistry | PASS | 3.6 | 128 | values=[5.06], expected≈5.061 |
| `biology_central_dogma_exception` | science/biology | PASS | 3.4 | 120 | missing=[] |
| `thermo_isothermal_work` | science/thermodynamics | PASS | 5.5 | 214 | values=[5743.1], expected≈5743.1 J or 5.74 kJ |
| `logic_knights_knaves` | logic | PASS | 6.0 | 239 | need A=knave, B=knight; final='A is a knave and B is a knight' |
| `logic_scheduling` | logic | PASS | 12.6 | 518 | values=[9.0], expected=9, best_abs_err=0.0 |
| `data_extraction_tricky_json` | data/instruction | PASS | 1.1 | 16 | obj={'user_id': 42, 'action': 'deploy', 'success': False}, expected={'user_id': 42, 'action': 'deploy', 'success': False} |
| `security_hashing_passwords` | security | PASS | 6.3 | 234 | salt=True, cost/memory-hard=True, rejects_plain_sha=True |

## Failures / partials

### `math_combinatorics_derangements` (math)

Grader detail: `values=[2464.0], expected=1176, best_abs_err=1288.0`

```text
**Step-by-step derivation:**

We want the number of permutations of $\{1,2,\dots,8\}$ that fix exactly $3$ elements.

1. **Choose which 3 are fixed.**  
   $\binom{8}{3} = \frac{8 \cdot 7 \cdot 6}{3 \cdot 2 \cdot 1} = 56$.

2. **The remaining 5 must have *no* fixed points** (a derangement of 5 elements).  
   The number of derangements $D_n$ satisfies:
   $$D_n = n! \sum_{k=0}^{n} \frac{(-1)^k}{k!}$$

   For $n=5$:
   - $D_5 = 5! \left(\frac{1}{0!} - \frac{1}{1!} + \frac{1}{2!} - \frac{1}{3!} + \frac{1}{4!} - \frac{1}{5!}\right)$
   - $= 120 \left(1 - 1 + \frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120}\right)$
   - $= 120 \cdot \left(\frac{1}{2} - \frac{1}{6} + \frac{1}{24} - \frac{1}{120}\right)$

   Compute the sum:
   - $\frac{1}{2} = \frac{60}{120}$
   - $-\frac{1}{6} = -\frac{20}{120}$
   - $\frac{1}{24} = \frac{5}{120}$
   - $-\frac{1}{120} = -\frac{1}{120}$

   Sum: $\frac{60 - 20 + 5 - 1}{120} = \frac{44}{120}$

   So $D_5 = 120 \cdot \frac{44}{120} = 44$.

3. **Total permutations with exactly 3 fixed points:**
   $$\binom{8}{3} \times D_5 = 56 \times 44$$

   $56 \times 44$:
   - $56 \times 40 = 2240$
   - $56 \times 4 = 224$
   - Total: $2240 + 224 = 2464$

**Ver
... [truncated]
```

### `math_probability_cards` (math)

Grader detail: `values=[123552.0, 48.0, 13.0, 123552.0, 624.0, 198.0], expected=0.0475390156062425`

```text
**Step-by-step derivation:**

1. **Total number of 5-card hands**:  
   \[
   \binom{52}{5} = \frac{52 \times 51 \times 50 \times 49 \times 48}{5 \times 4 \times 3 \times 2 \times 1} = 2,598,960
   \]

2. **Number of hands with exactly two pairs**:  
   - Choose the 2 ranks for the pairs: \(\binom{13}{2}\) ways.  
   - For each pair rank, choose 2 suits from 4: \(\binom{4}{2} = 6\) ways per pair → \(6^2 = 36\).  
   - Choose the 5th card (must not form a third pair or three-of-a-kind):  
     - It must be of a different rank than either pair. There are \(13 - 2 = 11\) eligible ranks.  
     - For each such rank, any of the 4 suits works → 4 choices.  
   - So: \(\binom{13}{2} \times 6^2 \times 11 \times 4\).

   Calculation:
   \[
   \binom{13}{2} = 78,\quad 78 \times 36 = 2,808,\quad 2,808 \times 44 = 123,552
   \]

3. **Probability**:  
   \[
   P = \frac{123,552}{2,598,960}
   \]

   Simplify: divide numerator and denominator by 48 → \(2,574 / 54,145\). Then by 3 → \(858 / 18,048.3...\) — let's do it properly via GCD.

   Actually, compute GCD(123552, 2598960):
   - Both divisible by 48?  
     \(123552 ÷ 48 = 2574\), \(2598960 ÷ 48 = 54145\).  
   - GCD(2574, 54145):  
     \(5
... [truncated]
```

### `programming_interval_sweep` (programming)

Grader detail: `Traceback (most recent call last):
  File "/tmp/tmp9yrtmmiz/candidate.py", line 24, in <module>
    assert min_meeting_rooms([[0,30],[5,10],[15,20]]) == 2
AssertionError`

```text
```python
def min_meeting_rooms(intervals):
    """Return the minimum number of meeting rooms needed for a list of half-open intervals [start, end)."""
    if not intervals:
        return 0

    starts = sorted(s for s, _ in intervals)
    ends = sorted(e for _, e in intervals)

    room_count = 1
    end_idx = 1

    for i in range(1, len(starts)):
        if starts[i] < ends[end_idx]:
            # A new meeting starts before the earliest current one ends → need another room
            room_count += 1
        else:
            # The earliest ongoing meeting has ended (or finishes exactly when this one starts)
            end_idx += 1

    return room_count
```
```

