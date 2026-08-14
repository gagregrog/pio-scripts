#!/usr/bin/env bash
# Watches /dev/cu.* and prints devices as they appear or disappear, so you
# can plug a board in and immediately see which port it landed on.
#
# Usage:
#   scripts/watch_usb_devices.sh [interval_seconds]
#
# Ctrl-C to stop.

set -euo pipefail

interval="${1:-1}"
glob="${WATCH_GLOB:-/dev/cu.*}"

list_devices() {
  shopt -s nullglob
  local devices=($glob)
  shopt -u nullglob
  printf '%s\n' "${devices[@]}" | sort
}

diff_lines() {
  # $1 = mode: 13 (only in new) or 23 (only in old)
  comm "-$1" <(printf '%s\n' "$prev") <(printf '%s\n' "$curr")
}

prev="$(list_devices)"
echo "Watching $glob (every ${interval}s). Ctrl-C to stop."
echo "Current devices:"
if [ -n "$prev" ]; then
  printf '%s\n' "$prev" | sed 's/^/  /'
else
  echo "  (none)"
fi

trap 'echo; echo "Stopped."; exit 0' INT

while true; do
  sleep "$interval"
  curr="$(list_devices)"
  if [ "$curr" != "$prev" ]; then
    ts="$(date '+%H:%M:%S')"
    added="$(diff_lines 13)"
    removed="$(diff_lines 23)"
    if [ -n "$added" ]; then
      while IFS= read -r dev; do
        [ -n "$dev" ] && echo "[$ts] + $dev"
      done <<< "$added"
    fi
    if [ -n "$removed" ]; then
      while IFS= read -r dev; do
        [ -n "$dev" ] && echo "[$ts] - $dev"
      done <<< "$removed"
    fi
    prev="$curr"
  fi
done
