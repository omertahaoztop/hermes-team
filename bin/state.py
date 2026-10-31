#!/usr/bin/env python3
"""Read, write, or initialise a per-agent state file.

One helper instead of a model-authored script per run: the deterministic part
of an agent's work belongs in deterministic code. See docs/state-management.md
for the failure this replaces.

  state.py read  <role>            # JSON to stdout (template if absent)
  state.py write <role> [file|-]   # atomic write, from file or stdin
  state.py init  <role>            # create with defaults, never overwrite

Profile path: ~/.hermes/profiles/<role>/state/bot-<role>.json
Primary profile: ~/.hermes/state/bot-<role>.json
"""
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))


def path_for(role: str) -> Path:
    p = HOME / "profiles" / role / "state" / f"bot-{role}.json"
    if not p.parent.exists() and role == "is":
        p = HOME / "state" / f"bot-{role}.json"
    return p


def template(role: str) -> dict:
    return {"schema": 2, "bot": role, "last_run": None, "last_status": None,
            "error": None, "seen": []}


def read(role: str) -> dict:
    p = path_for(role)
    if not p.exists():
        return template(role)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"ERROR: cannot read {p}: {e} (a write moves unparseable JSON to {p.name}.corrupt-<ts>)")


def backup_if_corrupt(p: Path) -> None:
    try:
        json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return
    except ValueError:
        bak = p.with_name(f"{p.name}.corrupt-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}")
        os.replace(p, bak)
        print(f"backed up corrupt state: {bak}", file=sys.stderr)


def write(role: str, data: dict) -> None:
    p = path_for(role)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=f".{role}-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        backup_if_corrupt(p)
        os.replace(tmp, p)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, role = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", role):
        sys.exit(f"ERROR: invalid role name: {role!r}")

    if cmd == "read":
        print(json.dumps(read(role), ensure_ascii=False, indent=2))
    elif cmd == "init":
        p = path_for(role)
        if p.exists():
            print(f"exists: {p}")
        else:
            write(role, template(role))
            print(f"created: {p}")
    elif cmd == "write":
        src = sys.argv[3] if len(sys.argv) > 3 else "-"
        try:
            raw = sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError) as e:
            sys.exit(f"ERROR: input is not JSON: {e}")
        if not isinstance(data, dict):
            sys.exit("ERROR: root must be an object")
        data.setdefault("schema", 2)
        data.setdefault("bot", role)
        write(role, data)
        print(f"written: {path_for(role)}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
