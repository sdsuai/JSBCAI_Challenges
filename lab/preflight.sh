#!/usr/bin/env bash
# preflight.sh — check this machine can run the lab, BEFORE you burn time on it.
#
# Run this first:   ./lab/preflight.sh
#
# It changes nothing. It only looks. If everything here passes, bootstrap.sh
# will work; if something fails, you get the fix for your platform instead of a
# confusing error twenty minutes in.

set -uo pipefail

PASS=0
FAIL=0
WARN=0

ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; PASS=$((PASS+1)); }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$*"; FAIL=$((FAIL+1)); }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; WARN=$((WARN+1)); }
hint() { printf '      → %s\n' "$*"; }

echo
echo "Lab preflight"
echo "============="
echo

# --- platform ---------------------------------------------------------------
OS="$(uname -s)"
ARCH="$(uname -m)"
echo "Platform: $OS $ARCH"
case "$OS" in
  Darwin) ok "macOS supported (Intel and Apple Silicon both fine)" ;;
  Linux)
    if grep -qi microsoft /proc/version 2>/dev/null; then
      warn "You are inside WSL."
      hint "multipass runs on WINDOWS, not inside WSL. Open PowerShell and run"
      hint "the lab from there, or install multipass in Windows and use it from"
      hint "PowerShell while keeping your editor in WSL."
    else
      ok "Linux supported"
    fi
    ;;
  MINGW*|MSYS*|CYGWIN*)
    warn "Git Bash detected. This script works, but run multipass from PowerShell." ;;
  *) warn "Unrecognised platform '$OS' — multipass may still work" ;;
esac
echo

# --- multipass --------------------------------------------------------------
echo "multipass"
if command -v multipass >/dev/null 2>&1; then
  MP_VER="$(multipass version 2>/dev/null | head -1)"
  ok "installed (${MP_VER:-unknown version})"
  if multipass list >/dev/null 2>&1; then
    ok "daemon reachable"
  else
    bad "installed but the daemon is not responding"
    hint "macOS:   sudo launchctl kickstart -k system/com.canonical.multipassd"
    hint "Linux:   sudo snap restart multipass"
    hint "Windows: restart the 'Multipass' service in services.msc"
  fi
else
  bad "not installed"
  case "$OS" in
    Darwin) hint "brew install --cask multipass" ;;
    Linux)  hint "sudo snap install multipass" ;;
    *)      hint "https://multipass.run/install  (or: winget install Canonical.Multipass)" ;;
  esac
fi
echo

# --- resources --------------------------------------------------------------
echo "Resources (the lab needs ~2 GB RAM and ~16 GB disk for two VMs)"
MEM_GB=""
case "$OS" in
  Darwin) MEM_GB=$(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1024 / 1024 / 1024 )) ;;
  Linux)  MEM_GB=$(( $(awk '/MemTotal/ {print $2}' /proc/meminfo 2>/dev/null || echo 0) / 1024 / 1024 )) ;;
esac
if [ -n "$MEM_GB" ] && [ "$MEM_GB" -gt 0 ]; then
  if   [ "$MEM_GB" -ge 8 ]; then ok "RAM: ${MEM_GB} GB"
  elif [ "$MEM_GB" -ge 4 ]; then warn "RAM: ${MEM_GB} GB — tight but workable"
                                 hint "Use --memory 768M for each VM (see bootstrap.sh)"
  else bad "RAM: ${MEM_GB} GB — not enough for two VMs"
       hint "Run a single combined VM instead; see lab/README.md 'Low-memory mode'"
  fi
else
  warn "could not determine RAM"
fi

DISK_AVAIL="$(df -g . 2>/dev/null | awk 'NR==2 {print $4}' || df -BG . 2>/dev/null | awk 'NR==2 {gsub(/G/,"",$4); print $4}')"
if [ -n "${DISK_AVAIL:-}" ] && [ "$DISK_AVAIL" -ge 20 ] 2>/dev/null; then
  ok "free disk: ${DISK_AVAIL} GB"
elif [ -n "${DISK_AVAIL:-}" ]; then
  warn "free disk: ${DISK_AVAIL} GB — 20 GB recommended"
else
  warn "could not determine free disk space"
fi
echo

# --- virtualization ---------------------------------------------------------
echo "Virtualization"
case "$OS" in
  Darwin)
    ok "Hypervisor.framework is always available on macOS" ;;
  Linux)
    if [ -e /dev/kvm ]; then ok "/dev/kvm present"
    else warn "/dev/kvm missing — multipass will be slow or refuse to start"
         hint "Enable virtualization in BIOS/UEFI, and: sudo adduser \"\$USER\" kvm"
    fi ;;
  *)
    warn "On Windows, multipass needs Hyper-V (Pro/Enterprise) or VirtualBox (Home)"
    hint "Check with: systeminfo | findstr /C:\"Hyper-V\"" ;;
esac
echo

# --- local tooling ----------------------------------------------------------
echo "Local tools (nice to have — everything else lives inside the VMs)"
for t in ssh rsync git; do
  if command -v "$t" >/dev/null 2>&1; then ok "$t"; else warn "$t not found on the host"; fi
done
echo

# --- verdict ----------------------------------------------------------------
echo "-----------------------------------------------"
printf 'passed: %d   warnings: %d   failed: %d\n' "$PASS" "$WARN" "$FAIL"
echo
if [ "$FAIL" -gt 0 ]; then
  echo "Fix the ✗ items above, then run this again."
  echo "Stuck for more than an hour? Email philipamadasun1@gmail.com — setup"
  echo "trouble is not what we are assessing and we would rather unblock you."
  exit 1
fi
echo "Ready. Next:  ./lab/bootstrap.sh"
exit 0
