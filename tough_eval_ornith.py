#!/usr/bin/env python3
"""Tough mixed-domain eval for an Ollama model.

Default: ornith:latest at http://127.0.0.1:11434.
Writes JSON and Markdown reports under ./benchmark_results/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import statistics
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Any, Callable

import requests


def ns_to_s(v: int | float | None) -> float | None:
    return None if v is None else float(v) / 1_000_000_000.0


def tps(count: int | None, duration_ns: int | None) -> float | None:
    if not count or not duration_ns:
        return None
    s = duration_ns / 1_000_000_000.0
    return count / s if s > 0 else None


class Ollama:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.s = requests.Session()

    def generate(self, prompt: str, *, think: bool, num_predict: int, num_ctx: int = 8192, timeout: int = 600) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": think,
            "keep_alive": "10m",
            "options": {
                "temperature": 0,
                "seed": 123,
                "num_predict": num_predict,
                "num_ctx": num_ctx,
            },
        }
        start = time.perf_counter()
        r = self.s.post(f"{self.base_url}/api/generate", json=payload, timeout=timeout)
        wall = time.perf_counter() - start
        try:
            out = r.json()
        except Exception:
            out = {"raw_text": r.text}
        out["http_status"] = r.status_code
        out["wall_s"] = wall
        out["perf"] = {
            "load_s": ns_to_s(out.get("load_duration")),
            "prompt_eval_s": ns_to_s(out.get("prompt_eval_duration")),
            "eval_s": ns_to_s(out.get("eval_duration")),
            "total_s_reported": ns_to_s(out.get("total_duration")),
            "prompt_tps": tps(out.get("prompt_eval_count"), out.get("prompt_eval_duration")),
            "eval_tps": tps(out.get("eval_count"), out.get("eval_duration")),
        }
        return out


def last_final(text: str) -> str:
    matches = re.findall(r"FINAL\s*:\s*(.+)", text, flags=re.I)
    if matches:
        return matches[-1].strip()
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    return lines[-1] if lines else text.strip()


def strip_md(s: str) -> str:
    return s.strip().strip("` ")


def numbers(s: str) -> list[float]:
    return [float(x) for x in re.findall(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", s.replace(",", ""))]


def exact_text(expected: str, *, case: bool = False) -> Callable[[str], tuple[float, str]]:
    def check(resp: str) -> tuple[float, str]:
        got = strip_md(last_final(resp)).strip(". ")
        a = got if case else got.lower()
        b = expected if case else expected.lower()
        return (1.0 if a == b else 0.0, f"got={got!r}, expected={expected!r}")
    return check


def contains_all(*terms: str) -> Callable[[str], tuple[float, str]]:
    def check(resp: str) -> tuple[float, str]:
        text = resp.lower()
        missing = [t for t in terms if t.lower() not in text]
        return (1.0 if not missing else 0.0, f"missing={missing}")
    return check


def numeric_answer(expected: float, tol: float = 1e-6, *, use_final: bool = True) -> Callable[[str], tuple[float, str]]:
    def check(resp: str) -> tuple[float, str]:
        target = last_final(resp) if use_final else resp
        vals = numbers(target)
        if not vals:
            vals = numbers(resp)
        if not vals:
            return 0.0, "no numeric answer found"
        # accept any number in final/response within tolerance; this is forgiving for explanations.
        best = min(abs(v - expected) for v in vals)
        ok = best <= tol
        return (1.0 if ok else 0.0, f"values={vals[:8]}, expected={expected}, best_abs_err={best}")
    return check


def fraction_answer(num: int, den: int) -> Callable[[str], tuple[float, str]]:
    expected = num / den
    def check(resp: str) -> tuple[float, str]:
        # Prefer the requested FINAL line, but scan the whole response too because
        # verbose models may state the correct reduced fraction before truncating.
        final = last_final(resp)
        for scope_name, scope in [("final", final), ("response", resp)]:
            for m in re.finditer(r"(-?\d+)\s*/\s*(-?\d+)", scope):
                d = int(m.group(2))
                if d == 0:
                    continue
                got = int(m.group(1)) / d
                if abs(got - expected) < 1e-12:
                    return 1.0, f"got_fraction={m.group(0)!r} in {scope_name}, expected={num}/{den}"
        vals = numbers(final) or numbers(resp)
        if vals:
            best = min(abs(v - expected) for v in vals)
            return (1.0 if best < 1e-9 else 0.0, f"values={vals[:8]}, expected={expected}")
        return 0.0, f"no fraction/numeric answer; expected={num}/{den}"
    return check


def set_answer(expected: set[str]) -> Callable[[str], tuple[float, str]]:
    def check(resp: str) -> tuple[float, str]:
        s = last_final(resp).lower()
        found = set(re.findall(r"[a-z0-9_+-]+", s))
        missing = {x.lower() for x in expected} - found
        return (1.0 if not missing else 0.0, f"found={sorted(found)}, missing={sorted(missing)}")
    return check


def json_check(expected: dict[str, Any]) -> Callable[[str], tuple[float, str]]:
    def check(resp: str) -> tuple[float, str]:
        txt = resp.strip()
        m = re.search(r"```(?:json)?\s*(.*?)```", txt, re.S | re.I)
        if m:
            txt = m.group(1).strip()
        # prefer object substring
        if not txt.startswith("{"):
            m2 = re.search(r"\{.*\}", txt, re.S)
            if m2:
                txt = m2.group(0)
        try:
            obj = json.loads(txt)
        except Exception as e:
            return 0.0, f"json parse failed: {e}; text={txt[:200]!r}"
        ok = obj == expected
        return (1.0 if ok else 0.0, f"obj={obj!r}, expected={expected!r}")
    return check


def extract_code(resp: str) -> str:
    m = re.search(r"```(?:python|py)\s*(.*?)```", resp, re.S | re.I)
    if not m:
        m = re.search(r"```\s*(.*?)```", resp, re.S)
    code = m.group(1) if m else resp
    code = re.sub(r"^\s*python\s*", "", code.strip(), flags=re.I)
    return code.strip()


def run_python_candidate(code: str, tests: str, timeout: int = 6) -> tuple[bool, str]:
    program = code + "\n\n" + tests + "\nprint('OK')\n"
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "candidate.py"
        path.write_text(program)
        try:
            r = subprocess.run([sys.executable, str(path)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "timeout"
    if r.returncode == 0 and "OK" in r.stdout:
        return True, r.stdout.strip()
    return False, (r.stderr or r.stdout).strip()[-2000:]


def code_check(fn_name: str, tests: str, timeout: int = 6) -> Callable[[str], tuple[float, str]]:
    def check(resp: str) -> tuple[float, str]:
        code = extract_code(resp)
        if fn_name not in code:
            return 0.0, f"{fn_name} not found in code excerpt={code[:200]!r}"
        ok, detail = run_python_candidate(code, tests, timeout=timeout)
        return (1.0 if ok else 0.0, detail)
    return check


def sql_window_check(resp: str) -> tuple[float, str]:
    s = resp.lower()
    checks = {
        "select": "select" in s,
        "window": "over" in s and "partition by" in s,
        "lag_or_row_number": "lag(" in s or "row_number(" in s,
        "cte_or_subquery": "with" in s or "from (" in s,
        "event": "events" in s,
        "date_filter": "2025" in s,
    }
    return (1.0 if all(checks.values()) else 0.0, f"checks={checks}")


def physics_projectile_check(resp: str) -> tuple[float, str]:
    # Need theta ~= 5.88 degrees for v=50m/s, x=100m, same height, g=9.8, lower angle.
    vals = numbers(last_final(resp)) or numbers(resp)
    if not vals:
        return 0.0, "no numeric angle"
    expected = 0.5 * math.degrees(math.asin(9.8 * 100 / (50 * 50)))
    best = min(abs(v - expected) for v in vals)
    return (1.0 if best < 0.25 else 0.0, f"values={vals[:8]}, expected≈{expected:.3f} deg")


def circuit_check(resp: str) -> tuple[float, str]:
    # 6Ω || 3Ω = 2Ω, +4Ω = 6Ω, I=2A for 12V.
    vals = numbers(last_final(resp)) or numbers(resp)
    low = resp.lower()
    ok_current = any(abs(v - 2.0) < 1e-6 for v in vals)
    ok_unit = "a" in low or "amp" in low
    return (1.0 if ok_current and ok_unit else 0.0, f"values={vals[:8]}, need 2 A")


def chemistry_check(resp: str) -> tuple[float, str]:
    # pH = pKa + log(A-/HA) = 4.76 + log10(0.2/0.1)=5.061
    vals = numbers(last_final(resp)) or numbers(resp)
    expected = 4.76 + math.log10(2)
    best = min((abs(v - expected) for v in vals), default=999)
    return (1.0 if best < 0.03 else 0.0, f"values={vals[:8]}, expected≈{expected:.3f}")


def bayes_check(resp: str) -> tuple[float, str]:
    # prevalence .01, sens .99, spec .95 => .0099/(.0099+.0495)=1/6
    return fraction_answer(1, 6)(resp)


def eigen_multiset_check(resp: str) -> tuple[float, str]:
    s = last_final(resp)
    vals = [int(round(v)) for v in numbers(s)]
    if not vals:
        vals = [int(round(v)) for v in numbers(resp)]
    ok = sorted(vals) == [1, 3, 3]
    return (1.0 if ok else 0.0, f"values={vals}, expected multiset=[1,3,3]")


def knights_knaves_check(resp: str) -> tuple[float, str]:
    text = resp.lower()
    a_knave = bool(re.search(r"a\s*(?:is|=|:)\s*(?:a\s*)?knave|a\s+knave", text))
    b_knight = bool(re.search(r"b\s*(?:is|=|:)\s*(?:a\s*)?knight|b\s+knight", text))
    # Also accept compact forms like "A: knave; B: knight".
    final = last_final(resp).lower()
    a_knave = a_knave or ("a:" in final and "knave" in final.split("b")[0])
    b_knight = b_knight or ("b:" in final and "knight" in final.split("b:")[-1])
    return (1.0 if a_knave and b_knight else 0.0, f"need A=knave, B=knight; final={last_final(resp)!r}")


def thermodynamics_check(resp: str) -> tuple[float, str]:
    expected_j = 8.314 * 300 * math.log(10)
    text = last_final(resp).lower()
    vals = numbers(text) or numbers(resp)
    candidates = vals[:]
    if "kj" in text or "kiloj" in text:
        candidates += [v * 1000 for v in vals]
    best = min((abs(v - expected_j) for v in candidates), default=999999)
    return (1.0 if best < 30 else 0.0, f"values={vals[:8]}, expected≈{expected_j:.1f} J or {expected_j/1000:.2f} kJ")


def security_password_check(resp: str) -> tuple[float, str]:
    text = resp.lower()
    has_salt = "salt" in text
    has_cost = any(x in text for x in ["slow", "adaptive", "memory-hard", "memory hard", "work factor", "cost", "key stretching", "argon2", "bcrypt", "scrypt", "pbkdf2"])
    rejects_plain_sha = any(x in text for x in ["not adequate", "inadequate", "no", "not enough", "not sufficient", "should not"])
    return (1.0 if has_salt and has_cost and rejects_plain_sha else 0.0, f"salt={has_salt}, cost/memory-hard={has_cost}, rejects_plain_sha={rejects_plain_sha}")


def make_tests() -> list[dict[str, Any]]:
    # Prompts request a final line to simplify grading, but explanations are allowed.
    common = "Solve carefully. End with a separate line exactly like 'FINAL: <answer>'."
    return [
        # Math / stats
        {
            "id": "math_number_theory_crt",
            "domain": "math",
            "prompt": f"{common}\nFind the smallest nonnegative integer x such that x ≡ 2 mod 7, x ≡ 3 mod 11, and x ≡ 4 mod 13.",
            "checker": numeric_answer(212),
            "num_predict": 768,
        },
        {
            "id": "math_combinatorics_derangements",
            "domain": "math",
            "prompt": f"{common}\nHow many permutations of 1..8 have exactly 3 fixed points?",
            "checker": numeric_answer(2464),
            "num_predict": 768,
        },
        {
            "id": "math_probability_cards",
            "domain": "math",
            "prompt": f"{common}\nA 5-card poker hand is dealt from a standard 52-card deck. What is the probability it contains exactly two pairs? Give the exact reduced fraction.",
            "checker": fraction_answer(198, 4165),
            "num_predict": 1400,
        },
        {
            "id": "math_linear_algebra_eigenvalues",
            "domain": "math",
            "prompt": f"{common}\nWhat are the eigenvalues of the matrix [[2,1,0],[1,2,0],[0,0,3]]? Return them as a multiset.",
            "checker": eigen_multiset_check,
            "num_predict": 1024,
        },
        {
            "id": "math_calculus_integral",
            "domain": "math",
            "prompt": f"{common}\nEvaluate the definite integral from 0 to 1 of x^2 * ln(x) dx.",
            "checker": fraction_answer(-1, 9),
            "num_predict": 768,
        },
        {
            "id": "math_bayes_medical_test",
            "domain": "math/statistics",
            "prompt": f"{common}\nA disease has prevalence 1%. A test has sensitivity 99% and specificity 95%. If a person tests positive, what is P(disease | positive)? Give the exact fraction and approximate percent.",
            "checker": bayes_check,
            "num_predict": 1024,
        },
        # Programming / CS
        {
            "id": "programming_lru_cache",
            "domain": "programming",
            "prompt": "Return only Python code. Implement class LRUCache with __init__(capacity), get(key)->value or -1, and put(key,value). Both operations should be O(1).",
            "checker": code_check("LRUCache", r'''
c = LRUCache(2)
c.put(1, 1)
c.put(2, 2)
assert c.get(1) == 1
c.put(3, 3)
assert c.get(2) == -1
c.put(4, 4)
assert c.get(1) == -1
assert c.get(3) == 3
assert c.get(4) == 4
c.put(4, 40)
assert c.get(4) == 40
'''),
            "num_predict": 1400,
        },
        {
            "id": "programming_topological_sort_cycle",
            "domain": "programming",
            "prompt": "Return only Python code. Define topo_order(n, edges) where nodes are 0..n-1 and edges are (u,v) meaning u before v. Return a valid topological ordering list, or None if there is a cycle.",
            "checker": code_check("topo_order", r'''
def valid(order, n, edges):
    if order is None or len(order) != n or set(order) != set(range(n)):
        return False
    pos = {x:i for i,x in enumerate(order)}
    return all(pos[u] < pos[v] for u,v in edges)
assert valid(topo_order(4, [(0,1),(0,2),(1,3),(2,3)]), 4, [(0,1),(0,2),(1,3),(2,3)])
assert topo_order(3, [(0,1),(1,2),(2,0)]) is None
assert valid(topo_order(1, []), 1, [])
'''),
            "num_predict": 1400,
        },
        {
            "id": "programming_interval_sweep",
            "domain": "programming",
            "prompt": "Return only Python code. Define min_meeting_rooms(intervals) for half-open intervals [start,end). Return the minimum number of rooms required. Handle empty input and simultaneous end/start correctly.",
            "checker": code_check("min_meeting_rooms", r'''
assert min_meeting_rooms([]) == 0
assert min_meeting_rooms([[0,30],[5,10],[15,20]]) == 2
assert min_meeting_rooms([[7,10],[2,4]]) == 1
assert min_meeting_rooms([[1,3],[3,5],[5,7]]) == 1
assert min_meeting_rooms([[1,4],[2,5],[3,6]]) == 3
'''),
            "num_predict": 1000,
        },
        {
            "id": "programming_json_transform",
            "domain": "programming/data",
            "prompt": "Return only Python code. Define summarize_orders(orders) where orders is a list of dicts with user, status, and total fields. Return a dict mapping each user to the sum of total for only status == 'paid'. Users with no paid orders should be absent.",
            "checker": code_check("summarize_orders", r'''
orders = [
    {'user':'a','status':'paid','total':10},
    {'user':'b','status':'void','total':99},
    {'user':'a','status':'paid','total':2.5},
    {'user':'b','status':'paid','total':7},
]
assert summarize_orders(orders) == {'a': 12.5, 'b': 7}
assert summarize_orders([]) == {}
assert summarize_orders([{'user':'x','status':'failed','total':5}]) == {}
'''),
            "num_predict": 900,
        },
        {
            "id": "programming_sql_window",
            "domain": "programming/sql",
            "prompt": f"{common}\nPostgreSQL: table events(user_id, event_type, created_at). Write a query to find users whose first event in calendar year 2025 was 'signup' and whose immediately next event was 'purchase'.",
            "checker": sql_window_check,
            "num_predict": 1200,
        },
        # Science / engineering
        {
            "id": "physics_projectile_angle",
            "domain": "science/physics",
            "prompt": f"{common}\nIgnoring air resistance, a projectile is launched and lands at the same height 100 m away with speed 50 m/s. Using g=9.8 m/s^2, what is the smaller launch angle in degrees?",
            "checker": physics_projectile_check,
            "num_predict": 1024,
        },
        {
            "id": "physics_circuit_current",
            "domain": "science/physics",
            "prompt": f"{common}\nA 12 V ideal battery is connected to a 4 ohm resistor in series with a parallel pair of 6 ohm and 3 ohm resistors. What is the total current from the battery?",
            "checker": circuit_check,
            "num_predict": 768,
        },
        {
            "id": "chemistry_buffer_ph",
            "domain": "science/chemistry",
            "prompt": f"{common}\nA buffer contains 0.10 M acetic acid and 0.20 M acetate. Given pKa = 4.76, estimate the pH using Henderson-Hasselbalch.",
            "checker": chemistry_check,
            "num_predict": 768,
        },
        {
            "id": "biology_central_dogma_exception",
            "domain": "science/biology",
            "prompt": f"{common}\nWhat enzyme allows retroviruses to make DNA from an RNA genome, and why is this an exception to the simplest central dogma flow?",
            "checker": contains_all("reverse transcriptase", "RNA", "DNA"),
            "num_predict": 768,
        },
        {
            "id": "thermo_isothermal_work",
            "domain": "science/thermodynamics",
            "prompt": f"{common}\nFor 1 mole of ideal gas undergoing reversible isothermal expansion at 300 K from 1 L to 10 L, compute the work done by the gas in joules. Use R=8.314 J/mol/K.",
            "checker": thermodynamics_check,
            "num_predict": 1024,
        },
        # Logic / security / data reasoning
        {
            "id": "logic_knights_knaves",
            "domain": "logic",
            "prompt": f"{common}\nOn an island, knights always tell truth and knaves always lie. A says: 'B is a knave.' B says: 'A and I are of opposite types.' What are A and B?",
            "checker": knights_knaves_check,
            "num_predict": 768,
        },
        {
            "id": "logic_scheduling",
            "domain": "logic",
            "prompt": f"{common}\nTasks A,B,C,D,E have durations 3,2,4,2,1. Dependencies: A before C, B before C, C before D, B before E. With two identical workers and nonpreemptive tasks, what is the minimum project completion time?",
            "checker": numeric_answer(9),
            "num_predict": 1024,
        },
        {
            "id": "data_extraction_tricky_json",
            "domain": "data/instruction",
            "prompt": "Return only minified JSON. From this log line extract user_id, action, and success boolean: ts=2026-07-02 level=info msg='user 42 attempted deploy: success=false' trace=abc",
            "checker": json_check({"user_id": 42, "action": "deploy", "success": False}),
            "num_predict": 400,
        },
        {
            "id": "security_hashing_passwords",
            "domain": "security",
            "prompt": f"{common}\nFor storing user passwords, is plain SHA-256(password) adequate? If not, name two properties a better password hashing scheme should have.",
            "checker": security_password_check,
            "num_predict": 768,
        },
    ]


def run_eval(model: str, base_url: str, think: bool, outdir: Path) -> tuple[Path, Path]:
    ollama = Ollama(base_url, model)
    tests = make_tests()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows: list[dict[str, Any]] = []
    for i, test in enumerate(tests, 1):
        print(f"[{i:02d}/{len(tests)}] {test['id']} ...", flush=True)
        started = time.perf_counter()
        resp = ollama.generate(
            test["prompt"],
            think=think,
            num_predict=test.get("num_predict", 1024),
            num_ctx=test.get("num_ctx", 8192),
            timeout=test.get("timeout", 600),
        )
        response_text = resp.get("response") or ""
        try:
            score, detail = test["checker"](response_text)
        except Exception as e:
            score, detail = 0.0, f"checker error: {e!r}"
        row = {
            "id": test["id"],
            "domain": test["domain"],
            "score": score,
            "pass": score >= 1.0,
            "detail": detail,
            "response": response_text,
            "thinking_chars": len(resp.get("thinking") or ""),
            "wall_s": time.perf_counter() - started,
            "metrics": {
                "wall_s": resp.get("wall_s"),
                "done_reason": resp.get("done_reason"),
                "prompt_eval_count": resp.get("prompt_eval_count"),
                "eval_count": resp.get("eval_count"),
                "perf": resp.get("perf"),
            },
        }
        rows.append(row)
        print(f"    score={score} detail={detail[:160]}", flush=True)

    by_domain: dict[str, dict[str, float]] = {}
    for r in rows:
        d = r["domain"].split("/")[0]
        by_domain.setdefault(d, {"score": 0.0, "pass": 0, "total": 0})
        by_domain[d]["score"] += float(r["score"])
        by_domain[d]["pass"] += int(r["pass"])
        by_domain[d]["total"] += 1
    summary = {
        "score": sum(float(r["score"]) for r in rows),
        "pass": sum(1 for r in rows if r["pass"]),
        "total": len(rows),
        "accuracy": sum(float(r["score"]) for r in rows) / len(rows),
        "by_domain": by_domain,
        "mean_wall_s": statistics.mean(r["wall_s"] for r in rows),
        "total_wall_s": sum(r["wall_s"] for r in rows),
        "mean_eval_tps": statistics.mean(
            [r["metrics"]["perf"].get("eval_tps") for r in rows if r["metrics"].get("perf") and r["metrics"]["perf"].get("eval_tps")]
        ),
    }
    result = {
        "model": model,
        "base_url": base_url,
        "think": think,
        "started_at_utc": stamp,
        "summary": summary,
        "tests": rows,
    }
    outdir.mkdir(parents=True, exist_ok=True)
    json_path = outdir / f"tough_eval_{model.replace(':','_')}_{'think' if think else 'direct'}_{stamp}.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    md_path = outdir / f"tough_eval_{model.replace(':','_')}_{'think' if think else 'direct'}_{stamp}.md"
    md_path.write_text(render_md(result))
    return json_path, md_path


def render_md(result: dict[str, Any]) -> str:
    s = result["summary"]
    lines = []
    lines.append(f"# Tough Mixed-Domain Eval: `{result['model']}`")
    lines.append("")
    lines.append(f"Mode: `think:{str(result['think']).lower()}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Overall: **{s['pass']}/{s['total']}** passed (**{s['accuracy']*100:.1f}%**) ")
    lines.append(f"- Total wall time: **{s['total_wall_s']:.1f}s**")
    lines.append(f"- Mean wall time/test: **{s['mean_wall_s']:.1f}s**")
    lines.append(f"- Mean eval throughput: **{s['mean_eval_tps']:.1f} tok/s**")
    lines.append("")
    lines.append("## By domain")
    lines.append("")
    lines.append("| Domain | Passed | Total | Accuracy |")
    lines.append("|---|---:|---:|---:|")
    for d, row in sorted(s["by_domain"].items()):
        acc = row["score"] / row["total"] if row["total"] else 0
        lines.append(f"| {d} | {row['pass']} | {row['total']} | {acc*100:.1f}% |")
    lines.append("")
    lines.append("## Per-question results")
    lines.append("")
    lines.append("| ID | Domain | Result | Wall s | Eval tokens | Notes |")
    lines.append("|---|---|---:|---:|---:|---|")
    for r in result["tests"]:
        status = "PASS" if r["pass"] else "FAIL"
        eval_count = r["metrics"].get("eval_count")
        detail = str(r["detail"]).replace("|", "\\|").replace("\n", " ")[:180]
        lines.append(f"| `{r['id']}` | {r['domain']} | {status} | {r['wall_s']:.1f} | {eval_count} | {detail} |")
    lines.append("")
    lines.append("## Failures / partials")
    lines.append("")
    for r in result["tests"]:
        if r["pass"]:
            continue
        lines.append(f"### `{r['id']}` ({r['domain']})")
        lines.append("")
        lines.append(f"Grader detail: `{r['detail']}`")
        lines.append("")
        resp = r["response"].strip()
        if len(resp) > 1200:
            resp = resp[:1200] + "\n... [truncated]"
        lines.append("```text")
        lines.append(resp)
        lines.append("```")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "ornith:latest"))
    ap.add_argument("--base-url", default=os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ap.add_argument("--think", action="store_true", help="enable Ollama thinking mode")
    ap.add_argument("--outdir", default="benchmark_results")
    args = ap.parse_args()
    json_path, md_path = run_eval(args.model, args.base_url, args.think, Path(args.outdir))
    print(json_path)
    print(md_path)
    data = json.loads(json_path.read_text())
    print(json.dumps(data["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
