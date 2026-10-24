# hermes-team

A team of personal AI agents that live in a Telegram supergroup, built on
[Hermes Agent](https://github.com/NousResearch/hermes-agent). One agent per role, one topic
per agent, one scheduled run that produces something worth reading.

The core idea: an agent is not a chatbot you visit. It is a **profile** with its
own identity, instructions, memory, state and schedule — and it reports to you
on a rhythm. Nine roles, nine topics, nothing shared but a memory bank.

```
                    Telegram supergroup
  ┌──────────────────────────────────────────────────────┐
  │  General        ← you talk to any agent here         │
  │  ─────────────────────────────────────────────────   │
  │  Calendar  Task  Issue  Anchor  News  Scout  Mail …  │
  └──────────────────────────────────────────────────────┘
        ▲          ▲          ▲          ▲
        │          │          │          │
   ┌────┴───┐ ┌────┴───┐ ┌────┴───┐ ┌────┴───┐
   │profile │ │profile │ │profile │ │profile │   each: SOUL.md, SKILL.md,
   │calend. │ │ tasks  │ │ issues │ │  news  │   .env, state/, cron/, memory
   └────────┘ └────────┘ └────────┘ └────────┘
```

## Why this shape

| Decision | Reason |
|---|---|
| Agent = profile, not new primitive | Isolation for free: separate token, skill, state, memory, schedule |
| One topic per agent | Five morning reports do not bury a conversation; open the topic or ignore it |
| Read-only by default | An agent that can write to your tracker is an agent you must audit. Suggest, never apply |
| Every run produces a message | A silent agent is indistinguishable from a broken one. See [why `[SILENT]` was removed](docs/output-contract.md) |
| Evidence or nothing | Every line carries a job id, a link, or `file:field`. No unsourced sentences |
| Deterministic collectors | The model interprets data; it never fetches it. Fetching is a script's job |

## The nine roles

Generic roles — each is a template you fill in with your own sources. See
[docs/bot-roles.md](docs/bot-roles.md) for what each one reads and emits.

| # | Role | Reads | Emits |
|---|---|---|---|
| 1 | **Primary** | your own notes, check-ins | daily check-in, weekly pattern |
| 2 | **Calendar** | ICS feeds | day plan, conflicts, prep |
| 3 | **Tasks** | task tracker API | 4–6 stale-task reminders |
| 4 | **Issues** | issue tracker API | open/overdue + suggestions |
| 5 | **Anchor** | activity log, energy | morning anchor, evening proposal |
| 6 | **News** | RSS/Atom, HN | 4–6 signals, each argued |
| 7 | **Scout** | GitHub, package indexes | 4–6 repos worth attention |
| 8 | **Mail** | IMAP/Gmail | 5–8 triaged items, never sends |
| 9 | **Ops** | incident notes, runbooks | postmortem skeleton, prod steps |

## Quick start

```bash
git clone https://github.com/<you>/hermes-team && cd hermes-team
cp templates/SOUL.template.md   ~/.hermes/profiles/<role>/SOUL.md
cp templates/SKILL.template.md  ~/.hermes/profiles/<role>/skills/<role>/SKILL.md
install -m 755 bin/state.py ~/.hermes/scripts/state.py
```

Then create one routine, paused, and only unpause it after the first run proves
itself. Full sequence in [docs/setup.md](docs/setup.md).

## What is in here

| Path | What |
|---|---|
| `docs/architecture.md` | Why profile-per-agent, how the gateway is wired |
| `docs/bot-roles.md` | The nine roles: sources, output shape, failure mode |
| `docs/output-contract.md` | The shared contract every agent's `SOUL.md` embeds |
| `docs/state-management.md` | One helper for state writes, and the bug that forced it |
| `docs/setup.md` | BotFather → profile → soul → skill → routine |
| `templates/` | `SOUL`, `SKILL`, common rules, routine table |
| `bin/state.py` | Atomic read/write for per-agent state files |
| `bin/deploy.sh` | Push `templates/` into `~/.hermes/profiles/` |

## Hard rules this repo encodes

- **No secrets in git.** Tokens live in the profile's `.env`, never here.
- **Nothing is sent to the outside world.** No mail, no comments, no PRs, no
  calendar writes. Reading and reporting only.
- **A routine stays paused until a run proves itself.** "Installed" is not
  evidence; a `cron/output/` record and a real message are.
- **Delete the agent nobody reads.** An unread agent is negative value.

## License

MIT — see [LICENSE](LICENSE).
