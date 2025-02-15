#!/bin/bash

# start the Selenium server in the background
/opt/bin/entry_point.sh &

# wait for the Selenium server to start
sleep 5

unattended-upgrade

sleep 200

# start the cron_docker.sh script as the seluser user
su -c "/home/seluser/select-freeboxos/cron_docker.sh" seluser
