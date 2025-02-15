import logging
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException

from time import sleep

logging.basicConfig(
    filename="/var/log/select_freeboxos/select_freeboxos.log",
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("module_freeboxos")


FREEBOX_SERVER_IP = os.getenv("FREEBOX_SERVER_IP")
HTTPS = os.getenv("https")

if HTTPS == "true":
    https = True
else:
    https = False

freebox_os_password = os.getenv("freebox_os_password")

options = webdriver.FirefoxOptions()
options.add_argument("start-maximized")

try:
    driver = webdriver.Firefox(options=options)
except SessionNotCreatedException as e:
    logging.error("A SessionNotCreatedException occured. Exit programme.")
    print("A SessionNotCreatedException occured. Exit programme.")
    sys.exit(1)

#maximize the window size
driver.maximize_window()

try:
    if https:
        driver.get("https://" + FREEBOX_SERVER_IP + "/login.php")
    else:
        driver.get("http://" + FREEBOX_SERVER_IP + "/login.php")
except WebDriverException as e:
    if 'net::ERR_ADDRESS_UNREACHABLE' in e.msg:
        print("The programme cannot reach the address " + FREEBOX_SERVER_IP + " . Exit programme.")
        driver.quit()
        sys.exit(1)
    else:
        print("A WebDriverException occured. Exit programme.")
        driver.quit()
        sys.exit(1)

not_connected = True

sleep(4)
login = driver.find_element("id", "fbx-password")
sleep(1)
login.clear()
sleep(1)
login.click()
sleep(1)
login.send_keys(freebox_os_password)
sleep(1)
login.send_keys(Keys.RETURN)
sleep(6)


try:
    login = driver.find_element("id", "fbx-password")
except:
    not_connected = False
    sleep(2)
    driver.quit()


if not_connected:
    print("bad_password")
else:
    driver.quit()

    config_path = "/home/seluser/.config/select_freeboxos/config.py"

    with open(config_path, "r") as conf:
        lines = conf.readlines()

    with open(config_path, "w") as conf:
        for line in lines:
            if "HTTPS" in line:
                if https:
                    conf.write("HTTPS = True\n")
                else:
                    conf.write("HTTPS = False\n")
            else:
                conf.write(line)

    print("good_password")
