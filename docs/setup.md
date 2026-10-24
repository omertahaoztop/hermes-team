# Setup

Assumes Hermes Agent is installed and `hermes` runs as the service user. Replace
`<role>` with your agent names (`calendar`, `tasks`, `news`, …).

## 1. Create the bots

One bot per role in BotFather. Turn **privacy mode off** in each, otherwise the
bot cannot see group messages it was not explicitly mentioned in.

```bash
# per role, one line each: no labels needed
<token_calendar>
<token_tasks>
<token_news>
```

Verify every token is live before going further:

```bash
TOKEN=…; curl -s "https://api.telegram.org/bot$TOKEN/getMe" | jq .ok
```

## 2. Create the profiles

```bash
for role in calendar tasks news; do
  hermes profile create "$role"
done
```

Each new profile's `.env` starts empty and will fail with `HTTP 401: Invalid API
key` until you add a model key. Copy the token into **that profile's** `.env`
only:

```bash
echo "TELEGRAM_BOT_TOKEN=<token_calendar>" >> ~/.hermes/profiles/calendar/.env
chmod 600 ~/.hermes/profiles/*/.env
```

## 3. Create the group

A Telegram supergroup with **forum topics enabled**. One topic per role, plus one
`General` for talking to any bot.

Add all bots **after** converting the group to a supergroup — adding them during
the conversion silently drops memberships.

Topic ids end up in `~/.hermes/state/<team>-topics.json`, one line per role:

```json
{ "calendar": 12, "tasks": 14, "news": 9 }
```

## 4. Install the identity and skill

```bash
install -m 644 templates/SOUL.template.md  ~/.hermes/profiles/calendar/SOUL.md
install -d -m 755                          ~/.hermes/profiles/calendar/skills/calendar
install -m 644 templates/SKILL.template.md ~/.hermes/profiles/calendar/skills/calendar/SKILL.md
install -m 755 bin/state.py                ~/.hermes/scripts/state.py
```

`SOUL.md` must contain the common rules block. If you edit the block, edit
`templates/common-rules.md` and re-distribute — do not hand-edit per profile,
they will drift.

## 5. Per-profile settings

```bash
for role in calendar tasks news; do
  hermes -p "$role" config set cron.wrap_response false
  hermes -p "$role" config set platforms.telegram.extra.disable_link_previews true
done
```

Both matter for readability:

- `wrap_response: true` adds a six-line `Cronjob Response:` header and a "to stop
  or manage this job" footer around every message.
- Link previews expand the first link into a large card and eat half the message
  when a report carries four to six links.

**Global config does not inherit into profiles.** Setting these once in
`~/.hermes/config.yaml` has no effect. Verify per profile:

```bash
hermes -p calendar config get cron.wrap_response   # → false
```

## 6. Create the routine, paused

```bash
hermes -p calendar cron create calendar-day \
  --schedule "30 7 * * *" \
  --deliver "telegram:<group_id>:<thread_id>" \
  --failure-deliver local \
  --paused \
  --prompt "…"
```

Times are local to the host; set `TZ` deliberately.

## 7. Prove it before unpausing

```bash
# one-shot, output only
hermes -p calendar -z "run the calendar briefing"

# inspect what the scheduler actually produced
ls ~/.hermes/profiles/calendar/cron/output/<job_id>/
```

Then, and only then:

```bash
hermes -p calendar cron resume <job_id>
```

## 8. Verify the deployment

```bash
hermes -p calendar cron list            # schedule, status, last run
hermes -p calendar config get cron.wrap_response
ls ~/.hermes/profiles/                       # one directory per role
python3 ~/.hermes/scripts/state.py read calendar | jq .last_run
```

## Pitfalls

| Symptom | Cause |
|---|---|
| `HTTP 401: Invalid API key` on a new profile | profile `.env` is empty; add the model key |
| Bot ignores group messages | privacy mode still on in BotFather |
| Message arrives wrapped in `Cronjob Response:` | `cron.wrap_response` not set **per profile** |
| `Refusing to overwrite …scratch/…py` | the agent writes its own state script; use `state.py` |
| First link becomes a huge card | `disable_link_previews` not set per profile |
| `cron run` does nothing | job is paused — `cron resume` first |
| `scripts/foo.sh` not found in `--script` | the path resolves inside the profile's `scripts/`; pass the bare filename |
| Scheduled runs all stop at once | multiplexed gateway: the scheduler lives in the primary profile's process |
