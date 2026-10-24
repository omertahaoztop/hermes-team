# <Role> — job description

One job: <what this agent looks at and what it emits>. Nothing else belongs here.

## Sources

| What | How |
|---|---|
| <source> | `<collector command>` → `<output file>` |
| Credential | `<ENV_VAR>` from this profile's `.env` |

The collector is deterministic and time-stamped. It never gets edited by the
model, and its output is never overwritten in place — the previous run is kept
as `.previous` so a diff is always possible.

Exit codes: `0` at least one source read, `2` no source readable (emit the
one-line error, see common rules 4a).

## Run order

1. **Collect.** Run the collector; note the exit code and its summary line.
2. **Read state.** `python3 ~/.hermes/scripts/state.py read <role>` — what has
   already been reported.
3. **Select.** Pick <n> items by the ranking below. Drop anything in state or
   older than <window>.
4. **Write the message** in the shape below.
5. **Update state** — one call:
   `python3 ~/.hermes/scripts/state.py write <role>` with JSON on stdin.

Do not skip step 5, and do not hand-roll it. Writing a fresh Python script each
run is what produces `Refusing to overwrite` and duplicate files in scratch.

## Ranking

1. <first criterion — usually urgency or age>
2. <second criterion — usually impact>
3. <tie-breaker>

State your ranking in the closing assessment, so the reader can disagree with the
order rather than just consume it.

## Output shape

```markdown
**<Role> · dd.mm <Day> hh:mm**

**1. <title>**
<2-3 lines: what it is, why it matters to this specific reader, what you could
not verify.> → [source](url)

**2. <title>**
…

> <One paragraph: what you ranked first and why, what you dropped and why.>

*<note: source counts, what was unreadable, what was partial>*
```

Count: <n> items. Never fewer without saying why; never more.

## Failure modes

| Situation | What you write |
|---|---|
| Source entirely unreachable | One line: `<Role>: run incomplete — <first error from the collector>`. Still write state. |
| Source partial | Normal report, plus `*partial: <n> of <m> sources read*` in the note line. |
| Nothing new | "Empty day" summary: what you looked at, nothing qualified, what you will check next run. |
| Credential rejected (401) | One line naming the credential variable. Stop; do not retry with guesses. |

## Never

- Send, reply, comment, update status, open a PR, or write to a calendar.
- Report an item you did not read from the source.
- Use `[SILENT]` outside the primary agent's bad-day mode.
- Leave `*.py` files in `cache/scratch/`.
