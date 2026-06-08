#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
BIN_DIR="$HOME/.local/bin"
UNIT_PATH="$UNIT_DIR/armariumlabs.service"
COMMAND_PATH="$BIN_DIR/ArmariumLabs"
BASHRC="$HOME/.bashrc"
PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'

mkdir -p "$UNIT_DIR" "$BIN_DIR"

"$REPO_ROOT/scripts/setup_runtime.sh"

cat > "$UNIT_PATH" <<EOF
[Unit]
Description=ArmariumLabs local Bergfried server
After=network-online.target

[Service]
Type=simple
WorkingDirectory=$REPO_ROOT
ExecStart=$REPO_ROOT/scripts/serve.sh
Restart=on-failure
RestartSec=5
KillSignal=SIGINT
TimeoutStopSec=20

[Install]
WantedBy=default.target
EOF

ln -sfn "$REPO_ROOT/scripts/ArmariumLabs" "$COMMAND_PATH"

if [ -f "$BASHRC" ] && ! grep -Fq "$PATH_LINE" "$BASHRC"; then
  {
    echo ""
    echo "# ArmariumLabs command"
    echo "$PATH_LINE"
  } >> "$BASHRC"
fi

systemctl --user daemon-reload
systemctl --user enable armariumlabs.service

cat <<EOF
Installed user service:
  $UNIT_PATH

Installed command:
  $COMMAND_PATH

Shell command:
  export PATH="\$HOME/.local/bin:\$PATH"

Start now:
  ArmariumLabs --start

Status:
  ArmariumLabs --status

Stop:
  ArmariumLabs --stop
EOF
