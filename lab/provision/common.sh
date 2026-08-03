#!/usr/bin/env bash
# common.sh — helpers sourced by server.sh and workstation.sh.
#
# Nothing exciting, but two of these save real pain:
#
#   wait_for_apt  Ubuntu cloud images run unattended-upgrades at first boot,
#                 which holds the dpkg lock for a minute or two. Installing
#                 without waiting is THE classic provisioning failure, and the
#                 error message ("Could not get lock /var/lib/dpkg/lock-frontend")
#                 tells you nothing about why.
#
#   already_done  Makes provisioning idempotent, so re-running bootstrap.sh is
#                 cheap and safe instead of a second full install.

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

LAB_DOMAIN="jsbcai.lab"
LAB_BASE_DN="dc=jsbcai,dc=lab"
LAB_ADMIN_DN="cn=admin,${LAB_BASE_DN}"

# Deliberately weak and deliberately committed. This lab is disposable and
# reachable only from your own machine. Do not carry this habit anywhere real —
# and note that "the admin password is in the repo" is itself one of the things
# Part D asks you to have an opinion about.
LAB_ADMIN_PW="labadmin"

STAMP_DIR="/var/lib/lab-provision"

log()  { printf '\033[36m[lab]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[lab]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[31m[lab] ERROR: %s\033[0m\n' "$*" >&2; exit 1; }

wait_for_apt() {
  local waited=0
  while fuser /var/lib/dpkg/lock-frontend /var/lib/apt/lists/lock \
              /var/cache/apt/archives/lock >/dev/null 2>&1; do
    if [ "$waited" -eq 0 ]; then log "waiting for unattended-upgrades to release apt..."; fi
    sleep 3
    waited=$((waited + 3))
    [ "$waited" -ge 300 ] && die "apt still locked after 5 minutes"
  done
  # cloud-init may still be finishing; it also touches apt
  command -v cloud-init >/dev/null 2>&1 && cloud-init status --wait >/dev/null 2>&1 || true
}

apt_install() {
  wait_for_apt
  apt-get install -y --no-install-recommends "$@"
}

already_done() {
  local stamp="${STAMP_DIR}/$1"
  [ -f "$stamp" ]
}

mark_done() {
  mkdir -p "$STAMP_DIR"
  date -Iseconds > "${STAMP_DIR}/$1"
}
