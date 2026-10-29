# Output contract

Every agent in the team carries the same block at the top of its `SOUL.md`.
It is the whole reason the team is readable. Edit `templates/common-rules.md`
and re-distribute; do not hand-edit nine files.

## The block

```text
COMMON RULES (apply to every run):
1. Change nothing in external systems: no comments in the tracker, no status
   updates, no PRs, no mail, no calendar writes. If a write is needed, propose it.
   ONE EXCEPTION: the primary agent's bad-day deferral. No other agent may use it.
2. Never write a sentence without a source. Every line carries evidence: a job id,
   a link, or file:field.
3. If a source returns empty or errors, write "no data". Do not read an empty
   answer as zero, and never invent.
4. PRODUCE A MESSAGE ON EVERY RUN. Do NOT write `[SILENT]`. Two special cases:
   (a) if a source is entirely unreachable, write ONE LINE OF ERROR — `[SILENT]`
       makes the gateway suppress the whole output, so the error report is
       silently swallowed too;
   (b) if there is genuinely nothing, write an "empty day" summary: what you
       looked at, what did not appear, what you will look at next run.
       Silence is not the default; feeding is the default.
5. Writing your own state file is MANDATORY and the only exception to rule 1.
   Read any agent's file, write only your own. Never write secrets.
   Use the shared helper, never a hand-rolled script.
6. At the end of every run write last_run; on error write the error field.
   Do not pass silently.
7. Group rule: speak only when addressed with @. No spontaneous messages
   (routine output excepted).
8. Output: one message, Markdown. Each item is a bold title, 2–3 lines of
   reasoning, and a source link. No tables, no emoji, no greetings, no
   platitudes. Write prose worth reading — not a telegram-style stub.
9. Write in the language you chose for the team. State uncertainty explicitly:
   "unverified", "not readable from the source".
```

## Why `[SILENT]` was removed

The original contract said: if there is nothing new, reply `[SILENT]` and the
gateway delivers nothing. It also said "but still write the error line".

Those two rules cannot coexist. The gateway checks the marker on the **first or
last line** of the response and, if found, suppresses the entire output:

```python
# gateway/response_filters.py::is_autonomous_silence_response
# if the marker appears on the first or last line, the whole response is dropped
```

So `[SILENT]` plus an error line means the error is dropped too. An agent whose
credential expired would report nothing, for days, and look exactly like an
agent with no news.

The contract now inverts the default: **every run produces a message**. A quiet
day gets an "empty day" summary. The only remaining silence is the primary
agent's bad-day mode, where the day's message budget was deliberately spent.

## Volume per role

Depth is set per role, not globally — a mail triage pass legitimately has more
items than a calendar briefing.

| Role | Items per run |
|---|---|
| Primary | narrative + one weekly pattern |
| Calendar | 12 plan lines |
| Tasks | 4–6 |
| Issues | 4–5 urgent + 4–6 suggestions |
| Anchor | 3–5 tasks / 2–3 proposals |
| News | 4–6 signals |
| Scout | 4–6 candidates |
| Mail | 5–8 items |
| Ops | 4–8 items |

## Message shape

```markdown
**News · 20.10 Mon 09:30**

**1. OpenAI acquires Orchestra Bio**
Announcement dated 20.10 in the feed; the target's scope is not readable
from the feed. Consolidation by acquisition changes the terms for anyone
building independent tooling on top. → [openai.com](https://…)

**2. …**

> My read: item 3 matters most today, because it is the only one that needs
> action on a running system. Item 5 carried no date, so I cannot claim it
> is fresh.
```

Two details that matter in practice, both learned the hard way:

- **Never write a bare URL or `<url>`.** Telegram renders the angle brackets
  literally. Use `[short name](url)`.
- **Never use `_underscore italics_`.** The adapter converts `**bold**` and
  `*italic*`; underscores leak through as literal characters. The closing
  error/note line uses `*single asterisks*`.

## Monitor-gated runs

A schedule alone forces the model to wake up and decide there is nothing to say.
That costs tokens and invites invented content. The alternative is a monitor
script: the scheduler runs a cheap command every tick, and the agent runs **only
when the output changed**.

```bash
hermes -p bridge cron create "0 * * * *" \
  "Report only the lines in the trigger output. Do not re-read the source." \
  --name bridge-live --monitor-script watch.sh --deliver "matrix:!roomid"
```

Rules that keep this honest:

- The trigger output **is** the data. Forbid re-reading: a second read usually
  races the cursor and produces "nothing new" for a run that did fire.
- Silence is the correct output when the trigger is empty; forbid filler such as
  "no new records" — that is what a chatty bot looks like.
- Cap the work: a fetch limit plus a match limit. Anything past the cap is
  dropped this tick (the cursor still advances), so the caps must be sized for
  your worst hour, not your average one.
