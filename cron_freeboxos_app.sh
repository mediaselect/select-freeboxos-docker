echo --- start: $(date) >> /var/log/select_freeboxos/cron_freeboxos.log
export DISPLAY=:99
/home/seluser/.venv/bin/python3 /home/seluser/select-freeboxos/freeboxos.py >> /var/log/select_freeboxos/cron_freeboxos.log 2>&1
echo --- end: $(date) >> /var/log/select_freeboxos/cron_freeboxos.log
