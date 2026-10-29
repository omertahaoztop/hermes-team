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

## Matrix channel (reference deployment)

Each agent is its own Matrix user with its own room; one space groups them.

```bash
# 1. user (Synapse host, registration secret from homeserver.yaml)
register_new_matrix_user -c /etc/matrix-synapse/homeserver.yaml \
  -u bridge -p "$(openssl rand -hex 24)" --no-admin http://localhost:8008

# 2. token for that user
curl -s -X POST http://localhost:8008/_matrix/client/v3/login \
  -d '{"type":"m.login.password","identifier":{"type":"m.id.user","user":"bridge"},
       "password":"<password>"}'

# 3. room + invite yourself
curl -s -X POST http://localhost:8008/_matrix/client/v3/createRoom \
  -H "Authorization: Bearer <token>" \
  -d '{"name":"Bridge","preset":"private_chat","invite":["@you:example.org"]}'
```

Profile `.env` — the room id appears twice, once as the allowed room and once as the
default:

```bash
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_USER_ID=@bridge:example.org
MATRIX_ACCESS_TOKEN=<token>
MATRIX_ALLOWED_USERS=@you:example.org
MATRIX_ALLOWED_ROOMS=!roomid
MATRIX_HOME_ROOM=!roomid
```

Then `hermes -p bridge cron create … --deliver "matrix:!roomid"` and write
`m.space.child` in your space so the room shows up under it.

### Pitfalls that cost real time

| Symptom | Cause |
|---|---|
| Room messages arrive, agent never answers | gateway process started before `.env` gained the Matrix keys — restart it; the log line to look for is `matrix connected (profile: X)` |
| Display name still shows the profile name | set `m.room.member` state for the agent *in that room*, not only the profile display name |
| Avatar upload returns 404 | the public vhost may not proxy `/_matrix/media/*`; upload against the internal listener (`http://localhost:8008`) |
| Room is not listed under the space | you own the space power level and the agent does not: adding `m.space.child` requires power, so either add the room yourself or grant the agent moderator |
| Old messages replayed on first run | no cursor yet — the first run reads `num_before` backlog; seed the cursor before enabling the job |
