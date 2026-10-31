#!/usr/bin/env python3
"""Count every agent's suggestions[] and how many landed, read-only: scorecard.py [days, default 7]"""
import json
import os
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
if HOME.parent.name == "profiles":
    HOME = HOME.parent.parent

LANDED = {"accepted", "worked"}


def line(items: list, since: str, days: int) -> str:
    recent = Counter(s.get("status", "proposed") for s in items if s.get("date", "") >= since)
    total = Counter(s.get("status", "proposed") for s in items)
    spread = ", ".join(f"{k} {n}" for k, n in recent.most_common())
    landed = sum(total[k] for k in LANDED)
    out = f"last {days}d {sum(recent.values())}" + (f" ({spread})" if spread else "")
    out += f" · all {len(items)}, landed {landed} ({round(100 * landed / len(items))}%)"
    if total["proposed"] == len(items):
        out += ", no outcome recorded yet"
    return out


def main() -> None:
    try:
        days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    except ValueError:
        sys.exit("usage: scorecard.py [days]")
    since = (date.today() - timedelta(days=days)).isoformat()
    files = sorted(HOME.glob("profiles/*/state/bot-*.json")) + sorted(HOME.glob("state/bot-*.json"))
    shown = 0
    for p in files:
        role = p.stem.removeprefix("bot-")
        try:
            items = json.loads(p.read_text(encoding="utf-8")).get("suggestions") or []
        except (OSError, ValueError) as e:
            print(f"{role}: unreadable ({e})")
            continue
        if items:
            print(f"{role}: {line(items, since, days)}")
            shown += 1
    if not shown:
        print("no agent has suggestions[] in its state yet")


if __name__ == "__main__":
    main()
