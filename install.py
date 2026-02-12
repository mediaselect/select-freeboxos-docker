import getpass
import json
import logging
import os
import shutil
import requests
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException

from time import sleep
from subprocess import Popen, PIPE, run

from module_freeboxos import get_website_title

logging.basicConfig(
    filename="/var/log/select_freeboxos/select_freeboxos.log",
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("module_freeboxos")

answers = ["oui", "non"]
opciones = ["1", "2", "3"]
opcion = 5
https = False

print("\nBienvenue dans le programme d'installation pour enregistrer "
      "automatiquement les vidéos qui vous correspondent dans votre "
      "Freebox.\nVous pouvez vous connecter à Freebox OS soit par internet, "
      "soit par votre réseau local. Par mesure de sécurité, le programme "
      "utilisera uniquement des connexions par HTTPS pour se connecter par "
      "internet. La connexion par le réseau local se fera en HTTP et n'est donc "
      "pas sécurisé. Ceci ne pose pas de problème si votre PC est fixe et "
      "qu'il reste toujours connecté à votre domicile dans votre réseau "
      "local. Dans le cas contraire, il est conseillé de configurer "
      "l'accès à distance à Freebox OS de manière sécurisée, avec un nom de domaine personnalisé: "
      "https://www.universfreebox.com/article/36003/Tuto-Accedez-a-Freebox-OS-a-distance-de-maniere-securisee-avec-un-nom-de-domaine-personnalise\n"
      "En plus de sécuriser votre connexion par HTTPS, ceci vous permettra de vous "
      "connecter en déplacement.\n"
      )

crypted = "no_se"
go_on = True

while crypted.lower() not in answers:
    crypted = input("\nVoulez vous chiffrer les identifiants de connection à "
                    "l'application web MEDIA-select.fr ainsi que le mot de passe "
                    "admin à Freebox OS? Si vous répondez oui, "
                    "il faudra penser à débloquer votre gestionnaire de mots de "
                    "passe (habituellement gnome-keyring sur les OS Debian/Ubuntu "
                    "ou Credential Manager sur Windows) s'il n'est pas paramétré "
                    "pour être débloqué automatiquement lors de l'ouverture de votre "
                    "session afin de permettre l'accès aux identifiants. Il faudra "
                    "également lancer le programme credentials_setup_linux.py "
                    "ou credentials_setup_windows.py machine hôte pour chiffrer "
                    "les identifiants.(répondre par oui ou non) : ").strip().lower()

if crypted.lower() == "non":
    while opcion not in opciones:
        opcion = input("Merci de choisir une des options suivantes:\n\n1) J'ai "
                    "configuré l'accès à Freebox OS hors de mon domicile et "
                    "je choisis de sécuriser ma connexion par HTTPS.\n\n2) Mon "
                    "PC restera toujours connecté au réseau local de ma "
                    "Freebox et je ne veux pas configurer l'accès à "
                    "à Freebox OS hors de mon domicile.\n\n3) Je "
                    "désire quitter le programme d'installation.\n\n"
                    "Choisissez entre 1 et 3: ")

    if opcion == "1":

        FREEBOX_SERVER_IP = input(
            "\nVeuillez saisir l'adresse à utiliser pour l'accès distant de "
            "votre Freebox.\nCelle-ci peut ressembler à "
            "https://votre-sous-domaine.freeboxos.fr:55412\n"
            "Veillez à choisir le port d'accès distant sécurisé (HTTPS et "
            "non HTTP) pour sécuriser la connexion: \n"
        )
        FREEBOX_SERVER_IP = FREEBOX_SERVER_IP.replace("https://", "")
        FREEBOX_SERVER_IP = FREEBOX_SERVER_IP.replace("http://", "")
        FREEBOX_SERVER_IP = FREEBOX_SERVER_IP.rstrip("/")
        cmd = ["curl", "-sI", "-w", "%{http_code}", "https://" + FREEBOX_SERVER_IP + "/login.php"]
        http = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        stdout, stderr = http.communicate()
        http_response = stdout.split()[-1]

        while http_response != "200":
            FREEBOX_SERVER_IP = input("\nLa connexion à la Freebox Server a "
                "échoué.\n\nMerci de saisir de nouveau l'adresse à utiliser pour "
                "l'accès distant de votre Freebox.\nCelle-ci peut ressembler à "
                "https://votre-sous-domaine.freeboxos.fr:55412\n"
                "Veillez à choisir le port d'accès distant sécurisé (HTTPS et "
                "non HTTP) pour sécuriser la connexion: \n")
            FREEBOX_SERVER_IP = FREEBOX_SERVER_IP.replace("https://", "")
            FREEBOX_SERVER_IP = FREEBOX_SERVER_IP.replace("http://", "")
            FREEBOX_SERVER_IP = FREEBOX_SERVER_IP.rstrip("/")
            cmd = ["curl", "-sI", "-w", "%{http_code}", "https://" + FREEBOX_SERVER_IP + "/login.php"]
            http = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            stdout, stderr = http.communicate()
            http_response = stdout.split()[-1]

    elif opcion == "2":
        print("\nVous avez choisi de vous connecter à votre Freebox par votre "
            "réseau local.")

        FREEBOX_SERVER_IP = "192.168.1.254"

        url = "http://" + FREEBOX_SERVER_IP
        title = get_website_title(url)

        option = 5
        repeat = False
        out_prog = "nose"

        while title != "Freebox OS":
            print("\nLa connexion à la Freebox Server a échoué.\n\nMerci de vérifier "
                    "que vous êtes bien connecté au réseau local de votre Freebox "
                    "(cable ethernet ou wifi).")
            if repeat:
                print("\nLe programme a détecté une nouvelle fois que le routeur "
                    "est différent de celui de la Freebox server.\n")
            if title is not None:
                print("\nLe programme a détecté comme nom possible de votre "
                    f"routeur la valeur suivante: {title}\n")
            else:
                print("\nLe programme n'a pas détecté le nom de votre routeur.\n")
            if repeat:
                while out_prog.lower() not in answers:
                    out_prog = input("Voulez-vous continuer de tenter de vous "
                                    "connecter? (repondre par oui ou non): ")
            if out_prog.lower() == "non":
                print('Sortie du programme.\n')
                sys.exit()

            print("Merci de vérifier que vous êtes bien connecté au réseau local "
                "de votre Freebox serveur. \n")
            while option not in opciones:
                option = input(
                    "Après avoir vérifié la connexion, vous pouvez choisir une "
                    "de ces 3 options pour continuer:\n\n1) Vous n'étiez pas "
                    "connecté au réseau local de votre Freebox serveur "
                    "précédemment et vous voulez tenter de nouveau de vous "
                    "connecter\n\n2) Vous êtiez sûr d'être connecté au réseau "
                    "local de votre Freebox serveur. Vous avez vérifié l'adresse "
                    "ip de la Freebox server dans la fenêtre 'Paramètres de la "
                    "Freebox' après avoir clické sur 'Mode réseau' et celle-ci "
                    "est différente de 192.168.1.254.\n\n3) "
                    "Vous voulez utiliser le nom d'hôte mafreebox.freebox.fr qui "
                    "fonctionnera sans avoir besoin de vérifier l'adresse IP de "
                    "la freebox server. Il faudra cependant veiller à ne pas "
                    "utiliser de VPN avec votre PC/Mac pour pouvoir vous "
                    "connecter.\n\nChoisissez entre 1 et 3: "
                )
            if option == "1":
                cmd = ["ip", "route", "show", "default"]
                ip_ad = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
                stdout, stderr = ip_ad.communicate()
                FREEBOX_SERVER_IP = stdout.split()[2]

                print("\nLe programme a détecté que votre routeur "
                    f"a l'adresse ip {FREEBOX_SERVER_IP}\n\nLe programme va "
                    "maitenant vérifier si celui-ci est celui de la Freebox server\n")
            elif option == "2":
                FREEBOX_SERVER_IP = input(
                    "\nVeuillez saisir l'adresse IP de votre Freebox: "
                )
            else:
                FREEBOX_SERVER_IP = "mafreebox.freebox.fr"

            option = "5"

            print("\nNouvelle tentative de connexion à la Freebox:\n\nVeuillez patienter.")
            print("\n---------------------------------------------------------------\n")

            url = "http://" + FREEBOX_SERVER_IP
            title = get_website_title(url)

            repeat = True
            out_prog = "nose"

    else:
        print("Merci d'avoir utilisé le programme d'installation pour enregistrer "
            "automatiquement les vidéos qui vous correspondent dans votre "
            "Freebox.\n\nAu revoir!")
        sys.exit()

    if opcion == "1":
        https = True

    print("Le programme peut atteindre la page de login de Freebox OS. Il "
        "va maintenant tenter de se connecter à Freebox OS avec votre "
        " mot de passe:")

    options = webdriver.FirefoxOptions()
    options.add_argument("start-maximized")

    try:
        driver = webdriver.Firefox(options=options)
    except SessionNotCreatedException as e:
        print("A SessionNotCreatedException occured. Exit programme.")
        logging.error(
            "A SessionNotCreatedException occured. Exit programme."
        )
        sys.exit(1)

    #maximize the window size
    driver.maximize_window()

    try:
        if https:
            driver.get(f"https://{FREEBOX_SERVER_IP}/login.php")
        else:
            driver.get(f"http://{FREEBOX_SERVER_IP}/login.php")
    except WebDriverException as e:
        if 'net::ERR_ADDRESS_UNREACHABLE' in e.msg:
            print(f"The programme cannot reach the address {FREEBOX_SERVER_IP} . Exit programme.")
            logging.error(
                f"The programme cannot reach the address {FREEBOX_SERVER_IP} . Exit programme."
            )
            driver.quit()
            sys.exit(1)
        else:
            print("A WebDriverException occured. Exit programme.")
            logging.error(
                "A WebDriverException occured. Exit programme."
            )
            driver.quit()
            sys.exit(1)

    not_connected = True
    answer_hide = "maybe"
    n = 0

    while not_connected:
        if answer_hide.lower() == "oui":
            freebox_os_password = input(
                "\nVeuillez saisir votre mot de passe admin de la Freebox: "
            )
        else:
            freebox_os_password = getpass.getpass(
                "\nVeuillez saisir votre mot de passe admin de la Freebox: "
            )
        print(
            "\nVeuillez patienter pendant la tentative de connexion à "
            "Freebox OS avec votre mot de passe.\n"
        )
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
            n += 1
            if n > 6:
                print(
                    "\nImpossible de se connecter à Freebox OS avec ce mot de passe. "
                    "Veuillez vérifier votre mot de passe de connexion admin en vous "
                    "connectant à l'adresse http://mafreebox.freebox.fr/login.php puis "
                    "relancez le programme install.py. "
                )
                driver.quit()
                go_on = False
                break
            try_again = input(
                "\nLe programme install.py n'a pas pu se connecter à Freebox OS car "
                "le mot de passe ne correspond pas à celui enregistré dans "
                "la Freebox.\nVoulez-vous essayer de nouveau?(oui ou non): "
            )
            if try_again.lower() == "oui":
                if answer_hide.lower() != "oui":
                    while answer_hide.lower() not in answers:
                        answer_hide = input(
                            "\nVoulez-vous afficher le mot de passe que vous saisissez "
                            "pour que cela soit plus facile? (répondre par oui ou non): "
                        )
            else:
                driver.quit()
                go_on = False
                break
        except:
            print("Le mot de passe correspond bien à votre compte admin Freebox OS")
            not_connected = False
            sleep(2)
            driver.quit()

max_sim_recordings = 0
title_answer = "no_se"
change_max_rec = "no_se"
record_logs = "no_se"
auto_update = "no_se"

if go_on:
    while title_answer.lower() not in answers:
        title_answer = input(
            "\nVoulez-vous utiliser le nommage de TV-select "
            "pour nommer les titres des programmes? Si vous répondez oui, alors "
            "les titres seront composés du titre du programme, de son numéro "
            "d'idendification dans MEDIA-select puis de la recherche "
            "correspondante. Si vous répondez non, le nommage de Freebox OS "
            "sera utilisé (dans ce cas des erreurs peuvent apparaitre si la "
            "différence de temps (marge avant le début du film) est trop "
            "grande): "
        )
    print("\n\nLe nombre maximum de flux simultanés autorisé par Free est "
          "limité à 2 selon l'assistance de Free:\n"
          "https://assistance.free.fr/articles/gerer-et-visionner-mes-enregistrements-72\n"
          "Cependant, cette limite semble venir du faible débit de l'ADSL et il "
          "est possible d'enregistrer un plus grand nombre de vidéos "
          "simultanément si vous avez la fibre optique.\n")
    while change_max_rec.lower() not in answers:
        change_max_rec = input("Voulez-vous augmenter le nombre maximum "
                        "d'enregistrements simultanés autorisés par "
                        "le programme? (répondre par oui ou non): ")

    if change_max_rec.lower() == "oui":
        while max_sim_recordings <= 0:
            max_sim_recordings = input(
                "\nVeuillez saisir le nombre de vidéos simultanément enregistrées "
                "autorisé par le programme: "
            )
            try:
                max_sim_recordings = int(max_sim_recordings)
            except ValueError:
                max_sim_recordings = 0
                print(
                    "\nVeuillez saisir un nombre entier supérieur à 0 pour le "
                    "nombre de vidéos simultanément enregistrées par le "
                    "programme."
                )
    else:
        max_sim_recordings = 2

    while record_logs.lower() not in answers:
        record_logs = input(
            "\n\nAutorisez-vous l'application à collecter et envoyer des journaux "
            "d'erreurs anonymisés pour améliorer les performances et corriger les "
            "bugs? (répondre par oui ou non) : ").strip().lower()

    while auto_update.lower() not in answers:
        auto_update = input(
            "\n\nAutorisez-vous l'application à se mettre à jour automatiquement? "
            "Si vous répondez 'non', vous devrez mettre à jour l'application par "
            "vous-même. (répondre par oui ou non) : ").strip().lower()

    cron_docker_conf_path = "/home/seluser/.config/select_freeboxos/cron_docker.conf"
    template_cron_docker_path = "/home/seluser/select-freeboxos/cron_docker_template.conf"

    if not os.path.exists(cron_docker_conf_path):
        shutil.copy(template_cron_docker_path, cron_docker_conf_path)
        os.chmod(cron_docker_conf_path, 0o640)

    cron_params = ["START_FREEBOXOS",
                   "AUTO_UPDATE",
                   ]

    with open("/home/seluser/.config/select_freeboxos"
              "/cron_docker.conf", "w", encoding='utf-8') as conf:
        for param in cron_params:
            if "START_FREEBOXOS" in param:
                if crypted.lower() == "oui":
                    conf.write("START_FREEBOXOS=false\n")
                else:
                    conf.write("START_FREEBOXOS=true\n")
            elif "AUTO_UPDATE" in param:
                if auto_update.lower() == "oui":
                    conf.write("AUTO_UPDATE=true\n")
                else:
                    conf.write("AUTO_UPDATE=false\n")
            else:
                conf.write(param + "\n")

    config = {}

    config["CRYPTED_CREDENTIALS"] = crypted.lower() == "oui"

    if config["CRYPTED_CREDENTIALS"]:
        config["ADMIN_PASSWORD"] = "XXXXXXX"
        config["FREEBOX_SERVER_IP"] = "XXXXXXX"
    else:
        config["ADMIN_PASSWORD"] = freebox_os_password
        config["FREEBOX_SERVER_IP"] = FREEBOX_SERVER_IP

    config["MEDIA_SELECT_TITLES"] = title_answer.lower() == "oui"
    config["MAX_SIM_RECORDINGS"] = int(max_sim_recordings)
    config["HTTPS"] = bool(https)
    config["SENTRY_MONITORING_SDK"] = record_logs.lower() == "oui"

    config_path = "/home/seluser/.config/select_freeboxos/config.json"

    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    os.chmod(config_path, 0o600)

conf_dir = os.path.expanduser("/home/seluser/.config/select_freeboxos")
netrc_file = os.path.join(conf_dir, ".netrc")

if not os.path.exists(netrc_file):
    with open(netrc_file, 'a', encoding='utf-8'):
        os.utime(netrc_file, None)

    os.chmod(netrc_file, 0o600)


if crypted.lower() == "non":
    print("\nConfiguration de la connexion à MEDIA-select.fr:\n")

    response = requests.head("https://media-select.fr", timeout=5)
    http_response = response.status_code

    if http_response != 200:
        print(
            "\nLa box MEDIA-select n'est pas connectée à internet. Veuillez "
            "vérifier votre connection internet et relancer le programme "
            "d'installation.\n\n"
        )
        go_on = False

    if go_on:
        username = input(
            "Veuillez saisir votre identifiant de connexion (adresse "
            "email) sur MEDIA-select.fr: "
        )
        password_mediarecord = getpass.getpass(
            "Veuillez saisir votre mot de passe sur MEDIA-select.fr: "
        )

        authprog_response = "403"

        with open("/home/seluser/.config/select_freeboxos"
                  "/.netrc", "r", encoding='utf-8') as file:
            lines_origin = file.read().splitlines()

        while authprog_response != "200":
            with open("/home/seluser/.config/select_freeboxos"
                      "/.netrc", "r", encoding='utf-8') as file:
                lines = file.read().splitlines()

            try:
                position = lines.index("machine www.media-select.fr")
                lines[position + 1] = "  login {username}".format(username=username)
                lines[position + 2] = "  password {password_mediarecord}".format(
                    password_mediarecord=password_mediarecord
                )
            except ValueError:
                lines.append("machine www.media-select.fr")
                lines.append("  login {username}".format(username=username))
                lines.append(
                    "  password {password_mediarecord}".format(
                        password_mediarecord=password_mediarecord
                    )
                )

            with open("/home/seluser/.config/select_freeboxos"
                      "/.netrc", "w", encoding='utf-8') as file:
                for line in lines:
                    file.write(line + "\n")

            cmd = ['curl', '-iSn', 'https://www.media-select.fr/api/v1/progweek']
            authprog = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            authprog_response = authprog.stdout.split('\n')[0].split(' ')[1]

            if authprog_response != "200":
                try_again = input(
                    "Le couple identifiant de connexion et mot de passe "
                    "est incorrect.\nVoulez-vous essayer de nouveau?(oui ou non): "
                )
                answer_hide = "maybe"
                if try_again.lower() == "oui":
                    username = input(
                        "Veuillez saisir de nouveau votre identifiant de connexion (adresse email) sur MEDIA-select.fr: "
                    )
                    while answer_hide.lower() not in answers:
                        answer_hide = input(
                            "Voulez-vous afficher le mot de passe que vous saisissez "
                            "pour que cela soit plus facile? (répondre par oui ou non): "
                        )
                    if answer_hide.lower() == "oui":
                        password_mediarecord = input(
                            "Veuillez saisir de nouveau votre mot de passe sur MEDIA-select.fr: "
                        )
                    else:
                        password_mediarecord = getpass.getpass(
                            "Veuillez saisir de nouveau votre mot de passe sur MEDIA-select.fr: "
                        )
                else:
                    go_on = False
                    with open("/home/seluser/.config/select_freeboxos"
                              "/.netrc", "w", encoding='utf-8') as file:
                        for line in lines_origin:
                            file.write(line + "\n")
                    break
        print("\nLe programme est maintenant prêt pour paramétrer les enregistrements.\n")
else:
    with open("/home/seluser/.config/select_freeboxos"
              "/.netrc", "r", encoding='utf-8') as file:
        lines = file.read().splitlines()

    try:
        position = lines.index("machine www.media-select.fr")
        lines[position + 1] = "  login XXXXXXXX"
        lines[position + 2] = "  password XXXXXXXX"
    except ValueError:
        lines.append("machine www.media-select.fr")
        lines.append("  login XXXXXXXX")
        lines.append("  password XXXXXXXX")

    with open("/home/seluser/.config/select_freeboxos"
              "/.netrc", "w", encoding='utf-8') as file:
        for line in lines:
            file.write(line + "\n")
    print("\nLe paramétrage du programme a été réalisé. Vous pouvez maintenant sortir "
          "du conteneur Docker pour lancer le programme credentials_setup_linux.py "
          "ou credentials_setup_windows.py depuis la machine hôte afin de "
          "chiffrer les identifiants de connexion à MEDIA-select.fr et Freebox OS.")
