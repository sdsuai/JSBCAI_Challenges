# Runbook: <what this procedure does>

Copy this per procedure into `runbooks/` in your submission. Keep them short.

A runbook is written for **the next volunteer at 11pm when the person who knew
how to do this is unreachable.** That reader is competent but has never touched
this system. Write for them, not for yourself, and not for us.

The test: could someone follow this without asking you a single question?

---

## What this is for

One or two sentences. When would somebody reach for this runbook?

## Before you start

- [ ] What access do you need? (which host, which account, sudo or not)
- [ ] What should you check is true first?
- [ ] **Is anything here irreversible?** Say so here, at the top, in bold.
- [ ] Is there a backup, and have you confirmed it is current?

## Steps

Numbered. Exact commands, in copy-pasteable blocks. Say what each one does and
what you expect to see — a step whose success you cannot recognise is a step
that will be done wrong.

1. **<what>** — why

   ```bash
   <exact command>
   ```

   Expected: `<what good output looks like>`

2. ...

## How to tell it worked

The actual verification. Not "it should be fine" — a command whose output
proves it, and what that output looks like.

```bash
<verification command>
```

## If it goes wrong

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| | | |

## How to undo it

If you cannot undo it, say that **here** and say what the recovery path is
instead (restore from backup, rebuild, call someone). "You can't" is a valid
and important answer — it just has to be written down before somebody finds
out the hard way.

---

*Written by: <name>  ·  Last verified: <date>  ·  Tested on: lab-server / lab-ws*

Update the "last verified" date whenever you actually run it. A runbook nobody
has executed in a year is a rumour.
