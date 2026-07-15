#!/usr/bin/env bash
# Watch a process's resident memory (RSS), printed every half second.
# Usage: ./watch_mem.sh <pid>        (Ctrl-C to stop)
#
# Works on macOS and Linux. Windows equivalent (PowerShell):
#   while ($true) { "{0:N0} MB" -f ((Get-Process -Id <pid>).WS / 1MB); Start-Sleep 0.5 }

if [ -z "$1" ]; then
    echo "usage: $0 <pid>" >&2
    exit 1
fi

while rss_kb=$(ps -o rss= -p "$1" 2>/dev/null) && [ -n "$rss_kb" ]; do
    echo "$(date +%H:%M:%S)  $((rss_kb / 1024)) MB"
    sleep 0.5
done
echo "process $1 exited"
