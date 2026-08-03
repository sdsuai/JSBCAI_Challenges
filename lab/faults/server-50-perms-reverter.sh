#!/usr/bin/env bash
# server-50-perms-reverter.sh — makes a fix not stay fixed.
#
# SPOILER WARNING. This is the answer to Ticket B5. Diagnose it first.
#
# Installs a cron job that re-applies the WRONG permissions to the shared
# folder every 10 minutes, undoing whatever the candidate did for B1.
#
# The framing is deliberately sympathetic, because this is how it actually
# happens: somebody wrote a small "enforcement" script to stop permissions
# drifting, the policy it enforces was correct at the time, and nobody
# revisited it when the policy changed. It is not malware and it is not
# stupidity — it is configuration management that outlived its own assumptions.
#
# What it teaches, and why it belongs only in the hardest grade:
#
#   A fix you did not verify is a fix you did not make. A candidate who
#   changes the mode, sees it go green, closes the ticket and moves on will
#   have the ticket reopen ten minutes later. The habit being trained is
#   "check whether something else owns this state before you change it" —
#   in practice: look in cron, look in systemd timers, look for config
#   management, THEN edit the file.
#
# The correct fix is not `crontab -r`. It is understanding what the job is for,
# deciding whether the policy or the job is wrong, and changing the right one —
# then saying so in a runbook so the next person does not simply reinstate it.

set -euo pipefail

cat > /usr/local/sbin/lab-perms-sync.sh <<'SCRIPT'
#!/bin/bash
# Enforce shared-folder permissions.        -- added after the March audit
#
# The audit flagged that /srv/lab/shared was group-writable. This resets it
# on a schedule so it cannot drift again.
#
# TODO: revisit once the new group policy is agreed.   -- never revisited
LOG=/var/log/lab-perms-sync.log

chown root:staff /srv/lab/shared
chmod 0755 /srv/lab/shared

echo "$(date -Iseconds) permissions enforced on /srv/lab/shared" >> "$LOG"
SCRIPT
chmod 0755 /usr/local/sbin/lab-perms-sync.sh

cat > /etc/cron.d/lab-perms-sync <<'CRON'
# Enforce shared-folder permissions (see March audit)
*/10 * * * * root /usr/local/sbin/lab-perms-sync.sh
CRON
chmod 0644 /etc/cron.d/lab-perms-sync

# A believable history, so `tail` on the log looks routine rather than alarming.
: > /var/log/lab-perms-sync.log
for h in $(seq 72 -1 1); do
  echo "$(date -Iseconds -d "-${h} hours" 2>/dev/null || date -Iseconds) permissions enforced on /srv/lab/shared" \
    >> /var/log/lab-perms-sync.log
done

echo "[fault] installed lab-perms-sync cron — reverts /srv/lab/shared every 10 min"
