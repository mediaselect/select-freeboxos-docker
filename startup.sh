#!/bin/bash

# start the Selenium server in the background
/opt/bin/entry_point.sh &

# wait for the Selenium server to start
sleep 5

chown -R seluser:seluser /home/seluser/.local/share/select_freeboxos
chown -R seluser:seluser /home/seluser/.config/select_freeboxos

# Run unattended-upgrades
unattended-upgrade

# wait for upgrades to finish
sleep 200

# start the cron_docker.sh script as the seluser user
su -c "/home/seluser/select-freeboxos/cron_docker.sh" seluser
