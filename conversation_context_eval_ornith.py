#!/usr/bin/env python3
"""Long conversational context/memory eval for Ollama models.

This eval simulates hundreds of chat turns with short synthetic assistant acks,
then periodically asks probe questions via /api/chat. It measures whether the
model can retrieve/update facts, ignore distractors, reason over relations, and
stay consistent late in the conversation. It also records wall time and Ollama
prompt/eval token speeds per probe.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import re
import statistics
import time
from pathlib import Path
from typing import Any, Callable

import requests


def ns_to_s(v: int | float | None) -> float | None:
    return None if v is None else float(v) / 1_000_000_000.0


def tps(count: int | None, duration_ns: int | None) -> float | None:
    if not count or not duration_ns:
        return None
    sec = duration_ns / 1_000_000_000.0
    return count / sec if sec > 0 else None


class OllamaChat:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.session = requests.Session()

    def chat(self, messages: list[dict[str, str]], *, think: bool, num_ctx: int, num_predict: int, timeout: int = 600) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": think,
            "keep_alive": "10m",
            "options": {
                "temperature": 0,
                "seed": 777,
                "num_ctx": num_ctx,
                "num_predict": num_predict,
            },
        }
        start = time.perf_counter()
        r = self.session.post(f"{self.base_url}/api/chat", json=payload, timeout=timeout)
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


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def contains_all(*terms: str) -> Callable[[str], tuple[float, str]]:
    def check(resp: str) -> tuple[float, str]:
        low = normalize(resp)
        missing = [t for t in terms if t.lower() not in low]
        return (1.0 if not missing else 0.0, f"missing={missing}; response={resp[:180]!r}")
    return check


def contains_any(*terms: str) -> Callable[[str], tuple[float, str]]:
    def check(resp: str) -> tuple[float, str]:
        low = normalize(resp)
        hit = [t for t in terms if t.lower() in low]
        return (1.0 if hit else 0.0, f"hit={hit}; expected_any={terms}; response={resp[:180]!r}")
    return check


def exact_phrase(expected: str) -> Callable[[str], tuple[float, str]]:
    def check(resp: str) -> tuple[float, str]:
        low = normalize(resp).strip(". '")
        ok = low == expected.lower() or expected.lower() in low
        return (1.0 if ok else 0.0, f"expected={expected!r}; got={resp[:180]!r}")
    return check


def number_exact(expected: str) -> Callable[[str], tuple[float, str]]:
    def check(resp: str) -> tuple[float, str]:
        nums = re.findall(r"\d+", resp)
        ok = expected in nums or expected in resp
        return (1.0 if ok else 0.0, f"nums={nums}; expected={expected}; response={resp[:180]!r}")
    return check


def combo_check(required: dict[str, list[str]]) -> Callable[[str], tuple[float, str]]:
    """Require at least one synonym from each named slot."""
    def check(resp: str) -> tuple[float, str]:
        low = normalize(resp)
        missing = []
        for slot, synonyms in required.items():
            if not any(x.lower() in low for x in synonyms):
                missing.append(slot)
        return (1.0 if not missing else 0.0, f"missing_slots={missing}; response={resp[:220]!r}")
    return check


def json_or_text_combo(required: dict[str, list[str]]) -> Callable[[str], tuple[float, str]]:
    # Forgiving: JSON encouraged, but text with all values is acceptable.
    return combo_check(required)


SYSTEM = """You are in a long conversational memory evaluation.
Track the conversation carefully across many turns.
Facts labeled CANON are reliable. Facts labeled UPDATE replace earlier mutable facts.
Messages labeled CHATTER, RUMOR, or JOKE are distractors unless they concern a new unrelated person/object.
When the user sends a PROBE, answer only the requested answer, as briefly as possible. Prefer the latest UPDATE when relevant.
"""


CANON_EVENTS: dict[int, str] = {
    3: "CANON T003: Tom was playing with his red ball when he saw a yellow ox far away, then Tom went back home surprised.",
    18: "CANON T018: Elena lent Priya her striped scarf before Priya boarded the train. Elena kept the black umbrella.",
    27: "CANON T027: Maya put the brass key inside the blue vase.",
    44: "CANON T044: The lab cabinet code is 4192 for now.",
    58: "CANON T058: Nora's mentor is Ivo, and Ivo's codeword is glacier.",
    64: "CANON T064: Nora lent the copper compass to Jules.",
    82: "UPDATE T082: Maya moved the brass key out of the blue vase and into the green drawer.",
    96: "CANON T096: Nina's red box contains the map, the blue box contains the lens, and the green box contains the coin.",
    108: "UPDATE T108: The lab cabinet code changed from 4192 to 7305. The old code should be ignored.",
    124: "UPDATE T124: Jules handed the copper compass to Priya. Priya currently has it.",
    137: "CANON T137: Omar received Nina's red box and did not open it.",
    169: "CANON T169: If the user later writes lantern check, the correct response is violet rook.",
    211: "UPDATE T211: The archive token is hexagonal, made of copper, weighs 7 grams, and is stored under the orchid pot.",
}


PROBES: list[dict[str, Any]] = [
    {
        "id": "tom_ball_mid",
        "after_turn": 55,
        "category": "early_fact_recall",
        "question": "PROBE P01: In the old Tom story, what color was Tom's ball? Answer one word.",
        "checker": exact_phrase("red"),
        "fact_turn": 3,
        "num_predict": 64,
    },
    {
        "id": "tom_ox_mid",
        "after_turn": 75,
        "category": "entity_attribute_binding",
        "question": "PROBE P02: In Tom's story, what animal did he see and what color was it?",
        "checker": contains_all("yellow", "ox"),
        "fact_turn": 3,
        "num_predict": 80,
    },
    {
        "id": "key_after_update",
        "after_turn": 90,
        "category": "state_update",
        "question": "PROBE P03: Where is Maya's brass key now? Use the latest update.",
        "checker": contains_all("green", "drawer"),
        "fact_turn": 82,
        "num_predict": 80,
    },
    {
        "id": "train_coreference",
        "after_turn": 104,
        "category": "coreference",
        "question": "PROBE P04: Who boarded the train with the striped scarf?",
        "checker": contains_all("priya"),
        "fact_turn": 18,
        "num_predict": 80,
    },
    {
        "id": "cabinet_code_current",
        "after_turn": 118,
        "category": "state_update_numeric",
        "question": "PROBE P05: What is the current lab cabinet code? Return only the code.",
        "checker": number_exact("7305"),
        "fact_turn": 108,
        "num_predict": 64,
    },
    {
        "id": "compass_current_holder",
        "after_turn": 150,
        "category": "state_update_entity",
        "question": "PROBE P06: Who currently has the copper compass?",
        "checker": contains_all("priya"),
        "fact_turn": 124,
        "num_predict": 80,
    },
    {
        "id": "map_holder_box_reasoning",
        "after_turn": 176,
        "category": "multi_step_object_reasoning",
        "question": "PROBE P07: Who has the map now? Briefly infer from the box facts.",
        "checker": contains_all("omar"),
        "fact_turn": 137,
        "num_predict": 96,
    },
    {
        "id": "lantern_instruction",
        "after_turn": 205,
        "category": "instruction_memory",
        "question": "PROBE P08: lantern check",
        "checker": exact_phrase("violet rook"),
        "fact_turn": 169,
        "num_predict": 64,
    },
    {
        "id": "multi_hop_codeword",
        "after_turn": 235,
        "category": "multi_hop_relation",
        "question": "PROBE P09: What is the codeword associated with the mentor of the person who originally lent the copper compass?",
        "checker": contains_all("glacier"),
        "fact_turn": 58,
        "num_predict": 96,
    },
    {
        "id": "archive_token_combo",
        "after_turn": 255,
        "category": "multi_attribute_recall",
        "question": "PROBE P10: Give the archive token's shape, material, weight, and storage location.",
        "checker": combo_check({
            "shape": ["hexagonal", "hexagon"],
            "material": ["copper"],
            "weight": ["7", "seven"],
            "location": ["orchid", "pot"],
        }),
        "fact_turn": 211,
        "num_predict": 128,
    },
    {
        "id": "composite_late_json",
        "after_turn": 285,
        "category": "late_composite_reasoning",
        "question": "PROBE P11: Return compact JSON with keys ball_color,current_code,key_location,compass_holder for Tom/Maya/lab/compass facts.",
        "checker": json_or_text_combo({
            "ball_color": ["red"],
            "current_code": ["7305"],
            "key_location": ["green drawer"],
            "compass_holder": ["priya"],
        }),
        "fact_turn": 3,
        "num_predict": 160,
    },
    {
        "id": "tom_ball_very_late_consistency",
        "after_turn": 320,
        "category": "very_late_consistency",
        "question": "PROBE P12: Hundreds of turns later: what was the color of Tom's ball? One word only.",
        "checker": exact_phrase("red"),
        "fact_turn": 3,
        "num_predict": 64,
    },
    {
        "id": "tom_surprise_late",
        "after_turn": 335,
        "category": "late_event_reason",
        "question": "PROBE P13: Why did Tom go back home surprised? Answer with the remembered event.",
        "checker": contains_all("yellow", "ox"),
        "fact_turn": 3,
        "num_predict": 128,
    },
]


NAMES = ["Tim", "Tara", "Sam", "Mira", "Leo", "Asha", "Ben", "Iris", "Omar", "Nina", "Quinn", "Ravi", "Lena", "Pavel"]
COLORS = ["blue", "green", "purple", "orange", "silver", "white", "black", "gold", "pink", "brown", "crimson"]
OBJECTS = ["kite", "marble", "cup", "notebook", "lantern", "rope", "basket", "puzzle", "drum", "coin", "shell", "hat"]
ANIMALS = ["goat", "fox", "yak", "owl", "horse", "cat", "dog", "mule", "crane", "lizard"]
PLACES = ["garden", "library", "station", "attic", "market", "courtyard", "studio", "workshop", "balcony"]


def chatter(turn: int, rng: random.Random) -> str:
    """Create plausible distractor turns with many similar names/colors/objects."""
    name = rng.choice(NAMES)
    color = rng.choice(COLORS)
    obj = rng.choice(OBJECTS)
    animal = rng.choice(ANIMALS)
    place = rng.choice(PLACES)

    templates = [
        f"CHATTER T{turn:03d}: {name} mentioned a {color} {obj} near the {place}; this is just casual chatter.",
        f"CHATTER T{turn:03d}: A {color} {animal} appeared in a side anecdote, unrelated to Tom's earlier story.",
        f"RUMOR T{turn:03d}: Someone guessed a code like {rng.randint(1000,9999)}, but this rumor is not an UPDATE to the lab cabinet.",
        f"JOKE T{turn:03d}: Someone joked that Maya hid a plastic key in a {color} {obj}; jokes do not update the brass key.",
        f"CHATTER T{turn:03d}: We discussed {name}'s {color} ball, which is not Tom's ball.",
        f"CHATTER T{turn:03d}: A note says the phrase {rng.choice(['amber owl','blue rook','violet kite','silver lantern'])} belongs to another game, not the lantern check.",
        f"CHATTER T{turn:03d}: {name} moved from the {place} to the {rng.choice(PLACES)} while carrying a {color} {obj}.",
    ]
    return rng.choice(templates)


def build_turn(turn: int, rng: random.Random) -> str:
    return CANON_EVENTS.get(turn, chatter(turn, rng))


def summarize_result_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_category: dict[str, dict[str, float]] = {}
    for r in rows:
        cat = r["category"]
        by_category.setdefault(cat, {"score": 0.0, "pass": 0, "total": 0})
        by_category[cat]["score"] += float(r["score"])
        by_category[cat]["pass"] += int(r["pass"])
        by_category[cat]["total"] += 1

    walls = [r["wall_s"] for r in rows]
    prompt_counts = [r["metrics"].get("prompt_eval_count") for r in rows if r["metrics"].get("prompt_eval_count") is not None]
    eval_counts = [r["metrics"].get("eval_count") for r in rows if r["metrics"].get("eval_count") is not None]
    prompt_tps_vals = [r["metrics"].get("perf", {}).get("prompt_tps") for r in rows if r["metrics"].get("perf", {}).get("prompt_tps")]
    eval_tps_vals = [r["metrics"].get("perf", {}).get("eval_tps") for r in rows if r["metrics"].get("perf", {}).get("eval_tps")]

    def pct(vals: list[float], q: float) -> float | None:
        if not vals:
            return None
        vals = sorted(vals)
        idx = min(len(vals) - 1, max(0, round((len(vals) - 1) * q)))
        return vals[idx]

    # Retention buckets by gap between fact turn and probe turn.
    gap_buckets = {
        "0-75": {"pass": 0, "total": 0},
        "76-150": {"pass": 0, "total": 0},
        "151-250": {"pass": 0, "total": 0},
        "251+": {"pass": 0, "total": 0},
    }
    for r in rows:
        gap = r.get("turn_gap")
        if gap is None:
            continue
        if gap <= 75:
            b = "0-75"
        elif gap <= 150:
            b = "76-150"
        elif gap <= 250:
            b = "151-250"
        else:
            b = "251+"
        gap_buckets[b]["total"] += 1
        gap_buckets[b]["pass"] += int(r["pass"])

    return {
        "pass": sum(1 for r in rows if r["pass"]),
        "total": len(rows),
        "accuracy": sum(float(r["score"]) for r in rows) / len(rows) if rows else 0,
        "by_category": by_category,
        "by_turn_gap": gap_buckets,
        "total_wall_s": sum(walls),
        "mean_wall_s": statistics.mean(walls) if walls else None,
        "median_wall_s": statistics.median(walls) if walls else None,
        "p95_wall_s": pct(walls, 0.95),
        "max_prompt_eval_count": max(prompt_counts) if prompt_counts else None,
        "mean_prompt_eval_count": statistics.mean(prompt_counts) if prompt_counts else None,
        "mean_eval_count": statistics.mean(eval_counts) if eval_counts else None,
        "mean_prompt_tps": statistics.mean(prompt_tps_vals) if prompt_tps_vals else None,
        "mean_eval_tps": statistics.mean(eval_tps_vals) if eval_tps_vals else None,
    }


def render_md(result: dict[str, Any]) -> str:
    s = result["summary"]
    lines: list[str] = []
    lines.append(f"# Long Conversational Context Eval: `{result['model']}`")
    lines.append("")
    lines.append(f"Mode: `think:{str(result['think']).lower()}`; simulated turns: **{result['turns']}**; probes: **{s['total']}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Accuracy: **{s['pass']}/{s['total']}** (**{s['accuracy']*100:.1f}%**) ")
    lines.append(f"- Total probe wall time: **{s['total_wall_s']:.1f}s**")
    lines.append(f"- Mean / median probe latency: **{s['mean_wall_s']:.2f}s / {s['median_wall_s']:.2f}s**")
    lines.append(f"- P95 probe latency: **{s['p95_wall_s']:.2f}s**")
    lines.append(f"- Max prompt tokens evaluated on a probe: **{s['max_prompt_eval_count']}**")
    lines.append(f"- Mean prompt ingest speed: **{s['mean_prompt_tps']:.1f} tok/s**")
    lines.append(f"- Mean output speed: **{s['mean_eval_tps']:.1f} tok/s**")
    lines.append("")
    lines.append("## Results by retention gap")
    lines.append("")
    lines.append("| Gap from fact/update to probe | Passed | Total |")
    lines.append("|---|---:|---:|")
    for b, row in s["by_turn_gap"].items():
        lines.append(f"| {b} turns | {row['pass']} | {row['total']} |")
    lines.append("")
    lines.append("## Per-probe results")
    lines.append("")
    lines.append("| Probe | Category | After turn | Gap | Result | Wall s | Prompt tokens | Eval tokens | Response |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for r in result["probes"]:
        resp = r["response"].replace("|", "\\|").replace("\n", " ")[:160]
        lines.append(
            f"| `{r['id']}` | {r['category']} | {r['after_turn']} | {r.get('turn_gap')} | "
            f"{'PASS' if r['pass'] else 'FAIL'} | {r['wall_s']:.2f} | "
            f"{r['metrics'].get('prompt_eval_count')} | {r['metrics'].get('eval_count')} | {resp} |"
        )
    lines.append("")
    failures = [r for r in result["probes"] if not r["pass"]]
    if failures:
        lines.append("## Failures")
        lines.append("")
        for r in failures:
            lines.append(f"### `{r['id']}`")
            lines.append("")
            lines.append(f"Detail: `{r['detail']}`")
            lines.append("")
            lines.append("```text")
            lines.append(r["response"][:1200])
            lines.append("```")
            lines.append("")
    else:
        lines.append("No failed probes.")
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("This eval uses synthetic assistant `OK` replies for filler turns and calls the model only for probe questions. That isolates long-conversation context tracking from the model's tendency to produce verbose filler replies. Probe answers are appended to the conversation before later turns, so late consistency can be affected by the model's own earlier answers.")
    lines.append("")
    return "\n".join(lines)


def run_eval(model: str, base_url: str, turns: int, num_ctx: int, think: bool, outdir: Path) -> tuple[Path, Path]:
    rng = random.Random(20260702)
    chat = OllamaChat(base_url, model)
    probes_by_turn: dict[int, list[dict[str, Any]]] = {}
    for p in PROBES:
        if p["after_turn"] <= turns:
            probes_by_turn.setdefault(p["after_turn"], []).append(p)

    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM}]
    rows: list[dict[str, Any]] = []

    for turn in range(1, turns + 1):
        user_msg = build_turn(turn, rng)
        messages.append({"role": "user", "content": user_msg})
        # Synthetic filler reply: this makes a realistic alternating chat history
        # without spending model calls on ungraded chatter.
        messages.append({"role": "assistant", "content": "OK"})

        for probe in probes_by_turn.get(turn, []):
            probe_messages = messages + [{"role": "user", "content": probe["question"]}]
            print(f"[probe {len(rows)+1:02d}] {probe['id']} after turn {turn} messages={len(probe_messages)}", flush=True)
            started = time.perf_counter()
            raw = chat.chat(
                probe_messages,
                think=think,
                num_ctx=num_ctx,
                num_predict=probe.get("num_predict", 96),
                timeout=900,
            )
            wall = time.perf_counter() - started
            assistant_msg = raw.get("message", {"role": "assistant", "content": raw.get("response", "")})
            response = assistant_msg.get("content", "") if isinstance(assistant_msg, dict) else ""
            try:
                score, detail = probe["checker"](response)
            except Exception as e:
                score, detail = 0.0, f"checker error: {e!r}"
            row = {
                "id": probe["id"],
                "category": probe["category"],
                "after_turn": probe["after_turn"],
                "fact_turn": probe.get("fact_turn"),
                "turn_gap": probe["after_turn"] - probe.get("fact_turn", probe["after_turn"]),
                "question": probe["question"],
                "response": response,
                "score": float(score),
                "pass": bool(score >= 1.0),
                "detail": detail,
                "wall_s": wall,
                "metrics": {
                    "http_status": raw.get("http_status"),
                    "done_reason": raw.get("done_reason"),
                    "prompt_eval_count": raw.get("prompt_eval_count"),
                    "eval_count": raw.get("eval_count"),
                    "perf": raw.get("perf"),
                },
            }
            rows.append(row)
            print(f"    {'PASS' if row['pass'] else 'FAIL'} wall={wall:.2f}s prompt_tokens={row['metrics']['prompt_eval_count']} response={response!r}", flush=True)
            # Append the actual probe and actual model answer for subsequent consistency.
            messages.append({"role": "user", "content": probe["question"]})
            messages.append({"role": "assistant", "content": response})

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    result = {
        "model": model,
        "base_url": base_url,
        "started_at_utc": stamp,
        "turns": turns,
        "num_ctx": num_ctx,
        "think": think,
        "method": "synthetic filler assistant replies; model called for probes; actual probe answers appended",
        "canonical_events": CANON_EVENTS,
        "summary": summarize_result_rows(rows),
        "probes": rows,
    }
    outdir.mkdir(parents=True, exist_ok=True)
    json_path = outdir / f"conversation_context_eval_{model.replace(':','_')}_{turns}turns_{'think' if think else 'direct'}_{stamp}.json"
    md_path = outdir / f"conversation_context_eval_{model.replace(':','_')}_{turns}turns_{'think' if think else 'direct'}_{stamp}.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    md_path.write_text(render_md(result))
    return json_path, md_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "ornith:latest"))
    ap.add_argument("--base-url", default=os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ap.add_argument("--turns", type=int, default=340)
    ap.add_argument("--num-ctx", type=int, default=32768)
    ap.add_argument("--think", action="store_true")
    ap.add_argument("--outdir", default="benchmark_results")
    args = ap.parse_args()
    json_path, md_path = run_eval(args.model, args.base_url, args.turns, args.num_ctx, args.think, Path(args.outdir))
    print(json_path)
    print(md_path)
    data = json.loads(json_path.read_text())
    print(json.dumps(data["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
