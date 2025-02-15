#!/bin/bash

CONFIG_FILE="/home/seluser/.config/select_freeboxos/cron_docker.conf"

START_FREEBOXOS="true"
AUTO_UPDATE="false"

while true; do
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    else
        echo "Warning: Config file not found. Using default values." >> /var/log/select_freeboxos/auto_update.log 2>&1
    fi
    sleep 150
    if [ "$AUTO_UPDATE" = "true" ]; then
        cd /home/seluser/select-freeboxos && bash auto_update.sh >> /var/log/select_freeboxos/auto_update.log 2>&1
    fi
    sleep 150
    if [ "$START_FREEBOXOS" = "true" ]; then
        /home/seluser/.venv/bin/python3 /home/seluser/select-freeboxos/cron_docker.py >> /var/log/select_freeboxos/select_freeboxos.log 2>&1
    fi
done
