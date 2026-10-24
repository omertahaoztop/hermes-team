# Routines

One routine per report. Created paused; unpaused only after a run proves itself.

Times are host-local. Set `TZ` deliberately — if the host is UTC and you live at
UTC+3, a `30 7 * * *` schedule fires at 10:00 local and the "morning" briefing
arrives mid-morning.

## Shape

```bash
hermes -p <role> cron create <name> \
  --schedule "<cron expr>" \
  --deliver "telegram:<group_id>:<thread_id>" \
  --failure-deliver local \
  --paused \
  --prompt "<see below>"
```

- `--deliver` — one topic per agent. `General` is for conversation, not reports.
- `--failure-deliver local` — a failed run must not spam the channel; it lands in
  `cron list` and `cron/output/`.
- `--paused` — mandatory. See the rule at the bottom.

## Prompt shape

Keep the cron prompt short; the detail belongs in `SKILL.md`. The prompt's job is
to pin the run's identity and the output contract:

```text
Run the <role> routine for <slot>. Produce <n> items in the format your
SKILL.md defines: bold title, 2-3 lines of reasoning, one source link per item,
closing assessment saying which item matters most and why.
If the source returns nothing, write the empty-day summary — do not stay silent.
If the whole source is unreachable, write the one-line error, still write state.
```

Long prompts duplicate the skill and drift from it. Two or three sentences is
enough when `SKILL.md` is right.

## Settings that are not defaults

| Setting | Value | Why |
|---|---|---|
| `cron.wrap_response` | `false` | otherwise a six-line machinery header wraps every report |
| `platforms.telegram.extra.disable_link_previews` | `true` | a 4-6 link report is half-covered by the first preview card |

Both are **per profile**. Global config does not inherit.

```bash
hermes -p <role> config set cron.wrap_response false
hermes -p <role> config set platforms.telegram.extra.disable_link_previews true
```

## A sane table to start from

| Role | Schedule | Slot |
|---|---|---|
| Primary | `0 9 * * *` · `0 23 * * *` · `0 19 * * 0` | check-in, close, weekly pattern |
| Calendar | `30 7 * * *` | day plan |
| Tasks | `50 7 * * *` | stale-task reminder |
| Issues | `45 8 * * 1-5` | weekday triage |
| Anchor | `0 8 * * *` · `30 18 * * *` | anchor, evening proposal |
| News | `30 9 * * *` · `30 19 * * *` | morning, evening |
| Scout | `0 10 * * 1,4` | twice a week |
| Mail | `0 8 * * 1-5` · `30 17 * * 1-5` | weekday triage |
| Ops | on incident · daily | notes, not a schedule |

## The rule that matters

**A routine is not enabled until its first real run is inspected.**

```bash
hermes -p <role> -z "<the prompt>"         # one-shot, prints the message
ls ~/.hermes/profiles/<role>/cron/output/  # what the scheduler actually produced
hermes -p <role> cron resume <job_id>      # only now
```

"Installed" is not evidence. A `cron/output/` record plus a real message in the
topic is evidence.

## Operating

```bash
hermes -p <role> cron list          # status, last run
hermes -p <role> cron run <job_id>  # run now (paused jobs must be resumed first)
hermes -p <role> cron pause <job_id>
hermes -p <role> cron edit <job_id> --prompt "…"
```

Editing the prompt does not require a gateway restart: the config loader keys its
cache on the file signature. Editing `SOUL.md` or `SKILL.md` also takes effect on
the next run.
