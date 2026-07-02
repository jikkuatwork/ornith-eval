#!/usr/bin/env python3
"""Modular Ollama eval runner.

Examples:
  python3 evals/runner.py --list
  python3 evals/runner.py --suite kerala_core --model ornith:latest
  python3 evals/runner.py --suite deep_convoluted_conversation --turns 1200 --num-ctx 65536
  python3 evals/runner.py --suite all --limit 3
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import requests

try:  # supports both `python -m evals.runner` and `python evals/runner.py`
    from evals.graders import grade_response
except Exception:  # pragma: no cover
    from graders import grade_response  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
SUITES_DIR = ROOT / "evals" / "suites"


def ns_to_s(v: int | float | None) -> float | None:
    return None if v is None else float(v) / 1_000_000_000.0


def tps(count: int | None, duration_ns: int | None) -> float | None:
    if not count or not duration_ns:
        return None
    seconds = duration_ns / 1_000_000_000.0
    return count / seconds if seconds > 0 else None


class OllamaClient:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.session = requests.Session()

    def _decorate(self, out: dict[str, Any], wall: float, status: int) -> dict[str, Any]:
        out["http_status"] = status
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

    def generate(self, prompt: str, options: dict[str, Any], *, think: bool, fmt: str | None = None, timeout: int = 900) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": think,
            "keep_alive": "10m",
            "options": options,
        }
        if fmt:
            payload["format"] = fmt
        start = time.perf_counter()
        r = self.session.post(f"{self.base_url}/api/generate", json=payload, timeout=timeout)
        wall = time.perf_counter() - start
        try:
            out = r.json()
        except Exception:
            out = {"raw_text": r.text}
        return self._decorate(out, wall, r.status_code)

    def chat(self, messages: list[dict[str, str]], options: dict[str, Any], *, think: bool, timeout: int = 900) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": think,
            "keep_alive": "10m",
            "options": options,
        }
        start = time.perf_counter()
        r = self.session.post(f"{self.base_url}/api/chat", json=payload, timeout=timeout)
        wall = time.perf_counter() - start
        try:
            out = r.json()
        except Exception:
            out = {"raw_text": r.text}
        return self._decorate(out, wall, r.status_code)


def suite_paths() -> list[Path]:
    return sorted(SUITES_DIR.glob("*.json"))


def load_suite(name_or_path: str) -> dict[str, Any]:
    p = Path(name_or_path)
    if not p.exists():
        p = SUITES_DIR / f"{name_or_path}.json"
    if not p.exists():
        raise SystemExit(f"suite not found: {name_or_path}")
    data = json.loads(p.read_text())
    data["_path"] = str(p)
    return data


def make_options(defaults: dict[str, Any], item: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    opts = dict(defaults.get("options", {}))
    opts.setdefault("temperature", defaults.get("temperature", 0))
    opts.setdefault("seed", defaults.get("seed", 777))
    opts["num_ctx"] = args.num_ctx or item.get("num_ctx") or defaults.get("num_ctx", 8192)
    opts["num_predict"] = item.get("num_predict") or defaults.get("num_predict", 512)
    return opts


def row_metrics(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "http_status": raw.get("http_status"),
        "done_reason": raw.get("done_reason"),
        "wall_s": raw.get("wall_s"),
        "prompt_eval_count": raw.get("prompt_eval_count"),
        "eval_count": raw.get("eval_count"),
        "perf": raw.get("perf"),
    }


def run_standard_suite(suite: dict[str, Any], client: OllamaClient, args: argparse.Namespace) -> list[dict[str, Any]]:
    defaults = suite.get("defaults", {})
    cases = list(suite.get("cases", []))
    if args.limit:
        cases = cases[: args.limit]
    rows = []
    for i, case in enumerate(cases, 1):
        print(f"[{suite['id']} {i:02d}/{len(cases):02d}] {case['id']} ...", flush=True)
        options = make_options(defaults, case, args)
        think = bool(args.think if args.think is not None else case.get("think", defaults.get("think", False)))
        raw = client.generate(
            case["prompt"],
            options,
            think=think,
            fmt=case.get("format"),
            timeout=int(case.get("timeout", defaults.get("timeout", 900))),
        )
        response = raw.get("response", "")
        score, detail = grade_response(response, case["grader"])
        row = {
            "id": case["id"],
            "category": case.get("category", suite.get("id")),
            "domain": case.get("domain", suite.get("id")),
            "prompt": case["prompt"],
            "response": response,
            "score": float(score),
            "pass": bool(score >= 1.0),
            "detail": detail,
            "metrics": row_metrics(raw),
        }
        rows.append(row)
        print(f"    {'PASS' if row['pass'] else 'FAIL'} wall={raw.get('wall_s'):.2f}s eval={raw.get('eval_count')} detail={detail[:180]}", flush=True)
    return rows


DEFAULT_FILLER = {
    "names": ["Tara", "Sam", "Mira", "Leo", "Asha", "Ben", "Iris", "Quinn", "Ravi", "Lena", "Pavel", "Nina"],
    "colors": ["blue", "green", "purple", "orange", "silver", "white", "black", "gold", "pink", "brown", "yellow", "red"],
    "objects": ["kite", "marble", "cup", "notebook", "lantern", "rope", "basket", "puzzle", "drum", "coin", "shell", "hat", "ball"],
    "animals": ["goat", "fox", "yak", "owl", "horse", "cat", "dog", "mule", "crane", "lizard", "ox"],
    "places": ["garden", "library", "station", "attic", "market", "courtyard", "studio", "workshop", "balcony"],
}


def build_filler(turn: int, rng: random.Random, suite: dict[str, Any]) -> str:
    vocab = dict(DEFAULT_FILLER)
    vocab.update(suite.get("filler_vocab", {}))
    name = rng.choice(vocab["names"])
    color = rng.choice(vocab["colors"])
    obj = rng.choice(vocab["objects"])
    animal = rng.choice(vocab["animals"])
    place = rng.choice(vocab["places"])
    templates = suite.get("filler_templates") or [
        "Side note {turn}: {name} saw a {color} {animal} near the {place}; this belongs to that side story only.",
        "Random aside {turn}: {name} carried a {color} {obj}; do not confuse it with earlier people or objects.",
        "Joke {turn}: someone guessed the code might be {code}, but that joke was not a real update.",
        "Digression {turn}: we discussed {name}'s {color} ball, unrelated to Tom's old ball.",
        "Puzzle scrap {turn}: the phrase {phrase} appeared in a different game, not the remembered passphrase.",
        "Side key note {turn}: a spare key was mentioned inside a {color} {obj}, but it was not Maya's brass key.",
    ]
    return rng.choice(templates).format(
        turn=turn,
        name=name,
        color=color,
        obj=obj,
        animal=animal,
        place=place,
        code=rng.randint(1000, 9999),
        phrase=rng.choice(["amber owl", "blue rook", "violet kite", "silver lantern", "coconut lamp"]),
    )


def run_conversation_suite(suite: dict[str, Any], client: OllamaClient, args: argparse.Namespace) -> list[dict[str, Any]]:
    defaults = suite.get("defaults", {})
    events = {int(e["turn"]): e["text"] for e in suite.get("events", [])}
    probes = sorted(suite.get("probes", []), key=lambda p: int(p["after_turn"]))
    if args.limit:
        probes = probes[: args.limit]
    max_probe_turn = max((int(p["after_turn"]) for p in probes), default=0)
    turns = args.turns or suite.get("turns") or max_probe_turn
    turns = min(int(turns), max_probe_turn) if args.limit else int(turns)
    probes_by_turn: dict[int, list[dict[str, Any]]] = {}
    for p in probes:
        if int(p["after_turn"]) <= turns:
            probes_by_turn.setdefault(int(p["after_turn"]), []).append(p)

    rng = random.Random(int(suite.get("seed", 20260702)))
    messages: list[dict[str, str]] = [{"role": "system", "content": suite.get("system", "Remember the conversation and answer probes briefly.")}]
    rows: list[dict[str, Any]] = []

    for turn in range(1, turns + 1):
        content = events.get(turn) or build_filler(turn, rng, suite)
        messages.append({"role": "user", "content": content})
        messages.append({"role": "assistant", "content": suite.get("assistant_ack", "Got it.")})

        for probe in probes_by_turn.get(turn, []):
            print(f"[{suite['id']} probe {len(rows)+1:02d}/{len(probes):02d}] {probe['id']} after turn {turn} messages={len(messages)+1}", flush=True)
            options = make_options(defaults, probe, args)
            think = bool(args.think if args.think is not None else probe.get("think", defaults.get("think", False)))
            probe_messages = messages + [{"role": "user", "content": probe["question"]}]
            raw = client.chat(
                probe_messages,
                options,
                think=think,
                timeout=int(probe.get("timeout", defaults.get("timeout", 900))),
            )
            response = raw.get("message", {}).get("content", "")
            score, detail = grade_response(response, probe["grader"])
            row = {
                "id": probe["id"],
                "category": probe.get("category", "conversation"),
                "domain": probe.get("domain", "conversation"),
                "after_turn": int(probe["after_turn"]),
                "fact_turn": probe.get("fact_turn"),
                "turn_gap": int(probe["after_turn"]) - int(probe.get("fact_turn", probe["after_turn"])),
                "question": probe["question"],
                "response": response,
                "score": float(score),
                "pass": bool(score >= 1.0),
                "detail": detail,
                "metrics": row_metrics(raw),
            }
            rows.append(row)
            print(f"    {'PASS' if row['pass'] else 'FAIL'} wall={raw.get('wall_s'):.2f}s prompt={raw.get('prompt_eval_count')} response={response[:160]!r}", flush=True)
            messages.append({"role": "user", "content": probe["question"]})
            messages.append({"role": "assistant", "content": response})
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_category: dict[str, dict[str, float]] = {}
    for r in rows:
        cat = r.get("category") or r.get("domain") or "default"
        by_category.setdefault(cat, {"score": 0.0, "pass": 0, "total": 0})
        by_category[cat]["score"] += float(r["score"])
        by_category[cat]["pass"] += int(r["pass"])
        by_category[cat]["total"] += 1
    walls = [r["metrics"].get("wall_s") for r in rows if r["metrics"].get("wall_s") is not None]
    prompt_counts = [r["metrics"].get("prompt_eval_count") for r in rows if r["metrics"].get("prompt_eval_count") is not None]
    prompt_tps_vals = [r["metrics"].get("perf", {}).get("prompt_tps") for r in rows if r["metrics"].get("perf", {}).get("prompt_tps")]
    eval_tps_vals = [r["metrics"].get("perf", {}).get("eval_tps") for r in rows if r["metrics"].get("perf", {}).get("eval_tps")]
    return {
        "pass": sum(1 for r in rows if r["pass"]),
        "total": len(rows),
        "accuracy": (sum(float(r["score"]) for r in rows) / len(rows)) if rows else 0,
        "by_category": by_category,
        "total_wall_s": sum(walls),
        "mean_wall_s": statistics.mean(walls) if walls else None,
        "median_wall_s": statistics.median(walls) if walls else None,
        "max_prompt_eval_count": max(prompt_counts) if prompt_counts else None,
        "mean_prompt_eval_count": statistics.mean(prompt_counts) if prompt_counts else None,
        "mean_prompt_tps": statistics.mean(prompt_tps_vals) if prompt_tps_vals else None,
        "mean_eval_tps": statistics.mean(eval_tps_vals) if eval_tps_vals else None,
    }


def render_md(result: dict[str, Any]) -> str:
    suite = result["suite"]
    summary = result["summary"]
    lines = [
        f"# Modular Eval: `{suite['id']}` on `{result['model']}`",
        "",
        suite.get("title", ""),
        "",
        "## Summary",
        "",
        f"- Result: **{summary['pass']}/{summary['total']}** (**{summary['accuracy']*100:.1f}%**) ",
        f"- Total wall time: **{summary['total_wall_s']:.1f}s**",
        f"- Mean/median latency: **{summary['mean_wall_s']:.2f}s / {summary['median_wall_s']:.2f}s**" if summary.get("mean_wall_s") is not None else "- Mean/median latency: n/a",
        f"- Max prompt tokens: **{summary['max_prompt_eval_count']}**",
    ]
    if summary.get("mean_prompt_tps") is not None:
        lines.append(f"- Mean prompt ingest speed: **{summary['mean_prompt_tps']:.1f} tok/s**")
    if summary.get("mean_eval_tps") is not None:
        lines.append(f"- Mean output speed: **{summary['mean_eval_tps']:.1f} tok/s**")
    lines += ["", "## By category", "", "| Category | Passed | Total | Accuracy |", "|---|---:|---:|---:|"]
    for cat, row in sorted(summary["by_category"].items()):
        acc = row["score"] / row["total"] if row["total"] else 0
        lines.append(f"| {cat} | {row['pass']} | {row['total']} | {acc*100:.1f}% |")
    lines += ["", "## Per-item results", ""]
    if suite.get("kind") == "conversation":
        lines.append("| ID | Category | Turn | Gap | Result | Wall s | Prompt tokens | Response |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---|")
        for r in result["rows"]:
            resp = r["response"].replace("|", "\\|").replace("\n", " ")[:180]
            lines.append(f"| `{r['id']}` | {r['category']} | {r.get('after_turn')} | {r.get('turn_gap')} | {'PASS' if r['pass'] else 'FAIL'} | {r['metrics'].get('wall_s'):.2f} | {r['metrics'].get('prompt_eval_count')} | {resp} |")
    else:
        lines.append("| ID | Category | Result | Wall s | Eval tokens | Detail |")
        lines.append("|---|---|---:|---:|---:|---|")
        for r in result["rows"]:
            detail = r["detail"].replace("|", "\\|").replace("\n", " ")[:180]
            wall = r["metrics"].get("wall_s")
            lines.append(f"| `{r['id']}` | {r['category']} | {'PASS' if r['pass'] else 'FAIL'} | {wall:.2f} | {r['metrics'].get('eval_count')} | {detail} |")
    failures = [r for r in result["rows"] if not r["pass"]]
    if failures:
        lines += ["", "## Failures", ""]
        for r in failures:
            lines += [f"### `{r['id']}`", "", f"Detail: `{r['detail']}`", "", "```text", r["response"][:1600], "```", ""]
    return "\n".join(lines) + "\n"


def run_suite(suite: dict[str, Any], args: argparse.Namespace) -> tuple[Path, Path, dict[str, Any]]:
    client = OllamaClient(args.base_url, args.model)
    kind = suite.get("kind", "standard")
    if kind == "conversation":
        rows = run_conversation_suite(suite, client, args)
    elif kind == "standard":
        rows = run_standard_suite(suite, client, args)
    else:
        raise SystemExit(f"unknown suite kind: {kind}")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    result = {
        "model": args.model,
        "base_url": args.base_url,
        "started_at_utc": stamp,
        "suite": {k: v for k, v in suite.items() if k not in {"cases", "events", "probes", "filler_templates", "filler_vocab"}},
        "summary": summarize(rows),
        "rows": rows,
    }
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = f"modular_eval_{suite['id']}_{args.model.replace(':','_')}_{stamp}"
    json_path = outdir / f"{stem}.json"
    md_path = outdir / f"{stem}.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    md_path.write_text(render_md(result))
    return json_path, md_path, result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", default=None, help="suite id/path, or 'all'")
    ap.add_argument("--list", action="store_true", help="list suites")
    ap.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "ornith:latest"))
    ap.add_argument("--base-url", default=os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ap.add_argument("--num-ctx", type=int, default=None, help="override num_ctx")
    ap.add_argument("--turns", type=int, default=None, help="override conversation turns")
    ap.add_argument("--think", action="store_true", default=None, help="force think:true")
    ap.add_argument("--limit", type=int, default=None, help="limit cases/probes for smoke tests")
    ap.add_argument("--outdir", default="benchmark_results")
    args = ap.parse_args()

    if args.list or not args.suite:
        print("Available suites:")
        for p in suite_paths():
            data = json.loads(p.read_text())
            print(f"- {data.get('id', p.stem)} ({data.get('kind', 'standard')}): {data.get('title', '')}")
        return 0 if args.list else 2

    suites = [load_suite(p.stem) for p in suite_paths()] if args.suite == "all" else [load_suite(args.suite)]
    outputs = []
    for suite in suites:
        json_path, md_path, result = run_suite(suite, args)
        outputs.append((json_path, md_path, result["summary"]))
        print(json_path)
        print(md_path)
        print(json.dumps(result["summary"], indent=2))
    if len(outputs) > 1:
        total_pass = sum(s["pass"] for _, _, s in outputs)
        total = sum(s["total"] for _, _, s in outputs)
        print(json.dumps({"combined_pass": total_pass, "combined_total": total, "combined_accuracy": total_pass / total if total else 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
