# 🖧 Lab Ops — Systems, Storage & Security Challenge · Grade 3

**JSBCAI / Robotics Lab — Sysadmin Assistant Task · Grade 3**

> This is the **Grade 3** variant — the hardest. It adds two faults that are
> considerably harder to diagnose than anything in Grade 2, and it makes the
> disaster-recovery drill **required** rather than extra credit. Grades 1 and 2
> are lighter. If you were sent here directly, this is the one to do — do not go
> looking for the other branches.

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
* Work out why the share got **slow**, and whether it is even the network
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

### 2. Verify that your fix held

New at this grade, and stated plainly because it is fair to warn you rather
than merely catch you: **not everything in this lab stays fixed.**

Something else on this server may own the state you just changed. A fix that
goes green and then quietly reverts is worse than no fix at all, because now
there is a closed ticket saying it works. Before you change a file, form the
habit of asking what else writes to it — `crontab -l`, `ls /etc/cron.d/`,
`systemctl list-timers`, and any configuration management. Then re-check your
work later, not immediately.

`./lab/verify.sh` is cheap. Run it again after you have moved on to something
else.

### 3. Judgment about blast radius

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

### 4. Runbooks

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

#### B3 — "Some files on the share belong to 'svc-capture' and nobody knows why."

> *From: bob — I made these files but they're not mine anymore. Did someone
> change something? Have we been hacked?*

Nobody was hacked. Two machines disagree about something.

**Expected:** explain the actual mechanism in your runbook — specifically, what
identifies a user in an NFS request. Then fix it. Renumbering one account is
half an answer; the other half is what stops it happening again, and that is
the half that connects this part to Part A.

#### B4 — ⚠️ "The scratch area says it's full but there's loads of space."

> *From: carol — I'm trying to write frame indexes to /srv/lab/scratch and I
> get "No space left on device". But `df -h` says it's 5% used? I don't
> understand what I'm looking at.*

carol is reading the output correctly. The disk really does have space.

**Expected:** find the actual resource that ran out, and explain in your runbook
why the error message is the same for both cases. Then fix it — and note that
freeing things up is only the immediate fix. Your runbook must say what changes
so this does not recur in a month, because the underlying limit is fixed at
creation time and deleting files does not raise it.

A hint about method rather than answer: when a command's error contradicts what
you think you know, suspect that the thing you are measuring is not the thing
that ran out.

#### B5 — ⚠️ "I fixed this yesterday and it's broken again."

> *From: bob — you sorted out the shared drive on Monday and it worked. It's
> back to permission denied this morning. Did the fix not take?*

The fix took. Something undid it.

**Expected:** find what is reverting your change, and understand **why it
exists** before you touch it — it was written for a reason that was valid at
the time. Then decide what is actually wrong: the enforcement, or the policy it
enforces. Fix the right one.

Deleting it because it is inconvenient is the wrong answer, and so is working
around it. Your runbook must explain what it was for and why your change is
safe, or the next person will simply put it back.

This ticket is also the reason for the warning in *"Verify that your fix held"*
above.

#### B6 — Explain `root_squash`

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

### Part E — Network and throughput

#### E1 — Baseline

Measure the link between `lab-ws` and `lab-server` with `iperf3`. Record
throughput and round-trip latency. You cannot call something slow without a
number for what fast was.

#### E2 — Your actual wifi

Measure your own laptop's wifi: throughput and latency to your router, and to
something on the internet. Report the numbers.

In your write-up: your wifi reports a link rate (say 866 Mbps). You will not
measure anything close to it. Explain the gap — at least three distinct reasons,
and be specific.

#### E3 — ⚠️ "Copying from the share got really slow this week. Did the network die?"

> *From: bob — Pulling a folder of scans takes forever now. One big file seems
> fine though? Maybe it's my laptop.*

Bob's observation is the clue, and it is the opposite of what most people
assume.

**Expected:** find the actual cause, and — this is the graded part — **show
your method**. A candidate who tests with one large `dd` will measure a
perfectly healthy link and conclude the problem is elsewhere. Your write-up must
explain why one big file and 500 small files behave so differently over the same
link, in terms of what NFS does per file.

Then fix it, and note whether your fix survives a reboot.

#### E4 — "Is it the network, the disk, or NFS?"

Given a slow transfer, how do you tell those three apart? Write the decision
procedure — the commands, in order, and what each result rules out. This is a
runbook, and it is the most reusable thing you will produce in this challenge.

---

### Part F — Disaster recovery *(required at this grade)*

Extra credit in Grades 1 and 2. Required here, and weighted accordingly.

#### F1 — ⚠️ "The server's gone."

> *From: alice — lab-server is dead. Storage controller. It is not coming back.
> How fast can you get us running again?*

Run the drill:

```bash
./lab/disaster.sh
```

It destroys `lab-server` permanently and hands you back an **empty** Ubuntu VM.
It deliberately does not run our provisioning scripts — rebuilding from
`bootstrap.sh` would prove nothing, because that is our work. You rebuild from
**yours**: your committed LDIF, your backup, your hardened config, your backup
job, your runbooks.

**Start a timer when it finishes. Stop it when `./lab/verify.sh` is green
again** — every INFRA check and every ticket check.

Do not tidy up first to make it go smoothly. If your backup is incomplete, the
point is to find that out now. If a runbook says "restore the usual way", the
point is to find that out now.

**Expected:** `runbooks/DR-REPORT.md`, committed and placed at
`/srv/lab/shared/runbooks/DR-REPORT.md`, containing:

* **How long it took**, honestly, wall-clock.
* **What you could not recover**, and what it would have cost the lab. There is
  always something. A report claiming full recovery reads as a drill that was
  quietly prepared for rather than actually run.
* **Which of your runbooks failed you** — the step that was ambiguous at the
  moment you needed it most.
* **What you changed afterwards** so the next rebuild is faster.
* **Your predicted time versus your actual time** (`disaster.sh` asks you to
  write the prediction down before it destroys anything). The gap is
  interesting and we will ask about it.

> ⚠️ This is the only genuinely irreversible command in the challenge, and it is
> irreversible on purpose. `lab-ws` also survives with stale mounts pointing at
> exports that no longer exist — dealing with that is part of the drill.

---

### Part G — Runbooks and write-up

#### G1 — Runbooks

One per closed ticket, in `runbooks/`, from
[`templates/RUNBOOK.md`](templates/RUNBOOK.md). Also place copies at
`/srv/lab/shared/runbooks/` on the server. Short is good. **The test: could
someone follow it without asking you a single question?**

#### G2 — Decision log

`DECISIONS.md`, from [`templates/DECISIONS.md`](templates/DECISIONS.md).
Every moment you stopped, and every consequential thing you decided to proceed
with. See "How this is graded" above — this is not optional and it is not a
formality.

#### G3 — Write-up

Answer these in your own words. Short and concrete.

1. **B6** — `root_squash`: what it protects against, and what `no_root_squash`
   would allow.
2. **B3** — what actually identifies a user in an NFS request, and why that
   makes a directory service necessary rather than merely convenient.
3. **C1** — how a backup reported success every night for two weeks while
   backing up nothing. What class of bug is that, and where else does it hide?
4. **C3** — how long your restore took, and what you would change to make it
   faster or safer.
5. **E3** — why latency destroys a many-small-files copy but barely touches one
   large file.
6. **D3** — which earlier ticket would have prevented the incident.

7. **B4** — the two finite resources a filesystem can exhaust, why they produce
   the same error, and how you tell them apart in under ten seconds.

8. **B5** — how long your B1 fix survived before it was reverted, how you found
   what was reverting it, and how you decided which of the two to change.

9. **F1** — the single thing that most slowed your rebuild.
10. **A4** — what you did about dave, what you deliberately did not do, and what
    you would have asked first.
11. **The thing you got wrong** during this challenge, and how you found out.
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
* Walk through **two** tickets end to end — one diagnosis-heavy (B1, B3, or E3)
  and **one where you stopped and asked** (A4 or C3)
* Demonstrate the restore from C3 actually restoring
* Show the SSH hardening, and say what you checked before restarting sshd
* Walk through your incident report against the log
* **Show the disaster-recovery rebuild** — at minimum the destroyed server, and
  `verify.sh` going green again afterwards. Timelapse or cuts are fine; say how
  long it really took
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
| **Drift detection** | +12 | Write a checker that compares the live lab against a declared baseline — permissions, exports, sshd settings, group membership — and exits nonzero on any difference. Run it on a timer. This is the systemic answer to Ticket B5: instead of one script silently enforcing a stale policy, you get a declared expectation and a loud alarm when reality diverges. |
| **LDAP over TLS** | +12 | Your own CA, certificate on the server, `ldaps://` enforced, anonymous bind restricted. Show the traffic encrypted before and after. |
| **SSH certificate auth** | +10 | A small CA issuing short-lived user certificates instead of `authorized_keys`. Explain what this fixes about key management at lab scale. |
| **Centralized logging** | +10 | Ship both VMs' logs to one place, so an attacker clearing local logs does not erase the evidence. Relate it to D3. |

---

## 🧨 Grading Rubric

| Category | Points | What we are looking at |
| --- | --- | --- |
| **Part A** — Identity and accounts | 15 | Reproducible LDIF, sane uid choices, verified access, careful offboarding |
| **Part B** — Storage and permissions | 25 | Both causes found in B1, setgid understood, uid mechanism explained, inode exhaustion diagnosed, reverter found and reasoned about |
| **Part C** — Backups and restore | 20 | All three defects, loud failure, a real timed restore, safe restore path |
| **Part D** — Hardening and triage | 20 | Each change justified, findings ranked by risk, incident report with an honest unknowns section |
| **Part E** — Network and throughput | 15 | Correct method, latency-vs-bandwidth understood, reusable decision procedure |
| **Part F** — Disaster recovery | 20 | Rebuilt from own artifacts; honest report of what was lost; runbooks that survived contact |
| **Judgment & blast radius** | 20 | `DECISIONS.md`. Did you notice the dangerous tickets? Did you stop? |
| **Runbooks** | 10 | Followable by a stranger at 11pm |
| **Write-up** | 10 | Concrete, own words, commits to answers |
| **Video** | 15 | Required demos performed live, explains causes rather than commands |
| | **170** | |
| **Extra credit Tier 1 / Tier 2** | +20 / +20 | |
| | **210 max** | |

### How we actually read a submission

1. **`DECISIONS.md` first.** Before the fixes. It tells us more about whether we
   want to work with you than anything else in the repo.
2. **Then the root causes.** A green `verify.sh` with no explanation of what was
   wrong scores like a copied answer, because that is what it looks like.
3. **Then the video.** "I ran this command" is not an explanation. "The group
   couldn't write *and* new files weren't inheriting the group, so fixing the
   first would have brought the ticket straight back" is.

At this grade we also read **`DR-REPORT.md` immediately after `DECISIONS.md`**.
A rebuild that went perfectly is not a good sign — it means the drill was
prepared for rather than run. We are looking for the honest list of what could
not be recovered.

**Automatic point losses:**

* Destroyed data a ticket did not authorize destroying, without flagging it
* `DECISIONS.md` missing or empty
* A ticket closed with no root cause stated
* Runbooks that are shell history rather than instructions
* Fixes that exist only inside a VM and are not committed anywhere
* A B1 fix that has silently reverted by the time we look at it
* `DR-REPORT.md` claiming nothing was lost, with no detail supporting it

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
  disaster.sh          Part G — destroys lab-server for real. Read it first.
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
- [ ] `runbooks/DR-REPORT.md` — real timing, honest list of what was lost
- [ ] Your B1 fix is still holding — re-run `./lab/verify.sh` before you submit
- [ ] Write-up — all eleven questions, your own words
- [ ] Every fix committed as a file, not left inside a VM
- [ ] **Your email address in your README**
- [ ] Video — before/after `verify.sh`, two tickets end to end, live restore, the DR rebuild
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
