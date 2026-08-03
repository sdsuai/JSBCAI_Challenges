#!/usr/bin/env bash
# server-40-slow-link.sh — makes the network slow, the way a bad link is slow.
#
# SPOILER WARNING. This is the answer to Ticket E3.
#
# Adds 30 ms of latency (with a little jitter) to everything leaving the
# server, using tc's netem qdisc. Bandwidth is untouched — this is a LATENCY
# fault, and that distinction is the entire point of the ticket.
#
# Why it matters: a 30 ms round trip barely affects one big file, because the
# transfer pipelines. It is devastating for a directory of small files, because
# NFS makes several round trips PER FILE — lookup, open, read, close. Copy 500
# small files and you have paid 30 ms thousands of times.
#
# Candidates who "test the network" with a single big `dd` will measure a
# perfectly healthy link and conclude the problem is elsewhere. That is the
# trap, and it is a trap real engineers fall into constantly.
#
# Note this does NOT survive a reboot. That is realistic (and a small hint):
# a fault that vanishes when you reboot and returns when someone re-runs a
# script is a different kind of problem from a bad cable.
#
# To remove:            sudo tc qdisc del dev <iface> root
# To see it:            tc qdisc show dev <iface>
# To measure honestly:  ping, plus iperf3, plus a many-small-files copy

set -euo pipefail

IFACE="$(ip route show default 2>/dev/null | awk '/default/ {print $5; exit}')"
[ -n "$IFACE" ] || { echo "[fault] no default interface found" >&2; exit 1; }

tc qdisc del dev "$IFACE" root 2>/dev/null || true
tc qdisc add dev "$IFACE" root netem delay 30ms 5ms distribution normal

echo "[fault] added 30ms +/-5ms latency on ${IFACE} (bandwidth untouched)"
