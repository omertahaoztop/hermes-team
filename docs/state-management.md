# State management

## The problem

Each agent must remember what it already reported, or it repeats itself forever.
The obvious implementation is: at the end of a run, the model writes a small
Python script, loads the JSON, appends, and writes it back atomically.

That implementation fails, in a way worth documenting because it is silent.

### What actually happens

The write guard refuses the second write of the same path:

```
Refusing to overwrite ~/.hermes/profiles/news/cache/scratch/verify.py:
exists but this task has not seen its full current content.
The file was NOT modified.
```

The guard is correct. It exists so a stale conversation copy cannot clobber
current disk content. But the agent's response is what makes it a real failure:
it treats the refusal as a name collision and **writes the same script under a
new name**.

Observed over a few days:

| Profile | Scratch files | Names |
|---|---|---|
| news | 7 | `verify.py`, `verify2.py`, `read2.py`, `write-state.py`, `state_write.py` |
| mail | 9 | `update_state.py`, `update_state2.py`, … |
| scout | 31 | `j1.py` … `j24.py`, `gh.py` |
| primary | 5 MB | snapshots, locks, per-run scripts |

Every role accumulates near-duplicates of the same 40 lines, and the state file
is written by a different, unreviewed program each run.

## The fix: one helper

```bash
python3 ~/.hermes/scripts/state.py read <role>
python3 ~/.hermes/scripts/state.py write <role> < new.json
python3 ~/.hermes/scripts/state.py init <role>
```

`bin/state.py` is ~110 lines: atomic write via a temp file in the same directory,
`os.replace`, schema defaults, and a corrupt-JSON path that never resets: `read`
refuses and exits, and the next `write`, once the new file is fully written, moves the unparseable file aside to
`bot-<role>.json.corrupt-<UTC timestamp>`. No model-authored script, no `.tmp` bookkeeping,
no name collisions.

The contract now says, in the block every agent carries:

> Use the shared helper. Do not write your own Python script for state: the
> write guard will reject the second write and the run dies with
> `Refusing to overwrite`. Do not leave `state_write.py` or `verify2.py` behind
> in the scratch directory.

### Why a helper and not "be careful"

Because the failure is not a reasoning error, it is an architectural one. Any
design where a language model generates the program that performs a
deterministic, idempotent operation will produce a new program every time. The
deterministic operation belongs in deterministic code.

## Verification

The round trip must be exact and leave no residue:

```bash
python3 ~/.hermes/scripts/state.py read news > /tmp/a.json
python3 ~/.hermes/scripts/state.py write news < /tmp/a.json
python3 ~/.hermes/scripts/state.py read news | diff -q /tmp/a.json - && echo ROUNDTRIP_OK
ls ~/.hermes/profiles/news/state/   # no *.tmp left behind
```

After switching a real role to the helper, a live run should add **zero** files
to `cache/scratch/` and still advance the state:

```bash
ls ~/.hermes/profiles/news/cache/scratch | wc -l   # unchanged
python3 ~/.hermes/scripts/state.py read news | jq '.seen | length'   # grew
```

## Schema

State shapes differ per role — that is fine, the helper is schema-agnostic and
only enforces the common fields:

```json
{
  "schema": 2,
  "bot": "<role>",
  "last_run": "2026-10-24T23:43:18+03:00",
  "last_status": "ok",
  "error": null,
  "<role-specific>": []
}
```

Rules the helper cannot enforce, so keep them in the `SKILL.md`:

- Prune entries older than ~90 days, or the file grows without bound.
- On corrupt JSON, report it in the `error` field (`state.py write` already moves the old file aside) — never reset silently.
- Never write secrets, mail bodies, or address books into state.

## Suggestion ledger

Most roles suggest something every run, and without a record nobody knows
whether any of it was right. Common rule 10 gives every agent the same list in
its state:

```json
"suggestions": [
  {"date": "2026-11-01", "ref": "#44011", "status": "proposed"},
  {"date": "2026-10-28", "ref": "walk-20min", "status": "worked"}
]
```

`status` only moves forward: `proposed` → `accepted` / `declined` → `worked` /
`failed`. A suggestion closes when its effect is known, not when it is sent.

`bin/scorecard.py [days]` reads every profile's `suggestions[]` and prints, per
role, how many were made recently and how many landed (`accepted` or `worked`).
It is read-only. Run it from the primary agent's weekly routine and put the
numbers in the report: the role with the lowest hit rate is the one to
recalibrate. A role whose rows are all still `proposed` is not failing; it is
not recording answers, and the report should say so.

The idea comes from the recommendation ledger in
[mattabate/life-distributable](https://github.com/mattabate/life-distributable)
(`hub/internal/recs`), which keeps a separate decision and outcome per
recommendation so that future advice is based on a track record.

## Scratch directory

`~/.hermes/profiles/<role>/cache/scratch/` is `TMPDIR` for the agent's
subprocesses and is pruned after 24 idle hours (`SCRATCH_MAX_IDLE_HOURS`).
It is for transient work only. If it is growing across runs, an agent is
creating files it should not — that is the signal this whole document is about.
