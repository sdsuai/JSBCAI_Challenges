# 🖧 Lab Ops — Systems, Storage & Security Challenge · Grade 1

**JSBCAI / Robotics Lab — Sysadmin Assistant Task · Grade 1**

> This is the **Grade 1** variant. Grade 2 is the same challenge with a
> heavier Tier 2 extra-credit list. If you were sent here directly, this is
> the one to do — do not go looking for the other branch.

We already have a lab sysadmin. What we need is students who can take focused
work off their plate — the tickets that eat an afternoon and do not need the
person who designed the system to do them.

This challenge is those tickets.

You will be handed a small, broken lab — a directory server, a shared drive, a
backup job, an SSH server, and a workstation — and asked to do the things a
volunteer actually gets asked to do:

* Onboard and offboard accounts in an **LDAP** directory
* Fix "I can't write to the shared folder" on an **NFS** mount, properly
* Prove a **backup** can actually be restored from
* **Harden SSH** and triage an auth log that has something wrong in it
* Write the **runbooks** so the next person does not have to ask you

**You are allowed to use the internet and AI assistants (ChatGPT, Claude,
Copilot, Gemini, etc.).** What matters is that the lab ends up working, that
you can explain what was wrong, and that your **video walkthrough** holds up.

---

## ‼️ Important — read this whole section

* **Everything runs in two throwaway VMs on your own laptop.** No lab access,
  no cloud account, no servers, nothing to buy. macOS, Linux, or Windows. You
  cannot damage anything real, which is deliberate — it means you can run the
  command you are unsure about and find out what it does.
* **You need `multipass`** (free, from Canonical) and about 2 GB of spare RAM
  and 16 GB of disk. `./lab/preflight.sh` checks all of this before you commit
  any time to it.
* **Scripting is in bash, Python, or C++ — your choice.** We prefer C++ in the
  lab generally, but this particular problem set is mostly shell and config, and
  **nothing here is graded on language choice.** Use whatever is right for the
  task; for most of these that will be bash.
* **This task requires you to run your code from your machine's OS terminal.**
  On Windows that is PowerShell; on macOS and Linux a common one is bash. Your
  OS might use a different terminal, or several — doesn't matter, just use one.
* **After completing this task you will need to screen record a video** showing
  the lab working and you explaining what was wrong. Obviously, in the screen
  recording you MUST run things from the terminal.
* **Create a GitHub repo containing your work and the video.** Name it something
  like `JSB_labops_challenge` so it's identifiable.
* **You may freely use any tool available to you.** The internet, ChatGPT,
  anything. Fair warning specific to this problem set: AI is genuinely good at
  producing a plausible `sshd_config` and genuinely bad at telling you which of
  the five things it changed actually mattered on *your* machine. The tickets
  ask for root causes, and the video is where that shows.

### 📮 Submission — READ THE ENTIRE BULLET

* **Submit a pull request to this repo** so we have your GitHub username and can
  find your work. **Do not do your actual work in the public forked repo** —
  others can copy it.
* **Make a private clone** of the fork and do your real work there.
* **Send an invite to the private repo to `philipamadasun1@gmail.com`** so we
  can get access.
* **Put your email address in your README.** Please don't make us go looking.

---

## ⏱ Time commitment — 5 to 7 days

**This problem set is scoped to 5–7 days of real, active work.** Not five to
seven calendar days with the tab open — five to seven days of actually sitting
down and grinding on it.

That window is deliberate, and meeting it is part of what we are measuring.

Volunteering in this lab means taking real time out of your weeknights and your
weekends, consistently, for work you have been assigned. That *is* the role. If
you can carve out that time for this challenge, you can carve it out for the
tickets we hand you once you are here. If you cannot, the fit is wrong — and it
is far better for both of us to learn that now than three weeks into something
that is sitting blocked on you.

To be direct, because you deserve to know what you are signing up for: this is
not a role that works for someone who can look at their assignment once every
two weeks. That is not a judgment about you or your priorities. Plenty of
capable people are genuinely committed elsewhere — coursework, a job, family —
and that is completely legitimate. It is simply not compatible with the pace
this lab runs at.

**If you cannot make the window, email `philipamadasun1@gmail.com` *before* it
runs out**, explain why, and ask for more time. Real reasons exist — exam weeks,
illness, work shifts, a laptop that died. Ask and explain, and I will decide
whether the explanation warrants an extension. **Asking is never held against
you.** Going quiet and surfacing late with no word is a different thing, and it
tells us what working with you would be like.

Setup trouble is the one exception where you should mail us early and without
apology. Getting multipass running is not what we are assessing, and we would
rather unblock you in ten minutes than watch you lose two days.

---

## 💻 Platform support

| | macOS | Linux | Windows |
| --- | --- | --- | --- |
| multipass | `brew install --cask multipass` | `sudo snap install multipass` | `winget install Canonical.Multipass` |
| Virtualization | built in (Intel and Apple Silicon) | needs `/dev/kvm` | Hyper-V (Pro) or VirtualBox (Home) |
| Everything else | *inside the VMs — identical on all three* | | |

Because all the actual work happens inside two identical Ubuntu VMs, **your
host OS does not affect the challenge at all** beyond installing multipass.

> 🪟 **Windows users:** run multipass from **PowerShell**, not from inside WSL —
> the VMs are managed by Windows itself. You can keep your editor and git in
> WSL if you prefer; just drive `multipass` from PowerShell.

Run `./lab/preflight.sh` before anything else. It checks your platform, RAM,
disk, and virtualization, and tells you the exact fix for your OS if something
is missing.

---

## 🚀 Start here (about 15 minutes, mostly downloading)

```bash
git clone <your private repo>
cd <repo>

./lab/preflight.sh      # can this machine run the lab? changes nothing
./lab/bootstrap.sh      # build it — 5-10 min the first time
./lab/verify.sh         # what works, and what is YOUR ticket
```

`bootstrap.sh` builds two VMs and then **deliberately breaks several things**.
That is the assignment. `verify.sh` tells you which failures are faults you must
fix (`○ TICKET`) and which mean the lab itself did not build (`✗`).

```bash
multipass shell lab-ws          # your workstation — work from here
multipass shell lab-server      # the server's console
```

Read [`lab/README.md`](lab/README.md) for the architecture and the everyday
commands.

---

## 🧭 How this is graded — read this before you start

Three things matter more than speed, and one of them will surprise you.

### 1. Root cause, not symptom

Every ticket can be made to *look* fixed in one command. Several of them have a
second problem hiding behind the first, and a fix that makes the reporter happy
today and reproduces the ticket next week is not a fix. When you close a ticket,
you must be able to say what was actually wrong and why your change addresses
it — not just what you typed.

### 2. Judgment about blast radius

Some tickets below are written the way real tickets are written: slightly
ambiguous, and destructive if you do exactly what they say.

**We are watching for whether you notice.**

Stopping to check, or doing the safe half and flagging the rest, scores *higher*
than completing the ticket quickly. **"I stopped and asked" is a correct answer
to some of these**, and you record it in `DECISIONS.md` (template provided) with
what you would have asked and who you would have asked. There is no way to score
full marks on judgment by executing everything you were handed.

This is the single most valuable trait in someone helping a sysadmin. Clever is
common. Trustworthy with production data is not.

### 3. Runbooks

Work that only you can repeat has not reduced anyone's workload. Every ticket
you close gets a short runbook written for the next volunteer at 11pm when
nobody is around to ask. See [`templates/RUNBOOK.md`](templates/RUNBOOK.md).

---

## 📋 The tickets

Each ticket is written the way you would receive it, followed by what we
actually expect. `verify.sh` checks some of these automatically; the check
going green is **necessary but not sufficient** — root cause and runbook are
graded separately and no script can see them.

---

### Part A — Identity and accounts *(LDAP)*

The directory lives on `lab-server` at `dc=jsbcai,dc=lab`. Four accounts already
exist. Start by looking around:

```bash
multipass exec lab-server -- ldapsearch -x -b dc=jsbcai,dc=lab -LLL dn
```

#### A1 — "Three new students start Monday. Can you get them set up?"

> *From: alice — Erin Uzoma, Frank Balogun, Grace Mensah. Same access as the
> other students. They'll need the shared drive.*

Create the three accounts and put them in the right group.

**Expected:** a **committed LDIF file** applied with `ldapadd`, not three
accounts typed by hand. If you cannot re-run it on a rebuilt lab, you have not
finished. Pick `uidNumber`s that will not collide with anything — and say in
your runbook how you chose them and what you checked.

#### A2 — "Can you give Grace access to the dataset share?"

Grace needs read access to `/srv/lab/datasets`. Work out what controls that,
change it, and **verify it from the workstation as Grace** rather than assuming.

#### A3 — "Who has staff access right now?"

Produce an auditable answer with `ldapsearch`, not by reading a file and
squinting. Commit the command. In your runbook, explain the search filter you
used, character by character.

#### A4 — ⚠️ "Dave graduated last month. Clean up his account and free the space."

> *From: alice — He's gone, so his home directory can go too. That's a few GB
> back.*

**Read this ticket carefully before you touch anything.**

Do what is safe and correct, document what you did **not** do and why, and write
in `DECISIONS.md` what you would have asked alice before proceeding.

Two things to think about, and there are more: what happens to files elsewhere
on the share that are owned by `dave`'s uid once that uid stops resolving? And
is "delete" the same as "revoke access"? One of those is reversible.

> When you get to Part D, come back and re-read this ticket. It will look
> different.

---

### Part B — Shared storage and permissions *(NFS)*

#### B1 — "Nobody can save anything to the shared drive."

> *From: carol — I get "Permission denied" trying to save to /mnt/shared. It
> worked last week.*

Diagnose and fix it. Verify as an actual student account, not as root — root
behaves differently over NFS and that difference is worth understanding.

**Expected:** there are **two** problems here, not one. Fixing only the first
makes carol happy today and brings the ticket straight back when the next
person creates a file. Your runbook must name both.

#### B2 — "New files keep coming out with the wrong group."

Follow-on from B1, and the second half most people miss. Explain in your
runbook what a directory's setgid bit does, and why the default behaviour is
wrong for a shared folder.

#### B3 — Explain `root_squash`

No ticket, just a question for your write-up. `root` on the workstation gets
"permission denied" on files it appears to own. Why is that the default, what is
it protecting against, and what would `no_root_squash` let a workstation do?

---

### Part C — Backups and restore

There is a nightly backup job on `lab-server`. It has been reporting success
every night for two weeks.

#### C1 — ⚠️ "Can you confirm the backups are good? We're submitting Friday."

> *From: alice — The log says OK every night, so I think we're fine, but I'd
> feel better if someone checked.*

The log does say OK every night.

**Expected:** find out whether it is true, and report honestly. There are
**three separate defects** in that job. Find all of them, and explain how a
backup can fail every night for two weeks while reporting success. Then fix it,
and prove the fix by restoring — see C3.

#### C2 — "Make it tell us when it breaks."

Rewrite the job so a failure is loud. Consider: what should its exit code be?
What should the log say? How would anyone find out without reading the log?
State your assumptions about what monitoring exists — there isn't any, which is
itself worth saying out loud.

#### C3 — ⚠️ "Restore `notes/calibration.md` from before Tuesday."

The restore drill. This is the only thing that proves a backup is real.

**Time yourself, and put the number in your write-up.**

⚠️ **Restoring on top of live data is how people turn a small problem into an
outage.** Think about where you restore *to* before you run anything. Your
runbook must make the safe path the obvious one — if the next volunteer follows
it at 11pm while panicking, they must not be able to clobber production by
following your instructions literally.

#### C4 — Retention

How many backups do you keep, for how long, and what happens when the disk
fills? Write the policy down. It is three sentences, and almost nobody writes
it, which is why disks fill.

---

### Part D — Access hardening and log triage

#### D1 — "Can you lock down SSH on the server? IT asked."

`sshd_config` on `lab-server` was loosened for a demo and never put back.

**Expected:** audit it, fix it, and **explain each change** — what it allows,
why it is wrong here, and what would break if you changed it.

⚠️ **You are editing the configuration of the service you connect through.**
Get it wrong and you lock yourself out. `multipass shell lab-server` is your
console and will save you — note in your runbook what you would have done
without that safety net, because on a real server you do not have it.

#### D2 — "While you're in there, is anything else obviously wrong?"

Look beyond `sshd_config`. Who can bind to the directory anonymously and read
what? Where are credentials stored in this repo? What is exported to whom in
`/etc/exports`?

You will find more than you can fix in the time available. **Rank the findings
by risk and say what you would do first**, rather than fixing whatever is
easiest. The ranking is the deliverable.

#### D3 — ⚠️ "Something looks off in the auth log. Can you take a look?"

`/var/log/lab/auth.log` on the server, also committed at
[`logs/auth.log`](logs/auth.log).

Something happened. Work out what, when, and how it was possible.

**Expected:** an incident report using
[`templates/INCIDENT.md`](templates/INCIDENT.md), placed at
`/srv/lab/shared/runbooks/INCIDENT.md` and committed to your repo. Timeline
from the evidence, cited by line number. Facts separated from inferences. An
explicit list of **what these logs cannot tell you** — that section is worth
more than the timeline.

Then answer: **which earlier ticket in this challenge, if it had been done on
time, would have prevented this?**

---

### Part F — Runbooks and write-up

#### F1 — Runbooks

One per closed ticket, in `runbooks/`, from
[`templates/RUNBOOK.md`](templates/RUNBOOK.md). Also place copies at
`/srv/lab/shared/runbooks/` on the server. Short is good. **The test: could
someone follow it without asking you a single question?**

#### F2 — Decision log

`DECISIONS.md`, from [`templates/DECISIONS.md`](templates/DECISIONS.md).
Every moment you stopped, and every consequential thing you decided to proceed
with. See "How this is graded" above — this is not optional and it is not a
formality.

#### F3 — Write-up

Answer these in your own words. Short and concrete.

1. **B3** — `root_squash`: what it protects against, and what `no_root_squash`
   would allow.
2. **C1** — how a backup reported success every night for two weeks while
   backing up nothing. What class of bug is that, and where else does it hide?
3. **C3** — how long your restore took, and what you would change to make it
   faster or safer.
4. **D3** — which earlier ticket would have prevented the incident.
5. **A4** — what you did about dave, what you deliberately did not do, and what
   you would have asked first.
6. **The thing you got wrong** during this challenge, and how you found out.
   Everyone has one. Submissions claiming none read as submissions that did not
   check.

You were told to use AI freely, and that stands. **This write-up is the
exception** — for a practical reason, not a moral one: it is the only place we
find out whether *you* understood the systems you fixed, and it is extremely
obvious when the write-up is not in the same voice as the video.

---

## 🎥 Video walkthrough

**8–15 minutes.** Screen recording, your voice, everything run from a terminal.

* Show `./lab/verify.sh` before and after your work
* Walk through **two** tickets end to end — one diagnosis-heavy (B1 or C1)
  and **one where you stopped and asked** (A4 or C3)
* Demonstrate the restore from C3 actually restoring
* Show the SSH hardening, and say what you checked before restarting sshd
* Walk through your incident report against the log
* Say what you would do next with another week

---

## 🛠 Extra Credit *(optional)*

### 🟦 Tier 1 — laptop-friendly

| | Points | |
| --- | --- | --- |
| **Configuration as code** | +10 | Redo your fixes as an Ansible playbook (or equivalent) that turns a fresh lab green in one command. Prove it against `./lab/reset.sh`. |
| **Onboarding automation** | +8 | One script: name in, LDIF + group + home directory + verification out. Must be idempotent and must refuse bad input. |
| **Monitoring the backup** | +8 | Make a silent failure impossible to miss without reading a log. Justify the mechanism given no monitoring exists. |
| **`fail2ban`** | +6 | Configure it against the brute force in the auth log. Show it banning. Then say what it does *not* protect against. |
| **POSIX ACLs** | +8 | Solve B1/B2 with `setfacl` default ACLs instead. Compare with the setgid approach — when is each right? |
| **Disk quotas** | +6 | Per-user quotas on the share so one person cannot fill it. Show the limit being hit. |
| **Firewall** | +6 | `ufw`/`nftables` on the server, allowing only what the lab needs. Justify every open port. |

### 🟧 Tier 2 — harder

| | Points | |
| --- | --- | --- |
| **Disaster recovery drill** | +15 | Destroy `lab-server` entirely. Rebuild it from your backups and committed config. **Time it**, and report what you discovered was missing — there is always something. The single most valuable item on this list. |
| **LDAP over TLS** | +12 | Your own CA, certificate on the server, `ldaps://` enforced, anonymous bind restricted. Show the traffic encrypted before and after. |
| **Automated offboarding with an audit trail** | +10 | Turn Ticket A4 into one reviewable command: disable the directory account, inventory everything that user owns across the share, and write an audit record of who ran it, when, and what changed. **Deletion must require a separate explicit flag**, and everything before that point must be reversible. Show it run against a test account, show the audit record, and show it refusing to delete without the flag. |
| **Centralized logging** | +10 | Ship both VMs' logs to one place, so an attacker clearing local logs does not erase the evidence. Relate it to D3. |

---

## 🧨 Grading Rubric

| Category | Points | What we are looking at |
| --- | --- | --- |
| **Part A** — Identity and accounts | 15 | Reproducible LDIF, sane uid choices, verified access, careful offboarding |
| **Part B** — Storage and permissions | 15 | Both causes found in B1, setgid understood, `root_squash` explained |
| **Part C** — Backups and restore | 20 | All three defects, loud failure, a real timed restore, safe restore path |
| **Part D** — Hardening and triage | 20 | Each change justified, findings ranked by risk, incident report with an honest unknowns section |
| **Judgment & blast radius** | 20 | `DECISIONS.md`. Did you notice the dangerous tickets? Did you stop? |
| **Runbooks** | 10 | Followable by a stranger at 11pm |
| **Write-up** | 10 | Concrete, own words, commits to answers |
| **Video** | 15 | Required demos performed live, explains causes rather than commands |
| | **125** | |
| **Extra credit Tier 1 / Tier 2** | +20 / +20 | |
| | **165 max** | |

### How we actually read a submission

1. **`DECISIONS.md` first.** Before the fixes. It tells us more about whether we
   want to work with you than anything else in the repo.
2. **Then the root causes.** A green `verify.sh` with no explanation of what was
   wrong scores like a copied answer, because that is what it looks like.
3. **Then the video.** "I ran this command" is not an explanation. "The group
   couldn't write *and* new files weren't inheriting the group, so fixing the
   first would have brought the ticket straight back" is.

**Automatic point losses:**

* Destroyed data a ticket did not authorize destroying, without flagging it
* `DECISIONS.md` missing or empty
* A ticket closed with no root cause stated
* Runbooks that are shell history rather than instructions
* Fixes that exist only inside a VM and are not committed anywhere

---

## 🗂 What's in this repo

```
README.md              this file
lab/
  README.md            lab architecture and everyday commands
  preflight.sh         check your machine BEFORE you commit time
  bootstrap.sh         build both VMs, provision, inject faults
  verify.sh            what works; separates lab breakage from your tickets
  reset.sh             destroy and rebuild
  provision/           what gets installed on each VM
  seed/                initial directory contents (LDIF)
  faults/              spoilers — the deliberate breakage, explained
logs/
  auth.log             the log for the D3 incident
templates/
  RUNBOOK.md           one per closed ticket
  INCIDENT.md          for D3
  DECISIONS.md         the judgment log — graded, do not skip
```

---

## ✅ Final checklist

- [ ] `./lab/verify.sh` — every ticket check green
- [ ] A root cause written down for **every** ticket, not just a fix
- [ ] `runbooks/` — one per ticket, committed *and* on the server
- [ ] `DECISIONS.md` — including the three closing questions
- [ ] `runbooks/INCIDENT.md` — timeline, cited, with an unknowns section
- [ ] Write-up — all six questions, your own words
- [ ] Every fix committed as a file, not left inside a VM
- [ ] **Your email address in your README**
- [ ] Video — before/after `verify.sh`, two tickets end to end, live restore
- [ ] It all still works after `./lab/reset.sh` and re-applying your work

---

## 🧭 A closing note

Most of this challenge is not hard in the sense of requiring cleverness. It is
hard in the sense that it rewards being careful when nobody is watching, and
that is exactly the trait we are hiring for.

If you are unsure whether to run something destructive: **that hesitation is the
correct instinct.** Write it down in `DECISIONS.md`, do the safe version, and
say what you would have asked. You will score better than someone who guessed
and got lucky.

Watch the clock against [the 5–7 day window](#-time-commitment--5-to-7-days).
Finished and honest beats complete and overstated — and if the window genuinely
does not work for you, email before it closes rather than after.
