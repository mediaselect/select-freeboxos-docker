#!/bin/bash
set -e

# 1. Start Selenium server in the background
/opt/bin/entry_point.sh &

# 2. Wait for the Selenium server to initialize
sleep 5

# 3. GPG Key Management (Volume Safety)
SRC_KEY="/home/seluser/select-freeboxos/.gpg/public.key"
DEST_DIR="/home/seluser/.config/select_freeboxos"
DEST_KEY="$DEST_DIR/public.key"

mkdir -p "$DEST_DIR"
chown -R seluser:seluser "$DEST_DIR"

if [ ! -f "$DEST_KEY" ]; then
    echo "[startup] Installing GPG public key into config volume..."
    cp "$SRC_KEY" "$DEST_KEY"
    chown seluser:seluser "$DEST_KEY"
    chmod 640 "$DEST_KEY"
else
    echo "[startup] GPG public key already present."
fi

# 4. System updates (One-time upgrade at start)
echo "[startup] Checking for system security updates..."
unattended-upgrade

# start the cron_docker.sh script as the seluser user
su -c "/home/seluser/select-freeboxos/cron_docker.sh" seluser
