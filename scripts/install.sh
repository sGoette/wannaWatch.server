#!/bin/sh
set -e

ROOT="/usr/local/wannawatch.server"
RELEASES_DIR="$ROOT/releases"
CURRENT_LINK="$ROOT/current"

# Must run from inside a release folder like /usr/local/wannawatch.server/releases/v0.1.12
RELEASE_DIR="$(pwd)"

info() { echo "✅ $*"; }
warn() { echo "⚠️  $*" >&2; }
die() { echo "❌ $*" >&2; exit 1; }

# --- Preconditions ---
[ "$(id -u)" -eq 0 ] || die "Run as root."
echo "$RELEASE_DIR" | grep -q "^$RELEASES_DIR/" || die "Run this from inside $RELEASES_DIR/<version> (current: $RELEASE_DIR)"

[ -d "$RELEASE_DIR/backend" ] || die "Missing backend/ in $RELEASE_DIR"
[ -d "$RELEASE_DIR/frontend" ] || die "Missing frontend/ in $RELEASE_DIR"

# rc.d script expected at top-level of release
[ -f "$RELEASE_DIR/wannawatch" ] || die "Missing rc.d script file: $RELEASE_DIR/wannawatch"

# --- Create persistent dirs ---
info "Creating persistent directories (if missing)"
mkdir -p "$ROOT/data" \
         "$ROOT/data/db" \
         "$ROOT/data/posters" \
         "$ROOT/logs"

# --- Update 'current' symlink ---
info "Linking current -> $RELEASE_DIR"
ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"

# --- Install system packages ---
info "Installing system packages (Python 3.11 stack + ffmpeg)"
# Keep this minimal; adjust package names if your jail uses a specific python version.
pkg update -f
pkg install -y python3 ffmpeg py311-fastapi py311-uvicorn py311-aiosqlite py311-pydantic2 py311-requests py311-lxml py311-Levenshtein py311-zeroconf

# --- Install rc.d script ---
info "Installing rc.d script to /usr/local/etc/rc.d/wannawatch"
install -m 0555 "$CURRENT_LINK/wannawatch" /usr/local/etc/rc.d/wannawatch

# --- Enable service ---
info "Enabling service (wannawatch_enable=YES)"
if command -v sysrc >/dev/null 2>&1; then
  sysrc wannawatch_enable="YES" >/dev/null
else
  # fallback: add if not present, otherwise replace
  if grep -q '^wannawatch_enable=' /etc/rc.conf; then
    sed -i '' 's/^wannawatch_enable=.*/wannawatch_enable="YES"/' /etc/rc.conf
  else
    echo 'wannawatch_enable="YES"' >> /etc/rc.conf
  fi
fi

# --- Restart service ---
info "Restarting service"
service wannawatch restart || service wannawatch start

info "Done."
echo "Current release: $CURRENT_LINK -> $(readlink $CURRENT_LINK)"
