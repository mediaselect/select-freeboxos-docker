import logging
import json
import os
import requests
import sys

from pathlib import Path
from subprocess import Popen, PIPE, run
from datetime import datetime
from logging.handlers import RotatingFileHandler

log_file = "/var/log/select_freeboxos/select_freeboxos.log"
max_bytes = 10 * 1024 * 1024  # 10 MB
backup_count = 5
log_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)

log_format = '%(asctime)s %(levelname)s %(message)s'
log_datefmt = '%d-%m-%Y %H:%M:%S'
formatter = logging.Formatter(log_format, log_datefmt)

log_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(log_handler)

logger.setLevel(logging.INFO)

CONFIG_PATH = Path("/home/seluser/.config/select_freeboxos/config.json")

try:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    logger.error("Missing config.json file")
    sys.exit(1)
except json.JSONDecodeError:
    logger.error("Invalid JSON in config.json")
    sys.exit(1)

CRYPTED_CREDENTIALS = bool(config.get("CRYPTED_CREDENTIALS", False))

def get_file_modification_time(file_path):
    try:
        mod_time = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mod_time)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None

def remove_items(INFO_PROGS, INFO_PROGS_LAST, PROGS_TO_RECORD):
    # Remove items already set to be recorded
    try:
        with open(INFO_PROGS, 'r') as f:
            source_data = json.load(f)
    except FileNotFoundError:
        logger.error(
        "No info_progs.json file. Need to check curl command or "
        "internet connection. Exit programme."
        )
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        logger.error(
        "JSONDecodeError in info_progs.json file. Need to check curl command or "
        "internet connection. Exit programme."
        )
        sys.exit(1)

    try:
        with open(INFO_PROGS_LAST, 'r') as f:
            items_to_remove = json.load(f)
    except FileNotFoundError:
        items_to_remove = []

    modified_data = [item for item in source_data if item not in items_to_remove]

    with open(PROGS_TO_RECORD, 'w') as f:
        json.dump(modified_data, f, indent=4)

INFO_PROGS = '/home/seluser/.local/share/select_freeboxos/info_progs.json'
INFO_PROGS_LAST = '/home/seluser/.local/share/select_freeboxos/info_progs_last.json'
PROGS_TO_RECORD = '/home/seluser/.local/share/select_freeboxos/progs_to_record.json'
API_URL = "https://www.media-select.fr/api/v1/progweek"

if not CRYPTED_CREDENTIALS:
    netrc_path = os.path.expanduser("/home/seluser/.netrc")
    if not os.path.exists(netrc_path):
        logger.error("No .netrc file. Exit program")
        sys.exit(1)

stat_result = run(
    ["stat", "-c", "%Y-%s", INFO_PROGS],
    capture_output=True,
    text=True,
    check=False
)
error_file = stat_result.stderr.strip()

if error_file == "":
     info_file = stat_result.stdout.strip().split("-")
     time_file = datetime.fromtimestamp(int(info_file[0]))
     time_diff = datetime.now() - time_file
     size_file = int(info_file[1])

info_progs_last_mod_time = get_file_modification_time(INFO_PROGS_LAST)

if info_progs_last_mod_time is None or info_progs_last_mod_time.date() < datetime.now().date():
    if error_file != "" or time_diff.total_seconds() > 1800 or size_file == 0:
        if CRYPTED_CREDENTIALS:
            try:
                username_mediaselect = os.getenv("USERNAME_MEDIASELECT")
                password_mediaselect = os.getenv("PASSWORD_MEDIASELECT")

                if username_mediaselect is None or password_mediaselect is None:
                    logger.error("Environment variables are empty.")
                    raise ValueError("Environment variables are empty.")

                response = requests.get(
                    API_URL,
                    auth=(username_mediaselect, password_mediaselect),
                    headers={"Accept": "application/json; indent=4"}
                )

                response.raise_for_status()

                with open(INFO_PROGS, "w") as f:
                    f.write(response.text)

                logger.info("Data downloaded with requests successfully.")

            except requests.RequestException as e:
                logger.error(f"API request failed: {e}")
            except ValueError as e:
                logger.error(f"Error: {e}")
        else:
            try:
                curl_result = run(
                    [
                        "curl",
                        "-H", "Accept: application/json;indent=4",
                        "-n",
                        API_URL,
                    ],
                    stdout=PIPE,
                    stderr=PIPE,
                    text=False,  # Keep as bytes
                    check=False
                )

                with open(INFO_PROGS, "wb") as json_file:
                    json_file.write(curl_result.stdout)

                logger.info("Data downloaded with curl successfully.")

            except Exception as e:
                logger.error(f"Error: {str(e)}\n")

        remove_items(INFO_PROGS, INFO_PROGS_LAST, PROGS_TO_RECORD)

        Popen(
            ["bash", "cron_freeboxos_app.sh"],
            cwd="/home/seluser/select-freeboxos",
            stdout=PIPE,
            stderr=PIPE
        )
