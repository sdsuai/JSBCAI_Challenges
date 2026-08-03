#!/usr/bin/env bash
# disaster.sh — destroys lab-server and gives you a bare one back.
#
# This is the Part G drill. Grade 3 only.
#
#   ./lab/disaster.sh              ask first
#   ./lab/disaster.sh --yes        no prompt
#
# What it does:
#   1. Deletes lab-server and everything on it. Permanently.
#   2. Launches a fresh, EMPTY Ubuntu VM with the same name.
#   3. Restores /etc/hosts on both machines so they can see each other.
#   4. Stops. It installs nothing. No slapd, no NFS, no users, no data.
#
# What it deliberately does NOT do: run our provisioning scripts. Rebuilding
# from `bootstrap.sh` would prove nothing — that is OUR work, not yours. The
# drill is to rebuild from YOUR committed artifacts: your LDIF, your backup,
# your hardened sshd_config, your backup job, your runbooks.
#
# ─────────────────────────────────────────────────────────────────────────────
# BEFORE YOU RUN THIS, READ THE TICKET (README, Part G) AND THEN READ THIS:
#
# This is the one command in the whole challenge that is genuinely
# irreversible, and it is irreversible on purpose. If your backup is
# incomplete, you find out now. If your LDIF was typed by hand instead of
# committed, you find out now. If your runbook says "restore the usual way",
# you find out now.
#
# That discovery IS the exercise. Do not tidy up first to make it go smoothly.
# The most valuable thing you will produce in this challenge is an honest list
# of what you could not get back.
#
# Start a timer when it finishes. Stop it when `./lab/verify.sh` is green.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER="lab-server"
WS="lab-ws"
IMAGE="22.04"
MEM="1G"; DISK="8G"; CPUS="1"
ASSUME_YES=0

for arg in "$@"; do
  case "$arg" in
    --yes|-y)  ASSUME_YES=1 ;;
    --small)   MEM="768M"; DISK="6G" ;;
    -h|--help) sed -n '2,40p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
die() { printf '\033[31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

command -v multipass >/dev/null 2>&1 || die "multipass not found"

cat <<'EOF'

  ┌──────────────────────────────────────────────────────────────┐
  │  This DESTROYS lab-server and everything on it.              │
  │                                                              │
  │  Not a snapshot. Not recoverable. The directory, the data,   │
  │  the exports, your hardening, your backup job — all gone.    │
  │                                                              │
  │  You get back an empty Ubuntu VM and whatever you committed  │
  │  to your own repo.                                           │
  └──────────────────────────────────────────────────────────────┘

EOF

echo "Before continuing, honestly answer these. Write the answers down; Part G"
echo "asks you to compare them with what actually happened."
echo
echo "   1. Can you recreate every account and group without touching the old server?"
echo "   2. Is /srv/lab/shared and /srv/lab/datasets in a backup you have RESTORED from?"
echo "   3. Is your hardened sshd_config committed, or only on the box you are about to delete?"
echo "   4. How long do you think this will take you?"
echo

if [ "$ASSUME_YES" -ne 1 ]; then
  printf 'Type "destroy lab-server" to continue: '
  read -r reply
  [ "$reply" = "destroy lab-server" ] || { echo "Aborted. Nothing changed."; exit 1; }
fi

say "Destroying $SERVER"
multipass delete "$SERVER" --purge 2>/dev/null || true

say "Launching a bare $SERVER (no provisioning)"
multipass launch "$IMAGE" --name "$SERVER" --memory "$MEM" --disk "$DISK" --cpus "$CPUS"

say "Restoring name resolution"
vm_ip() { multipass info "$1" --format csv 2>/dev/null | awk -F, 'NR==2 {print $3}' | awk '{print $1}'; }
SERVER_IP="$(vm_ip "$SERVER")"
WS_IP="$(vm_ip "$WS")"
[ -n "$SERVER_IP" ] || die "could not determine $SERVER IP"

for vm in "$SERVER" "$WS"; do
  multipass info "$vm" >/dev/null 2>&1 || continue
  multipass exec "$vm" -- sudo bash -c "
    sed -i '/lab-server/d;/lab-ws/d' /etc/hosts
    echo '$SERVER_IP lab-server' >> /etc/hosts
    echo '${WS_IP:-127.0.0.1} lab-ws' >> /etc/hosts
  "
done

say "Done. The server is bare."
cat <<EOF

    lab-server   $SERVER_IP   (empty Ubuntu — nothing installed)
    lab-ws       ${WS_IP:-unknown}   (untouched, and its mounts are now dead)

  START YOUR TIMER.

  Rebuild from your own committed work. When you think you are finished:

      ./lab/verify.sh

  Every INFRA check and every ticket check must be green again. Then write
  runbooks/DR-REPORT.md — how long it took, what you could not recover, and
  what you have changed so that next time you can.

  Note that lab-ws still has stale NFS mounts pointing at a server that no
  longer has those exports. Dealing with that is part of the drill.

EOF
