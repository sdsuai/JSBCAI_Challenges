#!/usr/bin/env bash
# server.sh — provisions lab-server: LDAP directory, NFS exports, SSH.
#
# Runs as root inside the VM. Idempotent — re-running is cheap.
#
# What you get:
#   slapd          directory at dc=jsbcai,dc=lab, seeded with users and groups
#   nfs-kernel     three exports under /srv/lab
#   sshd           running, deliberately NOT hardened (that is Part D)

set -euo pipefail
# shellcheck source=/opt/lab/common.sh
source /opt/lab/common.sh

# ---------------------------------------------------------------------------
# Packages
# ---------------------------------------------------------------------------
if ! already_done packages; then
  log "installing packages"
  wait_for_apt
  apt-get update -y

  # slapd asks questions during install. Preseed them or the install hangs
  # forever with no visible prompt.
  debconf-set-selections <<EOF
slapd slapd/no_configuration boolean false
slapd slapd/domain string ${LAB_DOMAIN}
slapd shared/organization string JSBCAI Lab
slapd slapd/password1 password ${LAB_ADMIN_PW}
slapd slapd/password2 password ${LAB_ADMIN_PW}
slapd slapd/backend select MDB
slapd slapd/purge_database boolean false
slapd slapd/move_old_database boolean true
EOF

  apt_install slapd ldap-utils nfs-kernel-server rsync iperf3 acl quota \
              net-tools iproute2 tcpdump jq tree
  mark_done packages
fi

# The domain only takes effect if debconf ran with our answers; force it.
if ! ldapsearch -x -b "$LAB_BASE_DN" -s base >/dev/null 2>&1; then
  log "reconfiguring slapd for ${LAB_BASE_DN}"
  dpkg-reconfigure -f noninteractive slapd
fi
systemctl enable --now slapd >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# Directory contents
# ---------------------------------------------------------------------------
ldap_add() {
  local file="$1" rc=0
  # Capture the status explicitly. `set -e` plus `local rc=$?` is a well-known
  # way to lose an exit code, so do not get clever here.
  ldapadd -x -D "$LAB_ADMIN_DN" -w "$LAB_ADMIN_PW" -f "$file" >/dev/null 2>&1 || rc=$?
  case "$rc" in
    0)  log "loaded $(basename "$file")" ;;
    68) log "$(basename "$file") already present" ;;   # "Already exists" = fine
    *)  warn "$(basename "$file") failed (rc=$rc) — retrying with output"
        ldapadd -x -D "$LAB_ADMIN_DN" -w "$LAB_ADMIN_PW" -f "$file" || true ;;
  esac
}

if [ -d /opt/lab/seed ]; then
  log "seeding directory"
  for f in /opt/lab/seed/base.ldif /opt/lab/seed/groups.ldif /opt/lab/seed/users.ldif; do
    [ -f "$f" ] && ldap_add "$f"
  done
fi

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------
# Group IDs here MUST match the gidNumber values in seed/groups.ldif. When they
# drift, the workstation resolves a name the server does not agree with, and
# files land owned by a number instead of a person. That is not a bug in this
# script — it is the single most common NFS failure in the wild, and Part B
# asks you to reason about it.
if ! already_done storage; then
  log "creating exports"
  groupadd -g 20001 staff    2>/dev/null || true
  groupadd -g 20002 students 2>/dev/null || true
  groupadd -g 20003 robotics 2>/dev/null || true

  mkdir -p /srv/lab/shared /srv/lab/datasets /srv/lab/home
  chown root:staff    /srv/lab/shared
  chmod 0775          /srv/lab/shared
  chown root:robotics /srv/lab/datasets
  chmod 0755          /srv/lab/datasets
  chmod 0755          /srv/lab/home

  # Some content worth protecting, so backups and restores have a subject.
  mkdir -p /srv/lab/datasets/run-2024-03-11 /srv/lab/shared/notes
  for i in 1 2 3; do
    head -c 262144 /dev/urandom > "/srv/lab/datasets/run-2024-03-11/scan_00${i}.bin"
  done
  printf 'Calibration notes for the March run.\nDo not delete: referenced by the paper draft.\n' \
    > /srv/lab/shared/notes/calibration.md
  printf 'meeting notes\n' > /srv/lab/shared/notes/standup.md
  mkdir -p /srv/lab/shared/tmp
  for i in $(seq 1 40); do head -c 131072 /dev/urandom > "/srv/lab/shared/tmp/scratch_${i}.tmp"; done

  mark_done storage
fi

log "writing /etc/exports"
cat > /etc/exports <<'EOF'
# NFS exports for the JSBCAI lab.
#
# The workstation is the only client. In a real lab this would be a subnet,
# not a wildcard — tightening it is left to you (Part D).
/srv/lab/shared    *(rw,sync,no_subtree_check)
/srv/lab/datasets  *(ro,sync,no_subtree_check)
/srv/lab/home      *(rw,sync,no_subtree_check)
EOF
exportfs -ra
systemctl enable --now nfs-kernel-server >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# SSH — intentionally left soft. Hardening it is Part D.
# ---------------------------------------------------------------------------
systemctl enable --now ssh >/dev/null 2>&1 || true

log "server provisioning complete"
log "  base DN : ${LAB_BASE_DN}"
log "  admin   : ${LAB_ADMIN_DN} / ${LAB_ADMIN_PW}"
log "  exports : $(exportfs -s 2>/dev/null | wc -l) configured"
