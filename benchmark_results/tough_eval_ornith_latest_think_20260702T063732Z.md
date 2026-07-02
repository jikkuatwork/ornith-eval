# Tough Mixed-Domain Eval: `ornith:latest`

Mode: `think:true`

## Summary

- Overall: **11/20** passed (**55.0%**) 
- Total wall time: **274.2s**
- Mean wall time/test: **13.7s**
- Mean eval throughput: **46.4 tok/s**

## By domain

| Domain | Passed | Total | Accuracy |
|---|---:|---:|---:|
| data | 0 | 1 | 0.0% |
| logic | 1 | 2 | 50.0% |
| math | 3 | 6 | 50.0% |
| programming | 2 | 5 | 40.0% |
| science | 4 | 5 | 80.0% |
| security | 1 | 1 | 100.0% |

## Per-question results

| ID | Domain | Result | Wall s | Eval tokens | Notes |
|---|---|---:|---:|---:|---|
| `math_number_theory_crt` | math | FAIL | 19.4 | 768 | no numeric answer found |
| `math_combinatorics_derangements` | math | FAIL | 12.1 | 559 | values=[2464.0], expected=1176, best_abs_err=1288.0 |
| `math_probability_cards` | math | FAIL | 21.9 | 1024 | no fraction/numeric answer; expected=198/4165 |
| `math_linear_algebra_eigenvalues` | math | PASS | 8.7 | 373 | values=[1, 3, 3], expected multiset=[1,3,3] |
| `math_calculus_integral` | math | PASS | 12.5 | 552 | got_fraction='-1/9', expected=-1/9 |
| `math_bayes_medical_test` | math/statistics | PASS | 15.0 | 659 | got_fraction='1/6', expected=1/6 |
| `programming_lru_cache` | programming | FAIL | 17.5 | 782 | Traceback (most recent call last):   File "/tmp/tmp2nxljx74/candidate.py", line 70, in <module>     assert c.get(1) == 1            ^^^^^^^^   File "/tmp/tmp2nxljx74/candidate.py", |
| `programming_topological_sort_cycle` | programming | PASS | 6.6 | 270 | OK |
| `programming_interval_sweep` | programming | FAIL | 7.9 | 325 | Traceback (most recent call last):   File "/tmp/tmp7_ktlesd/candidate.py", line 18, in <module>     assert min_meeting_rooms([[0,30],[5,10],[15,20]]) == 2 AssertionError |
| `programming_json_transform` | programming/data | PASS | 4.5 | 169 | OK |
| `programming_sql_window` | programming/sql | FAIL | 27.1 | 1200 | checks={'select': False, 'window': False, 'lag_or_row_number': False, 'cte_or_subquery': False, 'event': False, 'date_filter': False} |
| `physics_projectile_angle` | science/physics | FAIL | 23.2 | 1024 | no numeric angle |
| `physics_circuit_current` | science/physics | PASS | 10.0 | 426 | values=[2.0], need 2 A |
| `chemistry_buffer_ph` | science/chemistry | PASS | 8.9 | 370 | values=[5.06], expected≈5.061 |
| `biology_central_dogma_exception` | science/biology | PASS | 9.1 | 376 | missing=[] |
| `thermo_isothermal_work` | science/thermodynamics | PASS | 13.7 | 586 | values=[5743.0], expected≈5743.1 J or 5.74 kJ |
| `logic_knights_knaves` | logic | PASS | 15.9 | 675 | need A=knave, B=knight; final='A is a knave and B is a knight.' |
| `logic_scheduling` | logic | FAIL | 24.5 | 1024 | values=[3.0], expected=9, best_abs_err=6.0 |
| `data_extraction_tricky_json` | data/instruction | FAIL | 3.9 | 140 | obj={'user_id': '42', 'action': 'deploy', 'success': False}, expected={'user_id': 42, 'action': 'deploy', 'success': False} |
| `security_hashing_passwords` | security | PASS | 11.7 | 474 | salt=True, cost/memory-hard=True, rejects_plain_sha=True |

## Failures / partials

### `math_number_theory_crt` (math)

Grader detail: `no numeric answer found`

```text

```

### `math_combinatorics_derangements` (math)

Grader detail: `values=[2464.0], expected=1176, best_abs_err=1288.0`

```text
To count permutations of {1,…,8} with exactly 3 fixed points:

1. **Choose** which 3 positions are fixed: $\binom{8}{3} = \frac{8\cdot7\cdot6}{3\cdot2\cdot1} = 56$.
2. The remaining 5 elements must form a **derangement** (no fixed points). $D(5) = 44$ (computed via inclusion-exclusion: $5! \sum_{k=0}^5 (-1)^k/k! = 44$).

$$\text{Answer} = 56 \times 44 = 2464.$$

FINAL: 2464
```

### `math_probability_cards` (math)

Grader detail: `no fraction/numeric answer; expected=198/4165`

```text

```

### `programming_lru_cache` (programming)

Grader detail: `Traceback (most recent call last):
  File "/tmp/tmp2nxljx74/candidate.py", line 70, in <module>
    assert c.get(1) == 1
           ^^^^^^^^
  File "/tmp/tmp2nxljx74/candidate.py", line 34, in get
    self._remove(self.cache[key])
  File "/tmp/tmp2nxljx74/candidate.py", line 20, in _remove
    if node.prev:
       ^^^^^^^^^
AttributeError: 'tuple' object has no attribute 'prev'`

```text
```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> (value, prev, next)
        self.head = None  # most recently used
        self.tail = None  # least recently used

    def _add(self, node):
        """Add node right after head."""
        if self.head is None:
            self.head = self.tail = node
        else:
            node.prev = None
            node.next = self.head
            self.head.prev = node
            self.head = node

    def _remove(self, node):
        """Remove a node from the list."""
        if node.prev:
            node.prev.next = node.next
            node.next.prev = node.prev
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

    def get(self, key):
        if key not in self.cache:
            return -1
        _, prev, nxt = self.cache[key]
        self._remove(self.cache[key])
        val_node = Node(key, self.cache[key][0], None)  # rebuild with fresh node
        self._add(val_node)
        self.cache[key] = (val_node.value, val_node.prev, val_node.next)
   
... [truncated]
```

### `programming_interval_sweep` (programming)

Grader detail: `Traceback (most recent call last):
  File "/tmp/tmp7_ktlesd/candidate.py", line 18, in <module>
    assert min_meeting_rooms([[0,30],[5,10],[15,20]]) == 2
AssertionError`

```text
```python
import heapq

def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    
    rooms = []  # min-heap of end times
    for start, end in sorted(intervals):
        if rooms and rooms[0] <= start:
            heapq.heappop(rooms)
        else:
            heapq.heappush(rooms, end)
    
    return len(rooms)
```
```

### `programming_sql_window` (programming/sql)

Grader detail: `checks={'select': False, 'window': False, 'lag_or_row_number': False, 'cte_or_subquery': False, 'event': False, 'date_filter': False}`

```text

```

### `physics_projectile_angle` (science/physics)

Grader detail: `no numeric angle`

```text

```

### `logic_scheduling` (logic)

Grader detail: `values=[3.0], expected=9, best_abs_err=6.0`

```text
The critical path A→C→D has length 3+4+2 = 9, which is a lower bound regardless of parallelism. Let me verify it's achievable:

**Schedule:**
- t=0: Worker 1 starts A(3), Worker 2 starts B(2)
- t=2: Worker 2 finishes B; C still waiting for A → assign E(1) to Worker 2
- t=3: Both free; A and B
```

### `data_extraction_tricky_json` (data/instruction)

Grader detail: `obj={'user_id': '42', 'action': 'deploy', 'success': False}, expected={'user_id': 42, 'action': 'deploy', 'success': False}`

```text
{"user_id":"42","action":"deploy","success":false}
```

