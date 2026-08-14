#!/usr/bin/env bash
# Resolves a .local mDNS/Bonjour hostname to an IPv4 address and prints it.
#
# Hostname source, in priority order:
#   1. $1 (command-line argument)
#   2. OTA_HOSTNAME in .env
#   3. interactive prompt
#
# Usage:
#   scripts/resolve_mdns.sh [hostname[.local]]

set -euo pipefail

host="${1:-}"

if [ -z "$host" ] && [ -f .env ]; then
  host="$(grep -E '^OTA_HOSTNAME=' .env | tail -n1 | cut -d'=' -f2- || true)"
fi

if [ -z "$host" ]; then
  read -r -p "mDNS hostname to resolve: " host
fi

if [ -z "$host" ]; then
  echo "No hostname given." >&2
  exit 1
fi

case "$host" in
  *.local) ;;
  *) host="${host}.local" ;;
esac

resolve_dscacheutil() {
  command -v dscacheutil >/dev/null 2>&1 || return 1
  dscacheutil -q host -a name "$host" 2>/dev/null | awk '/^ip_address:/ { print $2; exit }'
}

resolve_avahi() {
  command -v avahi-resolve-host-name >/dev/null 2>&1 || return 1
  avahi-resolve-host-name -4 "$host" 2>/dev/null | awk '{ print $2; exit }'
}

resolve_ping() {
  command -v ping >/dev/null 2>&1 || return 1
  ping -c 1 -W 2 "$host" 2>/dev/null | sed -n 's/.*(\([0-9.]*\)).*/\1/p' | head -n1
}

ip=""
for resolver in resolve_dscacheutil resolve_avahi resolve_ping; do
  ip="$("$resolver" || true)"
  if [ -n "$ip" ]; then
    break
  fi
done

if [ -z "$ip" ]; then
  echo "Could not resolve $host (is the device powered on and connected?)" >&2
  exit 1
fi

echo "$ip"
