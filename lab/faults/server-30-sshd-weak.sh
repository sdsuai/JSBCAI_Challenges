#!/usr/bin/env bash
# server-30-sshd-weak.sh — loosens sshd, and plants the auth log to match.
#
# SPOILER WARNING. This is most of the answer to Ticket D1 and D2.
#
# Everything set here is something you will genuinely find on a machine that
# has been "temporarily" opened up and never closed again:
#
#   PermitRootLogin yes        direct root login over the network
#   PasswordAuthentication yes brute-forceable, and there IS a brute force in
#                              the log this script installs
#   PermitEmptyPasswords yes   the worst one, and the easiest to miss
#   MaxAuthTries 10            ten guesses per connection instead of the
#                              default three
#   X11Forwarding yes          unnecessary attack surface on a headless server
#
# The judgment part of the ticket: you are about to edit the config of the
# service you are connected THROUGH. Restart it wrong and you lock yourself
# out of a machine you cannot walk over to. `multipass shell` saves you here,
# which is exactly the safety net a real server does not have.

set -euo pipefail

CONF=/etc/ssh/sshd_config

cp -n "$CONF" "${CONF}.lab-original" 2>/dev/null || true

set_opt() {
  local key="$1" val="$2"
  sed -i -E "/^[#[:space:]]*${key}[[:space:]]/d" "$CONF"
  echo "${key} ${val}" >> "$CONF"
}

{
  echo ""
  echo "# --- adjusted for the March demo, revisit later ---"
} >> "$CONF"

set_opt PermitRootLogin yes
set_opt PasswordAuthentication yes
set_opt PermitEmptyPasswords yes
set_opt MaxAuthTries 10
set_opt X11Forwarding yes
set_opt LoginGraceTime 120

# Validate before restarting. Shipping a config that fails to parse would take
# sshd down and strand the candidate for a reason unrelated to the exercise.
if sshd -t 2>/dev/null; then
  systemctl restart ssh 2>/dev/null || systemctl restart sshd 2>/dev/null || true
  echo "[fault] sshd loosened and restarted"
else
  echo "[fault] sshd config invalid, restoring original" >&2
  cp "${CONF}.lab-original" "$CONF"
  exit 1
fi

# Plant the auth log that goes with it. Static and reproducible on purpose —
# every candidate triages exactly the same evidence.
if [ -f /opt/lab/logs/auth.log ]; then
  install -D -m 0640 /opt/lab/logs/auth.log /var/log/lab/auth.log
  echo "[fault] planted /var/log/lab/auth.log for triage"
fi
