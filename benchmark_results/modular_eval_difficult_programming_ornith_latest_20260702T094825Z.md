# Modular Eval: `difficult_programming` on `ornith:latest`

Difficult executable Python programming tasks graded by hidden-ish unit tests.

## Summary

- Result: **3/8** (**37.5%**) 
- Total wall time: **68.7s**
- Mean/median latency: **8.59s / 7.85s**
- Max prompt tokens: **121**
- Mean prompt ingest speed: **907.2 tok/s**
- Mean output speed: **45.1 tok/s**

## By category

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| data_structures | 1 | 1 | 100.0% |
| data_transform | 0 | 1 | 0.0% |
| dynamic_programming | 0 | 1 | 0.0% |
| graphs | 2 | 3 | 66.7% |
| parsing | 0 | 1 | 0.0% |
| strings | 0 | 1 | 0.0% |

## Per-item results

| ID | Category | Result | Wall s | Eval tokens | Detail |
|---|---|---:|---:|---:|---|
| `dijkstra_path_reconstruction` | graphs | PASS | 5.24 | 201 | OK |
| `expression_parser` | parsing | FAIL | 10.72 | 446 | Traceback (most recent call last):   File "/tmp/tmpf5c0c1e9/candidate.py", line 67, in <module>     assert eval_expr('2+3*4') == 14            ^^^^^^^^^^^^^^^^^^   File "/tmp/tmpf5 |
| `sliding_window_median` | data_structures | PASS | 5.17 | 195 | OK |
| `json_patch_subset` | data_transform | FAIL | 16.62 | 712 | Traceback (most recent call last):   File "/tmp/tmp_9dspt_5/candidate.py", line 90, in <module>     out = apply_patch(orig, [{'op':'replace','path':'/a/0/b','value':3}, {'op':'add' |
| `word_ladder_length` | graphs | FAIL | 6.25 | 244 | Traceback (most recent call last):   File "/tmp/tmp2yhluwfy/candidate.py", line 30, in <module>     assert word_ladder_len('hit','cog',['hot','dot','dog','lot','log','cog']) == 5 A |
| `min_window_subsequence` | strings | FAIL | 7.99 | 320 | Traceback (most recent call last):   File "/tmp/tmpkozdbja3/candidate.py", line 30, in <module>     assert min_window_subsequence('abcdebdde', 'bde') == 'bcde' AssertionError |
| `weighted_interval_scheduling` | dynamic_programming | FAIL | 7.72 | 306 | Traceback (most recent call last):   File "/tmp/tmpfrvx6tpr/candidate.py", line 35, in <module>     assert max_weight_nonoverlap([(1,3,5),(2,5,6),(4,6,5),(6,7,4),(5,8,11),(7,9,2)]) |
| `tarjan_scc` | graphs | PASS | 8.98 | 366 | OK |

## Failures

### `expression_parser`

Detail: `Traceback (most recent call last):
  File "/tmp/tmpf5c0c1e9/candidate.py", line 67, in <module>
    assert eval_expr('2+3*4') == 14
           ^^^^^^^^^^^^^^^^^^
  File "/tmp/tmpf5c0c1e9/candidate.py", line 61, in eval_expr
    result = parse_add()
             ^^^^^^^^^^^
  File "/tmp/tmpf5c0c1e9/candidate.py", line 54, in parse_add
    right = parse_mul()
            ^^^^^^^^^^^
  File "/tmp/tmpf5c0c1e9/candidate.py", line 39, in parse_mul
    while peek() in ('*', '/'):
          ^^^^^^
  File "/tmp/tmpf5c0c1e9/candidate.py", line 10, in peek
    return s[pos[0]]
           ~^^^^^^^^
IndexError: string index out of range`

```text
```python
def eval_expr(s):
    """Evaluate an integer expression with +, -, *, parentheses, unary minus."""
    s = s.strip()
    if not s:
        raise ValueError("Empty expression")

    pos = [0]  # mutable index tracker

    def peek():
        return s[pos[0]]

    def advance():
        ch = s[pos[0]]
        pos[0] += 1
        return ch

    def parse_number():
        start = pos[0]
        while pos[0] < len(s) and s[pos[0]].isdigit():
            pos[0] += 1
        if pos[0] == start:
            raise ValueError(f"Expected digit at position {start}")
        return int(s[start:pos[0]])

    def parse_unary():
        ch = peek()
        if ch == '-':
            advance()
            val = parse_unary()  # allow nested unary minus like --5
            return -val
        elif ch == '+':
            advance()
            return parse_unary()
        else:
            return parse_number()

    def parse_mul():
        left = parse_unary()
        while peek() in ('*', '/'):
            op = advance()
            right = parse_unary()
            if op == '*':
                left *= right
            elif op == '/':
                if right == 0:
                    raise ZeroDivisionError("division by zero")
                left //= right
        return left

    def parse_add():
        left = parse_mul()
        while peek() in ('+', '-'):
            op = advance()
            right = parse_mul()
            if op == '+':
                left += right
            elif op == '-':
                left -= right
        return left

    result = parse_add()
  
```

### `json_patch_subset`

Detail: `Traceback (most recent call last):
  File "/tmp/tmp_9dspt_5/candidate.py", line 90, in <module>
    out = apply_patch(orig, [{'op':'replace','path':'/a/0/b','value':3}, {'op':'add','path':'/a/1','value':{'b':4}}, {'op':'remove','path':'/x'}])
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/tmp_9dspt_5/candidate.py", line 66, in apply_patch
    _set(parent, last_key, value)
  File "/tmp/tmp_9dspt_5/candidate.py", line 49, in _set
    raise KeyError(f"Cannot set key {key!r} on non-dict")
KeyError: "Cannot set key '1' on non-dict"`

```text
```python
import copy
from typing import Any


def apply_patch(doc: Any, patch: list) -> Any:
    """Apply a JSON Patch (RFC 6902 subset: add, replace, remove) to a deep copy of *doc*.

    Supported path forms:
      - /a/b/c          → nested dict keys
      - /a/0/b          → list index then dict key
      - /a/0            → list element at index 0
      - /               → root (only for replace)

    Returns a new document; the original *doc* is never mutated.
    """
    doc = copy.deepcopy(doc)

    for op in patch:
        operation = op["op"]
        path_str = op["path"]
        value = op.get("value")

        if not path_str.startswith("/"):
            raise ValueError(f"Path must start with '/': {path_str!r}")

        parts = [p for p in path_str.split("/") if p]  # strip leading empty string

        def _resolve(parts: list) -> tuple[Any, int]:
            """Walk *parts* and return (parent, index)."""
            cur = doc
            for i, part in enumerate(parts):
                try:
                    idx = int(part)
                except ValueError:
                    if not isinstance(cur, dict):
                        raise KeyError(f"Cannot index {part!r} on non-dict")
                    cur = cur[part]
                else:
                    if not isinstance(cur, list):
                        raise IndexError(f"Index {idx} on non-list")
                    cur = cur[idx]
            return cur, len(parts)

        def _set(parent: Any, key: str | int, value: Any) -> None:
            if isinstance(key, int):
                parent[key]
```

### `word_ladder_length`

Detail: `Traceback (most recent call last):
  File "/tmp/tmp2yhluwfy/candidate.py", line 30, in <module>
    assert word_ladder_len('hit','cog',['hot','dot','dog','lot','log','cog']) == 5
AssertionError`

```text
```python
from collections import deque

def word_ladder_len(begin: str, end: str, words: list[str]) -> int:
    """Return the number of words in the shortest transformation sequence
    from `begin` to `end`, changing one letter at a time and using only
    words from `words`. Return 0 if no such sequence exists."""

    word_set = set(words)
    # BFS level-by-level; count includes both begin and end.
    queue = deque([(begin, 1)])
    visited = {begin}

    while queue:
        cur_word, depth = queue.popleft()
        if cur_word == end:
            return depth

        for i in range(len(cur_word)):
            pattern = cur_word[:i] + "?" + cur_word[i+1:]
            for candidate in word_set:
                if candidate.startswith(pattern) and candidate.endswith(pattern):
                    # Check only the character at position i differs
                    if candidate != cur_word and candidate not in visited:
                        queue.append((candidate, depth + 1))
                        visited.add(candidate)

    return 0
```
```

### `min_window_subsequence`

Detail: `Traceback (most recent call last):
  File "/tmp/tmpkozdbja3/candidate.py", line 30, in <module>
    assert min_window_subsequence('abcdebdde', 'bde') == 'bcde'
AssertionError`

```text
```python
def min_window_subsequence(s: str, t: str) -> str:
    n = len(s)
    m = len(t)
    if m == 0 or n == 0:
        return ''

    # dp[i][j] = earliest ending index in s where we've matched t[0..j-1]
    INF = float('inf')
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = -1  # sentinel: before any character

    for i in range(1, n + 1):
        for j in range(m + 1):
            if s[i-1] == t[j-1]:
                dp[i][j] = min(dp[i][j], dp[i-1][j-1])
            dp[i][j] = min(dp[i][j], dp[i-1][j])

    # Reconstruct earliest shortest window
    best_start = -INF
    for i in range(n + 1):
        if dp[i][m] != INF:
            start = dp[i][m] + 1
            length = i - start
            if length < n - best_start or (length == n - best_start and start < best_start):
                best_start = start

    return s[best_start:best_start + n - best_start] if best_start != -INF else ''
```
```

### `weighted_interval_scheduling`

Detail: `Traceback (most recent call last):
  File "/tmp/tmpfrvx6tpr/candidate.py", line 35, in <module>
    assert max_weight_nonoverlap([(1,3,5),(2,5,6),(4,6,5),(6,7,4),(5,8,11),(7,9,2)]) == 17
AssertionError`

```text
```python
def max_weight_nonoverlap(intervals):
    """Return the maximum total weight of a set of non-overlapping intervals.
    
    Each interval is (start, end, weight) and half-open [start, end).
    Uses dynamic programming after sorting by start time."""
    if not intervals:
        return 0

    # Sort by start time; break ties by end time for stability
    sorted_intervals = sorted(intervals, key=lambda x: (x[0], x[1]))

    n = len(sorted_intervals)
    dp = [0] * (n + 1)  # dp[i] = max weight using first i intervals

    for i in range(1, n + 1):
        start_i, end_i, w_i = sorted_intervals[i - 1]

        # Option 1: skip interval i
        take_skip = dp[i - 1]

        # Option 2: include interval i — find the latest j < i such that
        # sorted_intervals[j-1].end <= start_i (i.e., no overlap)
        best_prev = 0
        for j in range(i):
            if sorted_intervals[j - 1][1] <= start_i:
                best_prev = dp[j]

        take_include = w_i + best_prev

        dp[i] = max(take_skip, take_include)

    return dp[n]
```
```

