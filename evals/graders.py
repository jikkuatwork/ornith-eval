#!/usr/bin/env python3
"""Deterministic graders for modular Ollama eval suites."""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def strip_fences(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:[a-zA-Z0-9_+-]+)?\s*(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    return text.strip("` \n\t")


def final_text(text: str) -> str:
    matches = re.findall(r"FINAL\s*:\s*(.+)", text, flags=re.I)
    if matches:
        return matches[-1].strip()
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    return lines[-1] if lines else text.strip()


def numbers(text: str) -> list[float]:
    return [float(x) for x in re.findall(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text.replace(",", ""))]


def score(ok: bool, detail: str) -> tuple[float, str]:
    return (1.0 if ok else 0.0, detail)


def grade_exact(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    expected = str(spec["value"])
    target = final_text(resp) if spec.get("use_final", True) else resp
    target = strip_fences(target).strip().strip(". '")
    if spec.get("case_sensitive", False):
        ok = target == expected
    else:
        ok = normalize(target).strip(". '") == normalize(expected)
    if not ok and spec.get("allow_contains", True):
        ok = expected.lower() in normalize(resp) if not spec.get("case_sensitive", False) else expected in resp
    return score(ok, f"expected={expected!r}; got={target[:200]!r}")


def grade_contains_all(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    low = normalize(resp)
    missing = [str(t) for t in spec.get("terms", []) if str(t).lower() not in low]
    return score(not missing, f"missing={missing}; response={resp[:220]!r}")


def grade_contains_any(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    low = normalize(resp)
    hits = [str(t) for t in spec.get("terms", []) if str(t).lower() in low]
    return score(bool(hits), f"hits={hits}; expected_any={spec.get('terms', [])}; response={resp[:220]!r}")


def grade_combo(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    low = normalize(resp)
    missing = []
    for slot, vals in spec.get("slots", {}).items():
        if not any(str(v).lower() in low for v in vals):
            missing.append(slot)
    return score(not missing, f"missing_slots={missing}; response={resp[:260]!r}")


def grade_numeric(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    expected = float(spec["value"])
    tol = float(spec.get("tolerance", 1e-6))
    target = final_text(resp) if spec.get("use_final", True) else resp
    vals = numbers(target) or numbers(resp)
    if not vals:
        return 0.0, "no numeric value found"
    # If unit accepts kJ, allow declared multiplier for all numbers.
    candidates = vals[:]
    for mult in spec.get("multipliers", []):
        candidates.extend([v * float(mult) for v in vals])
    best = min(abs(v - expected) for v in candidates)
    return score(best <= tol, f"values={vals[:10]}; expected={expected}; best_abs_err={best}")


def grade_fraction(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    num = int(spec["num"])
    den = int(spec["den"])
    expected = num / den
    scopes = [("final", final_text(resp)), ("response", resp)]
    for name, text in scopes:
        for m in re.finditer(r"(-?\d+)\s*/\s*(-?\d+)", text):
            d = int(m.group(2))
            if d == 0:
                continue
            got = int(m.group(1)) / d
            if abs(got - expected) <= float(spec.get("tolerance", 1e-12)):
                return 1.0, f"got_fraction={m.group(0)!r} in {name}; expected={num}/{den}"
    vals = numbers(final_text(resp)) or numbers(resp)
    if vals:
        best = min(abs(v - expected) for v in vals)
        return score(best <= float(spec.get("tolerance", 1e-9)), f"values={vals[:10]}; expected={expected}")
    return 0.0, f"no fraction/numeric answer; expected={num}/{den}"


def grade_json_equals(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    text = strip_fences(resp)
    if not text.startswith("{") and not text.startswith("["):
        m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
        if m:
            text = m.group(1)
    try:
        obj = json.loads(text)
    except Exception as e:
        return 0.0, f"json parse failed: {e}; text={text[:220]!r}"
    expected = spec["value"]
    return score(obj == expected, f"obj={obj!r}; expected={expected!r}")


def grade_regex_fullmatch(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    pattern = strip_fences(final_text(resp) if spec.get("use_final", False) else resp)
    # If model included a prose line, choose the most regex-looking non-empty line.
    lines = [ln.strip().strip("`/") for ln in pattern.splitlines() if ln.strip()]
    if lines:
        pattern = max(lines, key=lambda s: sum(ch in s for ch in "^$[]{}\\+*?.|()"))
    try:
        rx = re.compile(pattern)
    except Exception as e:
        return 0.0, f"compile failed for {pattern!r}: {e}"
    positives = spec.get("positives", [])
    negatives = spec.get("negatives", [])
    ok_pos = all(rx.fullmatch(x) for x in positives)
    ok_neg = not any(rx.fullmatch(x) for x in negatives)
    return score(ok_pos and ok_neg, f"pattern={pattern!r}; ok_pos={ok_pos}; ok_neg={ok_neg}")


def extract_code(resp: str) -> str:
    m = re.search(r"```(?:python|py)\s*(.*?)```", resp, re.S | re.I)
    if not m:
        m = re.search(r"```\s*(.*?)```", resp, re.S)
    code = m.group(1) if m else resp
    code = re.sub(r"^\s*python\s*", "", code.strip(), flags=re.I)
    return code.strip()


def run_python_candidate(code: str, tests: str, timeout: int = 8) -> tuple[bool, str]:
    program = code + "\n\n" + tests + "\nprint('OK')\n"
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "candidate.py"
        path.write_text(program)
        try:
            r = subprocess.run(
                [sys.executable, str(path)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return False, "timeout"
    if r.returncode == 0 and "OK" in r.stdout:
        return True, r.stdout.strip()
    return False, (r.stderr or r.stdout).strip()[-2500:]


def grade_python_unittest(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    code = extract_code(resp)
    required = spec.get("required_name")
    if required and required not in code:
        return 0.0, f"required name {required!r} not found in code excerpt={code[:240]!r}"
    ok, detail = run_python_candidate(code, spec["tests"], timeout=int(spec.get("timeout", 8)))
    return score(ok, detail)


def grade_choice(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    expected = str(spec["value"]).strip().lower()
    text = normalize(final_text(resp)).strip(". )(")
    m = re.match(r"(?:answer\s*[:\-]?\s*)?([a-z])\b", text)
    got = m.group(1) if m else text[:1]
    return score(got == expected, f"got={got!r}; expected={expected!r}; final={final_text(resp)!r}")


GRADERS = {
    "exact": grade_exact,
    "contains_all": grade_contains_all,
    "contains_any": grade_contains_any,
    "combo": grade_combo,
    "numeric": grade_numeric,
    "fraction": grade_fraction,
    "json_equals": grade_json_equals,
    "regex_fullmatch": grade_regex_fullmatch,
    "python_unittest": grade_python_unittest,
    "choice": grade_choice,
}


def grade_response(resp: str, spec: dict[str, Any]) -> tuple[float, str]:
    typ = spec.get("type")
    if typ not in GRADERS:
        return 0.0, f"unknown grader type={typ!r}"
    return GRADERS[typ](resp, spec)
