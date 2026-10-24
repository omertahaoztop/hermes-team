# Architecture

## Agent = profile

Hermes has no "bot" primitive, and it does not need one. A profile
(`~/.hermes/profiles/<name>/`) already contains everything an agent needs:

```
profiles/<role>/
├── SOUL.md            identity and the shared contract
├── config.yaml        per-profile settings (no inheritance from global)
├── .env               this agent's tokens only
├── skills/<role>/     the job description
├── state/bot-<role>.json   what it has already seen
├── cron/jobs.json     schedule
├── cron/output/       every run's raw output — the evidence trail
└── memory/            session history (per profile, not shared)
```

That is the whole design. Nine directories, nine tokens, nine schedules. No
orchestrator, no queue, no shared runtime.

## Why one gateway per profile, not one multiplexed

The tempting setup is a single gateway process serving all profiles. It works,
and it is wrong for this use case: when one profile's scheduler stalls, a
multiplexed gateway makes every profile look healthy while only one is running.
Per-profile services make a dead agent obvious.

If you do multiplex (`multiplex_profiles: true`), know the cost: the scheduled
runs all live in the primary profile's process, so a stale heartbeat there means
eight agents silently stop while the gateway reports "up".

## Delivery

Each routine delivers into its own topic:

```bash
hermes -p <role> cron create <name> \
  --deliver telegram:<group_id>:<thread_id> \
  --failure-deliver local \
  --paused
```

`--failure-deliver local` is deliberate: a failed run must not spam the channel.
It lands in `cron list` and in `cron/output/`, where you look when something is
missing.

## The wrapper trap

By default every delivered message is wrapped:

```
Cronjob Response: <job>
(job_id: …)
-------------

<your actual message>

To stop or manage this job…
```

Six lines of machinery above and below a four-line report. The switch is
per-profile, because **global config does not inherit into profiles**:

```bash
hermes -p <role> config set cron.wrap_response false
```

Verify with `hermes -p <role> config get cron.wrap_response`. Setting it only in
`~/.hermes/config.yaml` does nothing for the profiles.

## Memory: shared bank, separate sessions

Two separate things that are easy to conflate:

| | Scope | Contents |
|---|---|---|
| Memory bank | shared across all agents | durable facts: preferences, system truths, recurring patterns |
| Session history | per profile | the actual conversation transcript |

An agent's learning is therefore shared; an agent's conversation is not. A
sentence you said to one agent does not appear in another's transcript, but a
durable fact learned there can be recalled by all.

Tag writes with the agent identity (`bot:<role>`) so provenance survives.

## Isolation boundaries

- **Read other agents' state, never write it.** A shared output goes through the
  owning agent.
- **Tokens per profile.** A leaked token compromises one agent, not nine.
- **No writes to external systems.** Enforced by contract, not by capability, so
  review the `SKILL.md` of any role before you let it run unattended.
