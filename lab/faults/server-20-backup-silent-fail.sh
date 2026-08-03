#!/usr/bin/env bash
# server-20-backup-silent-fail.sh — installs a backup that backs nothing up.
#
# SPOILER WARNING. This is the answer to Ticket C1. Diagnose first.
#
# The script it installs runs every night, exits 0, writes a cheerful log line,
# and copies almost nothing. Three separate reasons, all of which are real
# mistakes people actually ship:
#
#   1. The source path has a trailing-slash bug combined with a subdirectory
#      that no longer exists, so rsync copies an empty tree.
#   2. An over-broad --exclude swallows the dataset files.
#   3. rsync's exit code is discarded by the `|| true`, so a failure still
#      reports success.
#
# The lesson underneath: a backup job that has never been RESTORED from is not
# a backup, it is a cron entry that makes you feel safe. The log says "OK"
# every single night.

set -euo pipefail

mkdir -p /srv/backup/nightly

cat > /usr/local/bin/lab-backup.sh <<'SCRIPT'
#!/bin/bash
# Nightly backup of the lab share.  -- installed by the previous volunteer
SRC=/srv/lab/shared/current
DEST=/srv/backup/nightly
LOG=/var/log/lab-backup.log

rsync -a --exclude='*.bin' --exclude='tmp' "$SRC/" "$DEST/" >/dev/null 2>&1 || true

echo "$(date -Iseconds) backup OK" >> "$LOG"
SCRIPT
chmod 0755 /usr/local/bin/lab-backup.sh

# A believable history: it has "worked" every night for two weeks.
: > /var/log/lab-backup.log
for d in $(seq 14 -1 1); do
  echo "$(date -Iseconds -d "-${d} days" 2>/dev/null || date -Iseconds) backup OK" \
    >> /var/log/lab-backup.log
done

# Wire it to cron so it is genuinely running, not just sitting there.
cat > /etc/cron.d/lab-backup <<'CRON'
# Nightly lab backup
17 2 * * * root /usr/local/bin/lab-backup.sh
CRON
chmod 0644 /etc/cron.d/lab-backup

# Run it once so /srv/backup/nightly exists and looks plausibly populated.
/usr/local/bin/lab-backup.sh || true

echo "[fault] installed /usr/local/bin/lab-backup.sh + cron, with a 14-day 'OK' history"
