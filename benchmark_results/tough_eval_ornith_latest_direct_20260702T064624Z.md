# Tough Mixed-Domain Eval: `ornith:latest`

Mode: `think:false`

## Summary

- Overall: **19/20** passed (**95.0%**) 
- Total wall time: **188.4s**
- Mean wall time/test: **9.4s**
- Mean eval throughput: **43.5 tok/s**

## By domain

| Domain | Passed | Total | Accuracy |
|---|---:|---:|---:|
| data | 1 | 1 | 100.0% |
| logic | 2 | 2 | 100.0% |
| math | 6 | 6 | 100.0% |
| programming | 4 | 5 | 80.0% |
| science | 5 | 5 | 100.0% |
| security | 1 | 1 | 100.0% |

## Per-question results

| ID | Domain | Result | Wall s | Eval tokens | Notes |
|---|---|---:|---:|---:|---|
| `math_number_theory_crt` | math | PASS | 17.2 | 713 | values=[212.0], expected=212, best_abs_err=0.0 |
| `math_combinatorics_derangements` | math | PASS | 15.4 | 659 | values=[2464.0], expected=2464, best_abs_err=0.0 |
| `math_probability_cards` | math | PASS | 25.4 | 1060 | got_fraction='198/4165' in final, expected=198/4165 |
| `math_linear_algebra_eigenvalues` | math | PASS | 4.0 | 137 | values=[1, 3, 3], expected multiset=[1,3,3] |
| `math_calculus_integral` | math | PASS | 7.1 | 265 | got_fraction='-1/9' in final, expected=-1/9 |
| `math_bayes_medical_test` | math/statistics | PASS | 8.9 | 352 | got_fraction='1/6' in final, expected=1/6 |
| `programming_lru_cache` | programming | PASS | 3.9 | 135 | OK |
| `programming_topological_sort_cycle` | programming | PASS | 5.5 | 197 | OK |
| `programming_interval_sweep` | programming | FAIL | 4.8 | 170 | Traceback (most recent call last):   File "/tmp/tmpehyfk5kl/candidate.py", line 24, in <module>     assert min_meeting_rooms([[0,30],[5,10],[15,20]]) == 2 AssertionError |
| `programming_json_transform` | programming/data | PASS | 2.4 | 70 | OK |
| `programming_sql_window` | programming/sql | PASS | 29.0 | 1200 | checks={'select': True, 'window': True, 'lag_or_row_number': True, 'cte_or_subquery': True, 'event': True, 'date_filter': True} |
| `physics_projectile_angle` | science/physics | PASS | 20.0 | 828 | values=[11.5], expected≈11.540 deg |
| `physics_circuit_current` | science/physics | PASS | 5.4 | 212 | values=[2.0], need 2 A |
| `chemistry_buffer_ph` | science/chemistry | PASS | 3.6 | 128 | values=[5.06], expected≈5.061 |
| `biology_central_dogma_exception` | science/biology | PASS | 3.6 | 120 | missing=[] |
| `thermo_isothermal_work` | science/thermodynamics | PASS | 5.8 | 214 | values=[5743.1], expected≈5743.1 J or 5.74 kJ |
| `logic_knights_knaves` | logic | PASS | 6.3 | 239 | need A=knave, B=knight; final='A is a knave and B is a knight' |
| `logic_scheduling` | logic | PASS | 12.9 | 518 | values=[9.0], expected=9, best_abs_err=0.0 |
| `data_extraction_tricky_json` | data/instruction | PASS | 1.1 | 16 | obj={'user_id': 42, 'action': 'deploy', 'success': False}, expected={'user_id': 42, 'action': 'deploy', 'success': False} |
| `security_hashing_passwords` | security | PASS | 6.1 | 234 | salt=True, cost/memory-hard=True, rejects_plain_sha=True |

## Failures / partials

### `programming_interval_sweep` (programming)

Grader detail: `Traceback (most recent call last):
  File "/tmp/tmpehyfk5kl/candidate.py", line 24, in <module>
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

