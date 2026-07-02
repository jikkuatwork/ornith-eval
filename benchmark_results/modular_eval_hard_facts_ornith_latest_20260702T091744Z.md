# Modular Eval: `hard_facts` on `ornith:latest`

Hard factual recall across computing, science, history, and systems.

## Summary

- Result: **3/3** (**100.0%**) 
- Total wall time: **7.7s**
- Mean/median latency: **2.56s / 0.86s**
- Max prompt tokens: **104**
- Mean prompt ingest speed: **812.5 tok/s**
- Mean output speed: **57.3 tok/s**

## By category

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| networking | 1 | 1 | 100.0% |
| systems | 1 | 1 | 100.0% |
| web | 1 | 1 | 100.0% |

## Per-item results

| ID | Category | Result | Wall s | Eval tokens | Detail |
|---|---|---:|---:|---:|---|
| `sysv_abi_registers` | systems | PASS | 6.07 | 63 | missing_slots=[]; response='The x86-64 System V ABI defines the first six general-purpose registers used for passing integer or pointer arguments as rdi, rsi, rdx, rcx, r8, and r9. |
| `ipv6_loopback` | networking | PASS | 0.86 | 3 | missing=[]; response='::1' |
| `http_429` | web | PASS | 0.76 | 4 | values=[429.0]; expected=429.0; best_abs_err=0.0 |
