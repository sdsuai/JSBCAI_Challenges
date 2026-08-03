#!/usr/bin/env bash
# bootstrap.sh — build the lab: two Ubuntu VMs, provisioned and networked.
#
#   ./lab/bootstrap.sh              build it
#   ./lab/bootstrap.sh --small      768M VMs, for a 4 GB laptop
#   ./lab/bootstrap.sh --no-faults  build it healthy (see below)
#
# Takes 5-10 minutes the first time (it downloads an Ubuntu image), ~2 minutes
# after that. Safe to re-run: it skips VMs that already exist.
#
#   lab-server   slapd (LDAP), nfs-kernel-server, sshd     — "the lab server"
#   lab-ws       the workstation you work FROM              — your shell
#
# Both are throwaway. Nothing here touches your real machine, and `reset.sh`
# puts everything back to a clean build. That is deliberate: it means you can
# try the dangerous thing and find out what it does.
#
# BY DEFAULT THIS INJECTS FAULTS. The lab does not come up healthy — several
# tickets in the README describe symptoms you then have to diagnose. That is
# the assignment. `--no-faults` gives you a clean lab if you want to explore
# first, but you must run the faulted build for your actual submission.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="22.04"
SERVER="lab-server"
WS="lab-ws"
MEM="1G"
DISK="8G"
CPUS="1"
INJECT_FAULTS=1

for arg in "$@"; do
  case "$arg" in
    --small)      MEM="768M"; DISK="6G" ;;
    --no-faults)  INJECT_FAULTS=0 ;;
    -h|--help)    sed -n '2,25p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

say()  { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
info() { printf '    %s\n' "$*"; }
die()  { printf '\033[31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

command -v multipass >/dev/null 2>&1 || die "multipass not found — run ./lab/preflight.sh"

# ---------------------------------------------------------------------------
launch() {
  local name="$1"
  if multipass info "$name" >/dev/null 2>&1; then
    info "$name already exists — skipping launch"
  else
    info "launching $name (${MEM} RAM, ${DISK} disk)"
    multipass launch "$IMAGE" --name "$name" --memory "$MEM" --disk "$DISK" --cpus "$CPUS"
  fi
  multipass info "$name" >/dev/null 2>&1 || die "failed to launch $name"
}

vm_ip() {
  # First IPv4 of the VM. `multipass info --format csv` is stable across
  # versions; parsing the human-readable output is not.
  multipass info "$1" --format csv 2>/dev/null | awk -F, 'NR==2 {print $3}' | awk '{print $1}'
}

# Copy a local file into a VM. multipass transfer cannot write to root-owned
# paths, so land it in /home/ubuntu first and move it with sudo.
push() {
  local vm="$1" src="$2" dest="$3" mode="${4:-0644}"
  local tmp="/home/ubuntu/.push.$$"
  multipass transfer "$src" "${vm}:${tmp}"
  multipass exec "$vm" -- sudo install -D -m "$mode" "$tmp" "$dest"
  multipass exec "$vm" -- rm -f "$tmp"
}

say "Launching VMs"
launch "$SERVER"
launch "$WS"

say "Discovering addresses"
SERVER_IP="$(vm_ip "$SERVER")"
WS_IP="$(vm_ip "$WS")"
[ -n "$SERVER_IP" ] || die "could not determine $SERVER IP"
[ -n "$WS_IP" ]     || die "could not determine $WS IP"
info "$SERVER = $SERVER_IP"
info "$WS     = $WS_IP"

say "Wiring name resolution"
# multipass gives the VMs addresses but no shared DNS, so each host learns the
# other by /etc/hosts. Real labs use DNS; this keeps the challenge focused.
for vm in "$SERVER" "$WS"; do
  multipass exec "$vm" -- sudo bash -c "
    sed -i '/lab-server/d;/lab-ws/d' /etc/hosts
    echo '$SERVER_IP lab-server' >> /etc/hosts
    echo '$WS_IP lab-ws'         >> /etc/hosts
  "
done
info "both VMs can now resolve lab-server and lab-ws"

say "Provisioning $SERVER  (LDAP + NFS + SSH — a few minutes)"
push "$SERVER" "$HERE/provision/common.sh"  /opt/lab/common.sh  0755
push "$SERVER" "$HERE/provision/server.sh"  /opt/lab/server.sh  0755
for f in "$HERE"/seed/*.ldif; do
  push "$SERVER" "$f" "/opt/lab/seed/$(basename "$f")"
done
multipass exec "$SERVER" -- sudo /opt/lab/server.sh

say "Provisioning $WS  (NFS client + LDAP client)"
push "$WS" "$HERE/provision/common.sh"      /opt/lab/common.sh      0755
push "$WS" "$HERE/provision/workstation.sh" /opt/lab/workstation.sh 0755
multipass exec "$WS" -- sudo /opt/lab/workstation.sh "$SERVER_IP"

if [ "$INJECT_FAULTS" -eq 1 ]; then
  say "Injecting faults"
  info "the lab is now BROKEN in several specific ways — that is the assignment"

  # The triage log has to be on the server before server-30 plants it.
  if [ -f "$HERE/../logs/auth.log" ]; then
    push "$SERVER" "$HERE/../logs/auth.log" /opt/lab/logs/auth.log 0644
  fi

  # faults/server-*.sh run on lab-server, faults/ws-*.sh run on lab-ws.
  for f in "$HERE"/faults/*.sh; do
    [ -e "$f" ] || continue
    name="$(basename "$f")"
    case "$name" in
      server-*) target="$SERVER" ;;
      ws-*)     target="$WS" ;;
      *)        info "skipping $name (name must start with server- or ws-)"; continue ;;
    esac
    info "applying $name on $target"
    push "$target" "$f" "/opt/lab/faults/$name" 0755
    multipass exec "$target" -- sudo "/opt/lab/faults/$name" "$SERVER_IP" "$WS_IP" || \
      info "  ($name exited non-zero — continuing)"
  done
else
  say "Skipping fault injection (--no-faults)"
fi

say "Lab is up"
cat <<EOF

    lab-server   $SERVER_IP
    lab-ws       $WS_IP

  Get a shell on the workstation — this is where you work:

      multipass shell $WS

  Or run one command:

      multipass exec $WS -- id alice

  Check what is and is not working:

      ./lab/verify.sh

  Start over from a clean build at any time:

      ./lab/reset.sh

EOF

if [ "$INJECT_FAULTS" -eq 1 ]; then
  cat <<'EOF'
  Several things are deliberately broken. ./lab/verify.sh will show you which
  checks fail — those failures ARE your tickets. Read the README for the
  context each one comes with.

EOF
fi
