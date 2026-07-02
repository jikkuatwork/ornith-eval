#!/usr/bin/env python3
"""Natural-language long-conversation memory eval for Ollama models.

Unlike conversation_context_eval_ornith.py, this version avoids explicit CANON/UPDATE
labels in the transcript. It uses natural phrasing, corrections, side stories, and
jokes. The assistant replies to filler turns are synthetic short acks; the model is
called only for memory probes so we can measure context retrieval speed cleanly.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import re
import statistics
import time
from pathlib import Path
from typing import Any, Callable

import requests


def ns_to_s(v):
    return None if v is None else float(v) / 1_000_000_000.0


def tps(count, duration_ns):
    if not count or not duration_ns:
        return None
    s = duration_ns / 1_000_000_000.0
    return count / s if s > 0 else None


class OllamaChat:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.session = requests.Session()

    def chat(self, messages, *, num_ctx: int, num_predict: int, think: bool = False):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": think,
            "keep_alive": "10m",
            "options": {"temperature": 0, "seed": 778, "num_ctx": num_ctx, "num_predict": num_predict},
        }
        start = time.perf_counter()
        r = self.session.post(f"{self.base_url}/api/chat", json=payload, timeout=900)
        wall = time.perf_counter() - start
        out = r.json()
        out["wall_s"] = wall
        out["http_status"] = r.status_code
        out["perf"] = {
            "load_s": ns_to_s(out.get("load_duration")),
            "prompt_eval_s": ns_to_s(out.get("prompt_eval_duration")),
            "eval_s": ns_to_s(out.get("eval_duration")),
            "prompt_tps": tps(out.get("prompt_eval_count"), out.get("prompt_eval_duration")),
            "eval_tps": tps(out.get("eval_count"), out.get("eval_duration")),
        }
        return out


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def exact(expected: str):
    def check(resp):
        low = norm(resp).strip(". '")
        ok = low == expected.lower() or expected.lower() in low
        return (1.0 if ok else 0.0, f"expected={expected!r}; got={resp[:180]!r}")
    return check


def has_all(*terms):
    def check(resp):
        low = norm(resp)
        missing = [t for t in terms if t.lower() not in low]
        return (1.0 if not missing else 0.0, f"missing={missing}; got={resp[:180]!r}")
    return check


def has_number(n: str):
    def check(resp):
        nums = re.findall(r"\d+", resp)
        return (1.0 if n in nums or n in resp else 0.0, f"nums={nums}; expected={n}; got={resp[:180]!r}")
    return check


def combo(slots: dict[str, list[str]]):
    def check(resp):
        low = norm(resp)
        missing = [slot for slot, vals in slots.items() if not any(v.lower() in low for v in vals)]
        return (1.0 if not missing else 0.0, f"missing_slots={missing}; got={resp[:220]!r}")
    return check


SYSTEM = """You are having a long, natural conversation with the user.
Remember earlier details, corrections, ownership transfers, and small stories.
Some later turns are unrelated side stories or jokes, so bind facts to the right person/object.
When the user asks a memory question, answer briefly and directly.
"""

EVENTS = {
    2: "I want to tell you a tiny story for later: Tom was playing with his red ball when he saw a yellow ox far away, and he went back home surprised.",
    17: "Another detail to remember: Elena lent Priya her striped scarf before Priya boarded the train. Elena kept the black umbrella with herself.",
    28: "For Maya's errand, she first put the brass key inside the blue vase.",
    39: "The lab cabinet code, at this point in the chat, is 4192.",
    53: "Nora's mentor is Ivo. Ivo likes the codeword glacier.",
    61: "Nora lent the copper compass to Jules after the seminar.",
    79: "Correction about Maya: she moved the brass key from the blue vase into the green drawer, so the vase is no longer where the key is.",
    101: "Small update: the lab cabinet code changed from 4192 to 7305. Please use 7305 as the current code now.",
    116: "Nina packed three boxes: the red box has the map, the blue box has the lens, and the green box has the coin.",
    132: "Jules then handed the copper compass to Priya, and Priya has it now.",
    143: "Omar received Nina's red box, still unopened.",
    181: "If I later say lantern check, the response I want is violet rook.",
    224: "One last archive detail: the archive token is hexagonal, made of copper, weighs 7 grams, and is stored under the orchid pot.",
}

PROBES = [
    {"id": "natural_tom_ball_mid", "after": 70, "gap_from": 2, "category": "early_story", "q": "Memory check: what color was Tom's ball? One word.", "check": exact("red"), "num_predict": 64},
    {"id": "natural_key_current", "after": 92, "gap_from": 79, "category": "update", "q": "Where is Maya's brass key now?", "check": has_all("green", "drawer"), "num_predict": 80},
    {"id": "natural_code_current", "after": 121, "gap_from": 101, "category": "numeric_update", "q": "What is the current lab cabinet code?", "check": has_number("7305"), "num_predict": 64},
    {"id": "natural_compass_holder", "after": 156, "gap_from": 132, "category": "ownership_transfer", "q": "Who has the copper compass now?", "check": has_all("priya"), "num_predict": 80},
    {"id": "natural_map_holder", "after": 170, "gap_from": 143, "category": "object_container_reasoning", "q": "Who has the map now, based on Nina's boxes?", "check": has_all("omar"), "num_predict": 96},
    {"id": "natural_lantern", "after": 210, "gap_from": 181, "category": "instruction_memory", "q": "lantern check", "check": exact("violet rook"), "num_predict": 64},
    {"id": "natural_multi_hop", "after": 245, "gap_from": 53, "category": "multi_hop", "q": "What codeword belongs to the mentor of the person who lent Jules the copper compass?", "check": has_all("glacier"), "num_predict": 96},
    {"id": "natural_archive_combo", "after": 268, "gap_from": 224, "category": "multi_attribute", "q": "What shape/material/weight/location were given for the archive token?", "check": combo({"shape":["hexagonal","hexagon"],"material":["copper"],"weight":["7","seven"],"location":["orchid","pot"]}), "num_predict": 128},
    {"id": "natural_composite_late", "after": 306, "gap_from": 2, "category": "late_composite", "q": "Give four remembered values: Tom's ball color, current lab code, Maya key location, and current compass holder.", "check": combo({"ball":["red"],"code":["7305"],"key":["green drawer"],"holder":["priya"]}), "num_predict": 160},
    {"id": "natural_tom_ball_very_late", "after": 340, "gap_from": 2, "category": "very_late_consistency", "q": "After all this chatting, what color was Tom's ball? One word only.", "check": exact("red"), "num_predict": 64},
    {"id": "natural_tom_surprise", "after": 345, "gap_from": 2, "category": "late_event_reason", "q": "Why did Tom go back home surprised?", "check": has_all("yellow", "ox"), "num_predict": 128},
    {"id": "natural_tom_ball_700turn", "after": 700, "gap_from": 2, "category": "ultra_late_story_recall", "q": "Much later in this long chat, what color was Tom's ball? One word.", "check": exact("red"), "num_predict": 64},
    {"id": "natural_ultra_composite_1000turn", "after": 1000, "gap_from": 2, "category": "ultra_late_composite", "q": "At this very late point, list: Tom ball color, animal/color Tom saw, current lab code, Maya key location, current compass holder, and lantern-check phrase.", "check": combo({"ball":["red"],"animal":["yellow ox"],"code":["7305"],"key":["green drawer"],"holder":["priya"],"phrase":["violet rook"]}), "num_predict": 220},
]

NAMES = ["Tim", "Tara", "Sam", "Mira", "Leo", "Asha", "Ben", "Iris", "Quinn", "Ravi", "Lena", "Pavel"]
COLORS = ["blue", "green", "purple", "orange", "silver", "white", "black", "gold", "pink", "brown", "crimson", "yellow", "red"]
OBJECTS = ["kite", "marble", "cup", "notebook", "lantern", "rope", "basket", "puzzle", "drum", "coin", "shell", "hat", "ball"]
ANIMALS = ["goat", "fox", "yak", "owl", "horse", "cat", "dog", "mule", "crane", "lizard", "ox"]
PLACES = ["garden", "library", "station", "attic", "market", "courtyard", "studio", "workshop", "balcony"]


def filler(turn: int, rng: random.Random) -> str:
    name = rng.choice(NAMES)
    color = rng.choice(COLORS)
    obj = rng.choice(OBJECTS)
    animal = rng.choice(ANIMALS)
    place = rng.choice(PLACES)
    options = [
        f"Side note {turn}: {name} saw a {color} {animal} near the {place}, unrelated to the earlier Tom story.",
        f"Random aside {turn}: {name} was carrying a {color} {obj}; that belongs to {name}'s story, not anyone else's.",
        f"A joke during the chat: maybe the lab code is {rng.randint(1000,9999)}, but no, that was just a joke, not the real lab update.",
        f"We also talked about {name}'s {color} ball for a moment, separate from Tom.",
        f"A side puzzle used the phrase {rng.choice(['amber owl','blue rook','violet kite','silver lantern'])}, but it was not the lantern-check phrase.",
        f"Someone mentioned a spare key in a {color} {obj}, but it was not Maya's brass key.",
    ]
    return rng.choice(options)


def summarize(rows):
    walls = [r["wall_s"] for r in rows]
    prompt_counts = [r["metrics"].get("prompt_eval_count") for r in rows if r["metrics"].get("prompt_eval_count") is not None]
    prompt_tps_vals = [r["metrics"].get("perf", {}).get("prompt_tps") for r in rows if r["metrics"].get("perf", {}).get("prompt_tps")]
    eval_tps_vals = [r["metrics"].get("perf", {}).get("eval_tps") for r in rows if r["metrics"].get("perf", {}).get("eval_tps")]
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], {"pass":0,"total":0})
        by_cat[r["category"]]["pass"] += int(r["pass"])
        by_cat[r["category"]]["total"] += 1
    return {
        "pass": sum(1 for r in rows if r["pass"]),
        "total": len(rows),
        "accuracy": sum(r["score"] for r in rows) / len(rows),
        "by_category": by_cat,
        "total_wall_s": sum(walls),
        "mean_wall_s": statistics.mean(walls),
        "median_wall_s": statistics.median(walls),
        "max_prompt_eval_count": max(prompt_counts) if prompt_counts else None,
        "mean_prompt_eval_count": statistics.mean(prompt_counts) if prompt_counts else None,
        "mean_prompt_tps": statistics.mean(prompt_tps_vals) if prompt_tps_vals else None,
        "mean_eval_tps": statistics.mean(eval_tps_vals) if eval_tps_vals else None,
    }


def render_md(result):
    s = result["summary"]
    lines = [
        f"# Natural Long-Conversation Context Eval: `{result['model']}`",
        "",
        f"Turns: **{result['turns']}**; probes: **{s['total']}**; mode: `think:{str(result['think']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Accuracy: **{s['pass']}/{s['total']}** (**{s['accuracy']*100:.1f}%**)",
        f"- Total probe wall time: **{s['total_wall_s']:.1f}s**",
        f"- Mean/median probe latency: **{s['mean_wall_s']:.2f}s / {s['median_wall_s']:.2f}s**",
        f"- Max prompt tokens evaluated: **{s['max_prompt_eval_count']}**",
        f"- Mean prompt ingest speed: **{s['mean_prompt_tps']:.1f} tok/s**",
        f"- Mean output speed: **{s['mean_eval_tps']:.1f} tok/s**",
        "",
        "## Per-probe results",
        "",
        "| Probe | Category | After turn | Gap | Result | Wall s | Prompt tokens | Response |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in result["probes"]:
        resp = r["response"].replace("|", "\\|").replace("\n", " ")[:180]
        lines.append(f"| `{r['id']}` | {r['category']} | {r['after_turn']} | {r['turn_gap']} | {'PASS' if r['pass'] else 'FAIL'} | {r['wall_s']:.2f} | {r['metrics'].get('prompt_eval_count')} | {resp} |")
    fails = [r for r in result["probes"] if not r["pass"]]
    if fails:
        lines += ["", "## Failures", ""]
        for r in fails:
            lines += [f"### `{r['id']}`", "", f"Detail: `{r['detail']}`", "", "```text", r["response"][:1200], "```", ""]
    else:
        lines += ["", "No failed probes.", ""]
    lines += ["", "## Method note", "", "This version uses natural phrasing rather than explicit CANON/UPDATE labels. It still uses synthetic short assistant acknowledgements for filler turns and calls the model only at probe points."]
    return "\n".join(lines) + "\n"


def run(model, base_url, turns, num_ctx, think, outdir):
    rng = random.Random(20260703)
    chat = OllamaChat(base_url, model)
    by_turn = {}
    for p in PROBES:
        if p["after"] <= turns:
            by_turn.setdefault(p["after"], []).append(p)
    messages = [{"role":"system","content":SYSTEM}]
    rows = []
    for turn in range(1, turns+1):
        content = EVENTS.get(turn) or filler(turn, rng)
        messages.append({"role":"user", "content": content})
        messages.append({"role":"assistant", "content":"Got it."})
        for p in by_turn.get(turn, []):
            probe_messages = messages + [{"role":"user", "content":p["q"]}]
            print(f"[probe {len(rows)+1:02d}] {p['id']} after turn {turn} messages={len(probe_messages)}", flush=True)
            raw = chat.chat(probe_messages, num_ctx=num_ctx, num_predict=p["num_predict"], think=think)
            msg = raw.get("message", {}).get("content", "")
            score, detail = p["check"](msg)
            row = {
                "id": p["id"], "category": p["category"], "after_turn": p["after"], "fact_turn": p["gap_from"],
                "turn_gap": p["after"] - p["gap_from"], "question": p["q"], "response": msg,
                "score": float(score), "pass": bool(score >= 1), "detail": detail, "wall_s": raw["wall_s"],
                "metrics": {"http_status": raw.get("http_status"), "done_reason": raw.get("done_reason"), "prompt_eval_count": raw.get("prompt_eval_count"), "eval_count": raw.get("eval_count"), "perf": raw.get("perf")},
            }
            rows.append(row)
            print(f"    {'PASS' if row['pass'] else 'FAIL'} wall={row['wall_s']:.2f}s prompt_tokens={row['metrics']['prompt_eval_count']} response={msg!r}", flush=True)
            messages.append({"role":"user", "content":p["q"]})
            messages.append({"role":"assistant", "content":msg})
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    result = {"model":model,"base_url":base_url,"started_at_utc":stamp,"turns":turns,"num_ctx":num_ctx,"think":think,"method":"natural transcript; synthetic filler acks; model called for probes","events":EVENTS,"summary":summarize(rows),"probes":rows}
    outdir.mkdir(parents=True, exist_ok=True)
    jp = outdir / f"conversation_context_eval_natural_{model.replace(':','_')}_{turns}turns_{'think' if think else 'direct'}_{stamp}.json"
    mp = outdir / f"conversation_context_eval_natural_{model.replace(':','_')}_{turns}turns_{'think' if think else 'direct'}_{stamp}.md"
    jp.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    mp.write_text(render_md(result))
    return jp, mp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="ornith:latest")
    ap.add_argument("--base-url", default="http://127.0.0.1:11434")
    ap.add_argument("--turns", type=int, default=350)
    ap.add_argument("--num-ctx", type=int, default=32768)
    ap.add_argument("--think", action="store_true")
    ap.add_argument("--outdir", default="benchmark_results")
    args = ap.parse_args()
    jp, mp = run(args.model, args.base_url, args.turns, args.num_ctx, args.think, Path(args.outdir))
    print(jp)
    print(mp)
    print(json.dumps(json.loads(jp.read_text())["summary"], indent=2))

if __name__ == "__main__":
    main()
