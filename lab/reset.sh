#!/usr/bin/env bash
# reset.sh — destroy both VMs and rebuild the lab from scratch.
#
#   ./lab/reset.sh              ask first, then rebuild
#   ./lab/reset.sh --yes        no prompt
#   ./lab/reset.sh --destroy    tear down and DO NOT rebuild
#
# Use this freely. The whole point of a disposable lab is that you can try the
# command you are not sure about and find out what it does. Ten minutes to
# rebuild is a cheap price for actually understanding something.
#
# WHAT YOU LOSE: everything inside the VMs — your fixes, your runbooks, your
# scripts. Keep your work in this git repo on your own machine and copy it in,
# rather than editing only inside the VM. That is the habit that saves you, and
# it is also why the tickets ask for committed scripts rather than a shell
# history: work that exists only on one box is work that dies with the box.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER="lab-server"
WS="lab-ws"
ASSUME_YES=0
REBUILD=1

for arg in "$@"; do
  case "$arg" in
    --yes|-y)  ASSUME_YES=1 ;;
    --destroy) REBUILD=0 ;;
    -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

command -v multipass >/dev/null 2>&1 || { echo "multipass not found" >&2; exit 2; }

echo
echo "This will DESTROY these VMs and everything inside them:"
for vm in "$SERVER" "$WS"; do
  if multipass info "$vm" >/dev/null 2>&1; then echo "    $vm"; else echo "    $vm (not present)"; fi
done
echo
[ "$REBUILD" -eq 1 ] && echo "It will then rebuild from scratch." || echo "It will NOT rebuild."
echo

if [ "$ASSUME_YES" -ne 1 ]; then
  printf 'Type "destroy" to continue: '
  read -r reply
  [ "$reply" = "destroy" ] || { echo "Aborted. Nothing changed."; exit 1; }
fi

for vm in "$SERVER" "$WS"; do
  if multipass info "$vm" >/dev/null 2>&1; then
    echo "deleting $vm"
    multipass delete "$vm" --purge
  fi
done

if [ "$REBUILD" -eq 1 ]; then
  echo
  exec "$HERE/bootstrap.sh"
fi

echo "Done. Rebuild any time with ./lab/bootstrap.sh"
