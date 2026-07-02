# Modular Eval: `hard_facts` on `ornith:latest`

Hard factual recall across computing, science, history, and systems.

## Summary

- Result: **12/12** (**100.0%**) 
- Total wall time: **32.2s**
- Mean/median latency: **2.68s / 2.26s**
- Max prompt tokens: **104**
- Mean prompt ingest speed: **779.7 tok/s**
- Mean output speed: **50.2 tok/s**

## By category

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| biology | 2 | 2 | 100.0% |
| databases | 1 | 1 | 100.0% |
| distributed_systems | 1 | 1 | 100.0% |
| history | 1 | 1 | 100.0% |
| logic | 1 | 1 | 100.0% |
| networking | 2 | 2 | 100.0% |
| physics | 1 | 1 | 100.0% |
| systems | 1 | 1 | 100.0% |
| unicode | 1 | 1 | 100.0% |
| web | 1 | 1 | 100.0% |

## Per-item results

| ID | Category | Result | Wall s | Eval tokens | Detail |
|---|---|---:|---:|---:|---|
| `sysv_abi_registers` | systems | PASS | 2.17 | 63 | missing_slots=[]; response='The x86-64 System V ABI defines the first six general-purpose registers used for passing integer or pointer arguments as rdi, rsi, rdx, rcx, r8, and r9. |
| `ipv6_loopback` | networking | PASS | 0.85 | 3 | missing=[]; response='::1' |
| `http_429` | web | PASS | 0.81 | 4 | values=[429.0]; expected=429.0; best_abs_err=0.0 |
| `unicode_replacement_char` | unicode | PASS | 0.77 | 5 | missing=[]; response='U+FFFD' |
| `godel_second` | logic | PASS | 2.35 | 74 | missing=[]; response="**Gödel's Second Incompleteness Theorem.**\n\nIt states that if a sufficiently strong, consistent formal system (like Peano Arithmetic) is capable of expressi |
| `cap_theorem` | distributed_systems | PASS | 3.60 | 129 | missing_slots=[]; response='In the **CAP theorem**, the three letters stand for:\n\n- **C** — **Consistency**: Every read receives the most recent write or an error. All nodes see  |
| `p53_role` | biology | PASS | 3.78 | 136 | missing=[]; response='p53 is best known as **"the guardian of the genome."** It is a tumor suppressor protein that plays a central role in preventing cancer by:\n\n- **Monitoring D |
| `crispr_cas9_cut` | biology | PASS | 3.39 | 119 | hits=['guide RNA', 'gRNA', 'sgRNA']; expected_any=['guide RNA', 'gRNA', 'sgRNA', 'RNA guide']; response='The molecule that guides Cas9 to the target sequence in CRISPR-Cas9 editing |
| `postgres_mvcc_columns` | databases | PASS | 8.63 | 350 | missing_slots=[]; response='The PostgreSQL system columns commonly associated with tuple MVCC (Multi-Version Concurrency Control) transaction visibility are:\n\n1. **`ctid`** — Phy |
| `apollo11_landing` | history | PASS | 1.80 | 46 | missing_slots=[]; response='Apollo 11 landed on the Moon on **July 20, 1969** (UTC). The lunar module *Eagle* touched down at approximately 20:17 UTC that day.' |
| `tcp_teardown_flag` | networking | PASS | 2.42 | 76 | missing=[]; response='The **FIN** (Finish) flag is used to request a graceful connection teardown in TCP. When one side sends a segment with the FIN flag set, it indicates that it  |
| `relativity_mercury` | physics | PASS | 1.62 | 37 | missing=[]; response="Mercury. Einstein's general relativity accounted for the ~43 arcseconds per century discrepancy in Mercury's perihelion precession that Newtonian mechanics co |
