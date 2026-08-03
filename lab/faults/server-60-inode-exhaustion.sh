#!/usr/bin/env bash
# server-60-inode-exhaustion.sh — "the disk is full" when the disk is not full.
#
# SPOILER WARNING. This is the answer to Ticket B4. Diagnose it first.
#
# Creates a small loopback filesystem at /srv/lab/scratch with very few inodes,
# then uses them all up with tiny files.
#
# The symptom is the point:
#
#     $ df -h /srv/lab/scratch
#     Filesystem  Size  Used Avail Use% Mounted on
#     /dev/loop0   28M  1.1M   25M   5% /srv/lab/scratch     <-- 95% FREE
#
#     $ touch /srv/lab/scratch/anything
#     touch: cannot touch 'anything': No space left on device
#
# A filesystem has two separate finite resources: DATA BLOCKS (bytes) and
# INODES (one per file, allocated when the filesystem is created and fixed
# forever after). Run out of either and writes fail with ENOSPC — the same
# errno, the same message, completely different cause and completely different
# fix. `df -h` only shows you the first one. `df -i` shows the other.
#
# This is a genuinely senior diagnostic: everyone checks `df -h`, sees free
# space, and concludes the error message is lying. A candidate who reaches for
# `df -i` — or who thinks "ENOSPC has two causes" — is someone who has either
# been bitten before or actually understands filesystems.
#
# The real-world version is a mail spool, a session directory, or a build
# cache that accumulates millions of tiny files. It is common and it takes
# down real services.
#
# The fix is more than `rm`. Deleting files frees the inodes, but the
# filesystem still has a fixed inode count that will be exhausted again. The
# complete answer says what changes so it does not recur.

set -euo pipefail

IMG=/var/lib/lab-scratch.img
MNT=/srv/lab/scratch

if mountpoint -q "$MNT" 2>/dev/null; then
  echo "[fault] $MNT already mounted — skipping"
  exit 0
fi

mkdir -p "$MNT"

# 32 MB image, deliberately few inodes.
dd if=/dev/zero of="$IMG" bs=1M count=32 status=none

# -N sets the inode count directly. Some e2fsprogs builds refuse very low
# values, so fall back to a large bytes-per-inode ratio, which gets there the
# other way round. One of these always works.
mkfs.ext4 -q -F -N 128 "$IMG" >/dev/null 2>&1 \
  || mkfs.ext4 -q -F -i 262144 "$IMG" >/dev/null 2>&1 \
  || { echo "[fault] could not create the scratch filesystem" >&2; exit 1; }

# Survive a reboot, like a real mount would.
if ! grep -q "$MNT" /etc/fstab; then
  echo "$IMG  $MNT  ext4  loop,defaults  0  0" >> /etc/fstab
fi
mount "$IMG" "$MNT" -o loop

chmod 1777 "$MNT"

# Burn the inodes with tiny files, so bytes stay near zero.
mkdir -p "$MNT/capture-cache"
i=0
while : ; do
  if ! : > "$MNT/capture-cache/frame_${i}.idx" 2>/dev/null; then
    break
  fi
  i=$((i + 1))
  [ "$i" -gt 5000 ] && break     # backstop; should hit the inode wall well before
done

echo "[fault] $MNT out of inodes after ${i} files"
df -h "$MNT" | tail -1 | sed 's/^/[fault]   df -h: /'
df -i "$MNT" | tail -1 | sed 's/^/[fault]   df -i: /'
