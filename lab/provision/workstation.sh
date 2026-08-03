#!/usr/bin/env bash
# workstation.sh — provisions lab-ws: the machine you actually work from.
#
#   usage: workstation.sh <server-ip>
#
# What you get:
#   nfs-common     so you can mount the server's exports
#   nslcd          so `id alice` resolves against LDAP instead of /etc/passwd
#   iperf3, tc     for the throughput work in Part E
#
# The nslcd part is the interesting one. Without it this box has no idea who
# "alice" is, so an NFS file owned by uid 10001 shows up as the bare number
# 10001. With it, both machines agree on the same name-to-number mapping, which
# is the entire reason a lab runs a directory service at all.

set -euo pipefail
# shellcheck source=/opt/lab/common.sh
source /opt/lab/common.sh

SERVER_IP="${1:-}"
[ -n "$SERVER_IP" ] || die "usage: workstation.sh <server-ip>"

if ! already_done packages; then
  log "installing packages"
  wait_for_apt
  apt-get update -y

  # nslcd prompts for its URI/base during install; preseed to keep it silent.
  debconf-set-selections <<EOF
nslcd nslcd/ldap-uris string ldap://${SERVER_IP}/
nslcd nslcd/ldap-base string ${LAB_BASE_DN}
nslcd nslcd/ldap-auth-type select none
libnss-ldapd libnss-ldapd/nsswitch multiselect passwd, group, shadow
EOF

  apt_install nfs-common ldap-utils libnss-ldapd nslcd rsync iperf3 \
              net-tools iproute2 tcpdump jq tree
  mark_done packages
fi

# ---------------------------------------------------------------------------
# Name resolution against the directory
# ---------------------------------------------------------------------------
log "pointing nslcd at ldap://${SERVER_IP}/"
cat > /etc/nslcd.conf <<EOF
# Managed by lab provisioning.
uid nslcd
gid nslcd
uri ldap://${SERVER_IP}/
base ${LAB_BASE_DN}
# Anonymous bind. Fine for a disposable lab on a private network; Part D asks
# you what is wrong with it and what you would do instead.
EOF
chmod 0600 /etc/nslcd.conf
chown root:root /etc/nslcd.conf

# nsswitch decides the ORDER lookups are tried. files first, then ldap, so a
# local account always wins over a directory one — which is what keeps you able
# to log in when the directory is down.
log "updating /etc/nsswitch.conf"
sed -i -E \
  -e 's/^passwd:.*/passwd:         files systemd ldap/' \
  -e 's/^group:.*/group:          files systemd ldap/' \
  -e 's/^shadow:.*/shadow:         files ldap/' \
  /etc/nsswitch.conf

systemctl enable nslcd >/dev/null 2>&1 || true
systemctl restart nslcd || warn "nslcd failed to start — 'journalctl -u nslcd' will say why"

# ---------------------------------------------------------------------------
# Mount the shares
# ---------------------------------------------------------------------------
# fstab entries, so the mounts survive a reboot. `_netdev` tells systemd to
# wait for the network; without it a reboot races the mount and fails.
log "configuring mounts"
mkdir -p /mnt/shared /mnt/datasets
if ! grep -q '/mnt/shared' /etc/fstab; then
  cat >> /etc/fstab <<EOF

# JSBCAI lab shares
${SERVER_IP}:/srv/lab/shared    /mnt/shared    nfs  defaults,_netdev  0  0
${SERVER_IP}:/srv/lab/datasets  /mnt/datasets  nfs  defaults,_netdev,ro  0  0
EOF
fi

systemctl daemon-reload
mount -a || warn "mount -a reported a problem — 'dmesg | tail' and 'showmount -e ${SERVER_IP}'"

log "workstation provisioning complete"
if mountpoint -q /mnt/shared; then
  log "  /mnt/shared mounted"
else
  warn "  /mnt/shared NOT mounted — this may be one of your tickets"
fi
