# Incident report: <short description>

For Ticket D3. Copy to `runbooks/INCIDENT.md` in your submission, and also
place a copy at `/srv/lab/shared/runbooks/INCIDENT.md` on the server so
`verify.sh` can see it.

Write it the way you would hand it to the lab manager: they have five minutes,
they are not going to read the raw log, and they have to decide what to do
today. Lead with what happened and what you need from them.

---

## Summary

Two or three sentences, no jargon. What happened, to what, and is it over?

## Timeline

Times straight from the log. Do not round, do not guess, and mark anything you
are inferring rather than reading.

| Time | What the evidence shows | Source |
| --- | --- | --- |
| | | `auth.log:<line>` |

## What we know

Facts, each traceable to a specific log line. Cite line numbers.

## What we do not know

Be explicit. The single most useful thing in a real incident report is an
honest list of what the evidence cannot tell you — it stops everyone else
assuming it was ruled out. If you cannot tell from these logs whether data
actually left the building, say exactly that.

## How it was possible

Root cause, not just the proximate one. Keep asking "and why was *that* true?"
until you reach something someone decided. There is usually more than one
contributing failure, and they are usually boring.

## Immediate actions

What you did or would do in the next hour, and — importantly — **what you did
NOT do without authorisation**, and why.

| Action | Done? | Needs approval from | Risk if we wait |
| --- | --- | --- | --- |
| | | | |

## Preventing recurrence

Concrete and checkable. "Be more careful" is not a control. "Password auth
disabled; offboarding checklist now includes disabling the directory account
the same day" is.

## Evidence preserved

What you kept, and where. If you altered anything on the system before copying
the evidence, say so — it matters, and hiding it matters more.

---

*Reported by: <name>  ·  Date: <date>*
