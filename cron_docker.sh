#!/bin/bash

CONFIG_FILE="/home/seluser/.config/select_freeboxos/cron_docker.conf"
TIMESTAMP_FILE="/home/seluser/.local/share/select_freeboxos/last_update_check"

START_FREEBOXOS="true"
AUTO_UPDATE="false"

while true; do
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    else
        echo "Warning: Config file not found. Using default values." >> /var/log/select_freeboxos/auto_update.log 2>&1
    fi

    if [ "$AUTO_UPDATE" = "true" ]; then
        CURRENT_TIME=$(date +%s)

        LAST_UPDATE=$(cat "$TIMESTAMP_FILE" 2>/dev/null || echo 0)

        if (( CURRENT_TIME - LAST_UPDATE >= 86400 )); then
            echo "[$(date)] Starting daily auto-update check" >> /var/log/select_freeboxos/auto_update.log 2>&1
            cd /home/seluser/select-freeboxos && bash auto_update.sh >> /var/log/select_freeboxos/auto_update.log 2>&1

            echo "$CURRENT_TIME" > "$TIMESTAMP_FILE"
        fi
    fi

    sleep 150

    if [ "$START_FREEBOXOS" = "true" ]; then
        /home/seluser/.venv/bin/python3 /home/seluser/select-freeboxos/cron_docker.py >> /var/log/select_freeboxos/select_freeboxos.log 2>&1
    fi

    sleep 150
done
