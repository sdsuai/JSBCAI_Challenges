#!/usr/bin/env bash
# verify.sh — checks the lab, and tells you which failures are YOUR TICKETS.
#
#   ./lab/verify.sh              everything
#   ./lab/verify.sh --infra      only "is the lab itself healthy"
#   ./lab/verify.sh --part B     only one part's checks
#
# Two kinds of check, and the difference matters:
#
#   [INFRA]   must pass on a fresh build. If one of these fails, bootstrap did
#             not work and nothing you do to the lab will make sense. Re-run
#             ./lab/reset.sh, and email if it still fails.
#
#   [TICKET]  EXPECTED to fail on a fresh build. These are the faults. Turning
#             them green is the assignment. A ticket check going green is
#             necessary but not sufficient — several tickets ask for a root
#             cause and a runbook too, which no script can grade.
#
# This script only reads. It changes nothing, so run it as often as you like.

set -uo pipefail

SERVER="lab-server"
WS="lab-ws"
ONLY_INFRA=0
ONLY_PART=""

while [ $# -gt 0 ]; do
  case "$1" in
    --infra) ONLY_INFRA=1; shift ;;
    --part)  ONLY_PART="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,22p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

INFRA_PASS=0; INFRA_FAIL=0; TICKET_PASS=0; TICKET_FAIL=0
CUR_PART=""

c_ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
c_bad()  { printf '  \033[31m✗\033[0m %s\n' "$*"; }
c_tick() { printf '  \033[33m○\033[0m %s\n' "$*"; }
note()   { printf '      \033[2m%s\033[0m\n' "$*"; }

part() {
  CUR_PART="$1"
  if [ -n "$ONLY_PART" ] && [ "$ONLY_PART" != "$1" ]; then return; fi
  printf '\n\033[1m%s — %s\033[0m\n' "$1" "$2"
}

skip_part() { [ -n "$ONLY_PART" ] && [ "$ONLY_PART" != "$CUR_PART" ]; }

# check <INFRA|TICKET> <description> <vm> <command...>
check() {
  local kind="$1" desc="$2" vm="$3"; shift 3
  skip_part && return 0
  if [ "$ONLY_INFRA" -eq 1 ] && [ "$kind" != "INFRA" ]; then return 0; fi

  if multipass exec "$vm" -- sudo bash -c "$*" >/dev/null 2>&1; then
    if [ "$kind" = "INFRA" ]; then c_ok "$desc"; INFRA_PASS=$((INFRA_PASS+1))
    else c_ok "$desc  (ticket resolved)"; TICKET_PASS=$((TICKET_PASS+1)); fi
    return 0
  else
    if [ "$kind" = "INFRA" ]; then c_bad "$desc"; INFRA_FAIL=$((INFRA_FAIL+1))
    else c_tick "$desc  → TICKET, not yet fixed"; TICKET_FAIL=$((TICKET_FAIL+1)); fi
    return 1
  fi
}

# --------------------------------------------------------------------------
command -v multipass >/dev/null 2>&1 || { echo "multipass not found" >&2; exit 2; }

echo
echo "Lab verification"
echo "================"

part "0" "the lab itself"
for vm in "$SERVER" "$WS"; do
  if multipass info "$vm" >/dev/null 2>&1 && \
     multipass info "$vm" --format csv 2>/dev/null | awk -F, 'NR==2{exit $2=="Running"?0:1}'; then
    c_ok "$vm is running"; INFRA_PASS=$((INFRA_PASS+1))
  else
    c_bad "$vm is not running"; INFRA_FAIL=$((INFRA_FAIL+1))
    note "multipass start $vm     (or ./lab/reset.sh)"
  fi
done

part "A" "identity and accounts (LDAP)"
check INFRA "slapd is running" "$SERVER" \
  "systemctl is-active --quiet slapd"
check INFRA "directory answers at dc=jsbcai,dc=lab" "$SERVER" \
  "ldapsearch -x -b dc=jsbcai,dc=lab -s base >/dev/null"
check INFRA "seeded users present (alice, bob, carol, dave)" "$SERVER" \
  "for u in alice bob carol dave; do ldapsearch -x -b dc=jsbcai,dc=lab \"(uid=\$u)\" uid | grep -q \"^uid: \$u\" || exit 1; done"
check INFRA "groups have the expected gidNumbers" "$SERVER" \
  "ldapsearch -x -b dc=jsbcai,dc=lab '(cn=students)' gidNumber | grep -q 'gidNumber: 20002'"
check TICKET "the three new students exist (A1)" "$SERVER" \
  "for u in erin frank grace; do ldapsearch -x -b dc=jsbcai,dc=lab \"(uid=\$u)\" uid | grep -q \"^uid: \$u\" || exit 1; done"
check TICKET "dave can no longer authenticate (A4)" "$SERVER" \
  "! ldapwhoami -x -D uid=dave,ou=people,dc=jsbcai,dc=lab -w labpass >/dev/null 2>&1"

part "B" "shared storage and permissions (NFS)"
check INFRA "nfs-kernel-server is running" "$SERVER" \
  "systemctl is-active --quiet nfs-kernel-server"
check INFRA "/srv/lab/shared is exported" "$SERVER" \
  "exportfs -s | grep -q /srv/lab/shared"
check INFRA "workstation has /mnt/shared mounted" "$WS" \
  "mountpoint -q /mnt/shared"
check INFRA "workstation resolves alice through the directory" "$WS" \
  "getent passwd alice | grep -q 10001"
check TICKET "a student can write to the share (B1)" "$WS" \
  "runuser -u carol -- test -w /mnt/shared"
check TICKET "the share is setgid, so new files inherit the group (B2)" "$SERVER" \
  "[ -g /srv/lab/shared ]"

part "C" "backups and restore"
check INFRA "a backup job exists" "$SERVER" \
  "test -x /usr/local/bin/lab-backup.sh"
check TICKET "the backup actually contains the dataset files (C1)" "$SERVER" \
  "find /srv/backup -name '*.bin' -size +1k | grep -q ."
check TICKET "the backup contains the calibration notes (C1)" "$SERVER" \
  "find /srv/backup -name 'calibration.md' | grep -q ."
check TICKET "the backup job fails loudly when it fails (C2)" "$SERVER" \
  "! grep -q '|| true' /usr/local/bin/lab-backup.sh"

part "D" "access hardening and log triage"
check INFRA "the auth log is present for triage" "$SERVER" \
  "test -s /var/log/lab/auth.log"
check TICKET "root cannot log in over SSH (D1)" "$SERVER" \
  "sshd -T 2>/dev/null | grep -qi '^permitrootlogin no'"
check TICKET "password authentication is off (D1)" "$SERVER" \
  "sshd -T 2>/dev/null | grep -qi '^passwordauthentication no'"
check TICKET "empty passwords are refused (D1)" "$SERVER" \
  "sshd -T 2>/dev/null | grep -qi '^permitemptypasswords no'"
check TICKET "MaxAuthTries is tightened (D1)" "$SERVER" \
  "v=\$(sshd -T 2>/dev/null | awk '/^maxauthtries/{print \$2}'); [ -n \"\$v\" ] && [ \"\$v\" -le 4 ]"
check TICKET "an incident report was written (D3)" "$SERVER" \
  "test -s /srv/lab/shared/runbooks/INCIDENT.md"

part "F" "runbooks"
check TICKET "runbooks directory exists with content (F1)" "$SERVER" \
  "find /srv/lab/shared/runbooks -name '*.md' 2>/dev/null | grep -q ."

# --------------------------------------------------------------------------
echo
echo "-------------------------------------------------------------"
printf 'infrastructure : \033[32m%d passed\033[0m, ' "$INFRA_PASS"
if [ "$INFRA_FAIL" -gt 0 ]; then printf '\033[31m%d FAILED\033[0m\n' "$INFRA_FAIL"
else printf '%d failed\n' "$INFRA_FAIL"; fi
printf 'tickets        : %d resolved, %d outstanding\n' "$TICKET_PASS" "$TICKET_FAIL"
echo

if [ "$INFRA_FAIL" -gt 0 ]; then
  cat <<'EOF'
Infrastructure checks failed. That is NOT one of your tickets — the lab did not
build correctly. Try:

    ./lab/reset.sh

If it still fails, send the output to philipamadasun1@gmail.com. Setup trouble
is not what we are assessing and we would rather unblock you than watch you
lose two days to it.
EOF
  exit 1
fi

if [ "$TICKET_FAIL" -gt 0 ]; then
  echo "Outstanding tickets above are the work. See the README for the context"
  echo "each one comes with — the check going green is not the whole answer."
else
  echo "All checks green. Make sure your runbooks and write-up are done too:"
  echo "several tickets ask for a root cause and a decision that no script can grade."
fi
exit 0
