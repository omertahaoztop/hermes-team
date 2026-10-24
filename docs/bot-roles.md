# The nine roles

Each role is a template. Fill in your own sources; the shape of the job is what
this repo actually offers. Every role reads; none writes.

---

## 1. Primary — personal support

**Reads:** your own check-in notes, a local journal, prior patterns.
**Emits:** a daily check-in (mood, open loops, one question), a weekly pattern
observation ("three weeks in a row you deferred the same task").
**Special power:** the only agent allowed a bad-day mode that defers its own
runs. It is the only legitimate user of silence, because the day's message
budget was deliberately spent rather than forgotten.
**Fails when:** it starts giving advice instead of reflecting your own data back.

## 2. Calendar — day plan

**Reads:** ICS feeds (work + personal), declared conflicts.
**Emits:** 12 plan lines with times, plus prep notes for anything unusual, plus a
closing paragraph reading the day ("two back-to-back calls with no gap; the
afternoon is your only deep-work block").
**Fails when:** it lists events without interpreting them. A list of times is
what the calendar app already shows you.

## 3. Tasks — stale-task reminders

**Reads:** task tracker API (Vikunja, Todoist, Linear…).
**Emits:** 4–6 items, each with age in days, project, and why *this* one now.
Tiers: overdue → due today → oldest untouched. Prunes what it already showed in
the last 7 days, so you are not nagged about the same item twice in a week.
**Fails when:** it recites the whole backlog. Fifty open tasks have no priority;
five do.

## 4. Issues — open and overdue work

**Reads:** issue tracker API (Redmine, Jira, GitHub Issues).
**Emits:** two groups — 4–5 urgent (overdue, blocked, or customer-facing),
4–6 suggestions (rotating, so the same project is not proposed daily).
**Fails when:** it treats "assigned to me" as "urgent to me". Age and customer
impact decide, not assignment.

## 5. Anchor — morning anchor and evening proposal

**Reads:** an activity log, an energy record, a task pool of candidate activities.
**Emits:** a morning anchor (one thing that would make today count) and an
evening proposal (2–3 pool candidates matched to recorded energy).
**Fails when:** the pool goes stale. Regenerate it on a schedule, and cap how often
the same candidate can be proposed.

## 6. News — signals, not headlines

**Reads:** a fixed list of RSS/Atom feeds and aggregators, fetched by a
deterministic collector into a raw JSON file.
**Emits:** 4–6 signals. Each is a bold title, 2–3 lines of *why this matters to
you specifically*, a link, and an explicit note when a claim could not be
verified from the feed. Closes with which item matters most and why.
**Fails when:** it summarizes headlines. The value is the ranking argument, not
the summary — you could read the feed yourself.

## 7. Scout — repos worth attention

**Reads:** GitHub search API, package indexes, a candidate pool.
**Emits:** 4–6 candidates. Each: what it does, how active it is (last commit,
open-issue responsiveness), what contributing would teach you, and where the
first contribution could land.
**Fails when:** it recommends stars. A 40k-star repo is not an opportunity; a
responsive 300-star repo with a good-first-issue is.

## 8. Mail — triage, never send

**Reads:** IMAP or Gmail API summary data.
**Emits:** 5–8 items that need a human decision, each with sender, what is being
asked, deadline if any, and why it ranks there. Then a breakdown of the noise
(newsletters, notifications) with a count, so you can see how much was filtered.
**Fails when:** it summarizes every message. Triage means deciding what you may
ignore — say so explicitly.
**Never:** sends, replies, archives, or labels anything.

## 9. Ops — incident notes and runbooks

**Reads:** your incident notes, runbooks, recent changes.
**Emits:** 4–8 items in the shape Symptom / Evidence / Root cause / Action. On an
incident, a skeleton you fill in, not a story it invents.
**Fails when:** it states a cause it did not verify. "Unverified" is a valid and
required answer.

---

## Choosing fewer than nine

Nine is what one person's setup grew into. Start with two that are provably
useful and independently verifiable — issues and tasks are the usual first pair,
because you can check the tracker yourself.

The rule that matters more than the count: **delete the agent nobody reads.** An
agent that produces unread messages costs attention and returns nothing, and it
will quietly rot.

## Filling in a role

Take `templates/SKILL.template.md` and answer:

1. **Source** — exactly which endpoint or file, and which credential.
2. **Collector** — what deterministic script fetches it. If the answer is "the
   model fetches it", stop and write the script instead.
3. **State** — what must not be repeated across runs.
4. **Output** — which items, in which order, with what evidence per item.
5. **Failure** — what a one-line error looks like when the source is down.
