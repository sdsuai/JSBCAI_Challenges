#!/usr/bin/env bash
# server-10-shared-perms.sh — breaks writing to the shared folder.
#
# SPOILER WARNING. Reading this file tells you the answer to Ticket B1. You
# will learn more by diagnosing it first; the diagnosis is the skill, not the
# fix. Come back afterwards to check you understood the whole cause.
#
# What this does: leaves /srv/lab/shared owned root:staff but strips group
# write, and leaves the setgid bit off.
#
# Symptom the user reports: "I can't save anything to the shared drive."
#
# There are two separate problems stacked here, and a candidate who fixes only
# the first will think they are done:
#   1. group cannot write            -> chmod
#   2. new files do not inherit the  -> setgid bit on the directory, so that
#      group, so the NEXT person        files created inside it belong to the
#      hits the same wall               folder's group rather than the
#                                       creator's primary group
# Fixing (1) alone makes the reporter happy today and reproduces the ticket
# next week. That difference is most of what this part is testing.

set -euo pipefail

TARGET="/srv/lab/shared"

chown root:staff "$TARGET"
chmod 0755 "$TARGET"          # g-w, and no setgid
find "$TARGET" -mindepth 1 -maxdepth 1 -type d -exec chmod 0755 {} \;

echo "[fault] $TARGET is now 0755 root:staff (group cannot write, no setgid)"
