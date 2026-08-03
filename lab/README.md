# The lab

Two throwaway Ubuntu VMs. Everything you do happens inside them; nothing here
touches your real machine, and `reset.sh` puts it all back.

```
        your laptop
             │
             │  multipass
    ┌────────┴────────┐
    │                 │
┌───▼──────────┐  ┌───▼──────────┐
│  lab-server  │  │   lab-ws     │
│              │  │              │
│  slapd       │◄─┤ nslcd        │  who is uid 10002?
│  :389        │  │              │
│              │  │              │
│  nfsd        │◄─┤ /mnt/shared  │  the shared drive
│  :2049       │  │ /mnt/datasets│
│              │  │              │
│  sshd :22    │◄─┤ ssh          │
└──────────────┘  └──────────────┘
     the server      where you work
```

**You work from `lab-ws`.** That is the machine a student would sit at.
`lab-server` is the thing you are administering — reach it over SSH, the way
you would in real life, rather than treating it as a local shell.

```bash
multipass shell lab-ws                  # your workstation
multipass exec lab-ws -- id alice       # one-off command
multipass shell lab-server              # the server (your "console" access)
```

`multipass shell lab-server` is your out-of-band console — the equivalent of
physically walking to the rack. It is what saves you when you lock yourself out
over SSH, which you may well do in Part D. Real servers are not always so
forgiving, and that is worth remembering while you edit `sshd_config`.

## Files

| | |
| --- | --- |
| `preflight.sh` | checks your machine can run this. Run it first. Changes nothing. |
| `bootstrap.sh` | builds both VMs, provisions them, injects the faults |
| `verify.sh` | reports what works. Distinguishes lab breakage from your tickets |
| `reset.sh` | destroys and rebuilds. Use it freely |
| `disaster.sh` | **Part G.** Destroys `lab-server` for real and gives you a bare one. Read it before running it |
| `provision/` | what gets installed and configured on each VM |
| `seed/` | the initial directory contents (LDIF) |
| `faults/` | **spoilers.** The deliberate breakage. See below |

## About `faults/`

The lab does not come up healthy. Several things are deliberately broken, and
fixing them is the assignment.

**Those scripts are readable, and they explain exactly what they broke and
why.** We are not going to pretend otherwise — you could read them in ten
seconds, and the challenge already says you may use any tool you like.

But read them *after* you have diagnosed the problem, not before. The skill
being assessed is working backwards from a symptom with no idea what you are
looking for, which is the entire job. Reading the answer first converts a
diagnostic exercise into a typing exercise, and the video walkthrough will make
it obvious which one you did. Afterwards they are genuinely worth reading —
each explains the underlying mechanism in more depth than the ticket does.

## Not everything stays fixed

At this grade one of the faults is a job that periodically undoes a change you
made. That is deliberate, it is a real failure mode, and it is why `verify.sh`
is worth re-running some time after you think you are done rather than
immediately after each fix.

Before editing any file, it is worth knowing what else writes to it:

```bash
crontab -l; sudo crontab -l
ls -la /etc/cron.d/ /etc/cron.*/
systemctl list-timers --all
```

## Common operations

```bash
./lab/verify.sh                  # what is broken right now?
./lab/verify.sh --infra          # is the LAB broken, or is that my ticket?
./lab/verify.sh --part B         # just the storage checks

multipass list                   # VM status and IPs
multipass stop lab-server lab-ws # free up RAM without destroying anything
multipass start lab-server lab-ws

./lab/reset.sh                   # clean slate, ~5 minutes
./lab/reset.sh --destroy         # tear down, do not rebuild

./lab/disaster.sh                # Part G: destroy lab-server, keep nothing
```

## Keep your work outside the VMs

The VMs are disposable and you will probably reset one at some point. Anything
that exists only inside a VM dies with it.

Write your scripts, LDIFs, and configs **in this git repo on your laptop**,
then copy them in:

```bash
multipass transfer ./my-work/backup.sh lab-server:/home/ubuntu/
multipass exec lab-server -- sudo install -m 0755 /home/ubuntu/backup.sh /usr/local/bin/
```

This is also what the tickets ask for. "Committed script" and "shell history"
are not the same deliverable, and only one of them survives you.

## If something goes wrong

**A VM will not start, or bootstrap fails partway.** Run `./lab/reset.sh`.
Provisioning is idempotent, so re-running is safe.

**`verify.sh` reports INFRA failures.** That is not one of your tickets — the
lab did not build. Reset, and if it persists, send the output to
`philipamadasun1@gmail.com`.

**Everything is slow.** That may be a ticket (see Part E) rather than your
laptop. Check `tc qdisc show` on the server before you go hunting elsewhere.

**You locked yourself out over SSH.** `multipass shell lab-server`. Then read
your own runbook and notice whether it warned you.

## Low-memory mode

On a 4 GB laptop:

```bash
./lab/bootstrap.sh --small       # 768M per VM
```

If that is still too tight, run the VMs one at a time — stop `lab-ws` while
doing server-side work. It is slower and more annoying, but nothing in the
challenge requires both to be running simultaneously except the NFS and
throughput work in Parts B and E.
