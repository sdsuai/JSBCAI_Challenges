#!/usr/bin/env bash
# ws-10-uid-collision.sh — makes the workstation disagree with the server
# about who somebody is.
#
# SPOILER WARNING. This is the answer to Ticket B3.
#
# Creates a LOCAL account on the workstation with uidNumber 10002 — the same
# number the directory hands to `bob`. Because /etc/nsswitch.conf resolves
# `files` before `ldap`, the local entry wins.
#
# Symptom: files bob created on the server show up on the workstation owned by
# `svc-capture`, and anything `svc-capture` writes appears on the server as
# though bob wrote it. Nobody's password was stolen and nothing was hacked.
# Two machines simply disagree about what the number 10002 means.
#
# This is the single most important idea in the storage half of this challenge:
#
#     NFS does not send usernames. It sends NUMBERS.
#
# The permission check happens against a uid/gid that the CLIENT asserted, and
# the server trusts it. Every machine must agree on the mapping — which is the
# entire reason a lab runs a directory service instead of maintaining
# /etc/passwd by hand on twelve computers.
#
# Fixing it by renumbering the local account is only half an answer. The other
# half is: who else could this have happened to, and what stops it recurring?

set -euo pipefail

if id svc-capture >/dev/null 2>&1; then
  echo "[fault] svc-capture already exists"
else
  # A service account somebody added by hand months ago, taking the next free
  # uid at the time — which is exactly how these collisions happen.
  groupadd -g 10002 svc-capture 2>/dev/null || true
  useradd -u 10002 -g 10002 -M -s /usr/sbin/nologin \
          -c "capture rig service account" svc-capture 2>/dev/null || true
  echo "[fault] created local svc-capture with uid 10002 (collides with bob)"
fi

# Leave a file on the share owned by that uid, so the collision is visible
# rather than theoretical.
if mountpoint -q /mnt/shared 2>/dev/null; then
  install -d -m 0775 /mnt/shared/capture 2>/dev/null || true
  echo "frame index written by the capture rig" > /mnt/shared/capture/index.txt 2>/dev/null || true
  chown 10002:10002 /mnt/shared/capture/index.txt 2>/dev/null || true
  echo "[fault] wrote /mnt/shared/capture/index.txt owned by uid 10002"
fi
