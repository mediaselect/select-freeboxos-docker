# 📺 select-freeboxos-docker v3.1.0

> 🐳 Run Freebox recording automation anywhere with Docker
> 🎯 Automatically schedule TV recordings via Freebox OS

![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)
![Architecture](https://img.shields.io/badge/Arch-ARM%20%7C%20x86%20(Docker)-orange)
![Status](https://img.shields.io/badge/Status-Active-success)
![Self-hosted](https://img.shields.io/badge/Self--Hosted-Yes-blueviolet)
![Dependency](https://img.shields.io/badge/Requires-Freebox%20OS-lightgrey)

---

## 🍿 How TV Select works

TV Select turns TV into a **personal discovery engine**.

You define what you care about:

* a documentary about wine 🍷
* a history episode 🏛️
* a space report 🚀
* that rare movie you couldn’t find anywhere 🎬
* a tennis documentary your son will love 🎾

Then the system works for you:

1. 🔍 Your searches are analyzed
2. 🧠 TV programs are continuously scanned
3. 🎯 When a match is found:

   * 📧 You receive a notification
   * 📼 A recording is triggered automatically

👉 No manual searching. No scheduling.

---

## 📖 TV Select Ecosystem

This project is part of the **TV Select ecosystem**.

👉 Overview & setup guide:

[![TV Select Ecosystem](https://img.shields.io/badge/TV%20Select-Ecosystem-blue)](https://github.com/tv-select)

## 📡 About select-freeboxos-docker

select-freeboxos-docker runs **select-freeboxos inside a Docker container**.

👉 It:

- connects to **Freebox OS**
- automatically **schedules recordings**
- lets the Freebox handle the recording

---

## ⚡ Key features

- 🐳 Docker-based (portable & isolated)
- 📡 Automatic recording scheduling via Freebox OS
- 💾 Record directly on Freebox internal or USB storage
- 🤖 Browser automation (Selenium)
- 🔄 Runs continuously via Docker container
- ⚙️ Fully automated once configured

---

## 🧩 How it works

Search → Match → Schedule (Freebox OS) → Record → Watch

---

## 🏠 Freebox OS integration

This application uses the **recording feature of Freebox OS**.

- Recordings are stored on the Freebox
- No local video storage required

---

## 🐳 Why Docker?

Use this version if you want:

- a **portable setup**
- no dependency conflicts
- the same behavior on Linux and Windows
- an isolated environment

💡 The container uses a lightweight Ubuntu system (~200MB RAM idle).

---

## 🔄 Runtime behavior

The Docker container runs continuously.

- Linux: container runs via Docker Engine
- Windows: container runs via Docker Desktop

👉 Important:

- Docker must start automatically with your system
- The container is configured with `--restart always`
- No manual execution is required after setup

💡 This ensures recordings are always scheduled without interruption.

---

## 📁 Data persistence

Configuration and data are stored on the host using mounted volumes:

- Linux:
  - ~/.config/media-free-docker
  - ~/.local/share/media-free-docker

- Windows:
  - %LOCALAPPDATA%\media-free-docker

---

## ⚡ Installation

### Requirements

- Docker (Engine on Linux / Desktop on Windows)
- Freebox OS (version ≥ 4.7)
- Account on https://www.media-select.fr

---

## 🐧 Linux setup

### Pull image

docker pull mediaselect/select-freeboxos:v3.1.0

---

### Create volumes

mkdir -p ~/.config/media-free-docker ~/.local/share/media-free-docker

sudo chown -R 1200:1201 ~/.local/share/media-free-docker ~/.config/media-free-docker

---

### Run container

docker run -d \
--mount type=bind,source=/home/$USER/.config/media-free-docker,target=/home/seluser/.config/select_freeboxos \
--mount type=bind,source=/home/$USER/.local/share/media-free-docker,target=/home/seluser/.local/share/select_freeboxos \
-e SE_START_VNC=false \
--restart always \
--shm-size="2g" \
--name freeboxos_select \
mediaselect/select-freeboxos:v3.1.0

---

## 🪟 Windows setup

### Run container

docker run -d `
--mount type=bind,source="$env:LOCALAPPDATA\media-free-docker\config",target="/home/seluser/.config/select_freeboxos" `
--mount type=bind,source="$env:LOCALAPPDATA\media-free-docker",target="/home/seluser/.local/share/select_freeboxos" `
-e SE_START_VNC=false `
--restart always `
--shm-size="2g" `
--name freeboxos_select `
mediaselect/select-freeboxos:v3.1.0

---

## ⚙️ Configuration

Enter the container:

docker exec -u seluser -it freeboxos_select bash

Run setup:

source /home/seluser/.venv/bin/activate && python3 install.py

Then:

- Enter your Freebox OS admin password
- Enter your MEDIA-select credentials

---

## 🔐 Security

This application interacts with **Freebox OS using your admin credentials**.

### 🟢 Local usage (recommended)

- Runs on a device within your home network
- Connects directly to your Freebox using local addresses (e.g. `192.168.1.254`, `mafreebox.freebox.fr`)
- HTTP is allowed only in this context

### 🟡 Remote usage (secure)

- Remote access is possible **only with HTTPS enabled**
- Connections over HTTP outside the local network are **blocked automatically**
- A warning is displayed when a remote connection is detected

### 🔴 Unsafe configurations

- Remote HTTP connections are **blocked by the application**
- This prevents exposure of your Freebox admin credentials

---

💡 By default, the application enforces security rules based on the network context.

## ⏳ What to expect

- ❌ No immediate results
- ⏳ Wait for matches
- 🎯 Recordings are scheduled automatically
- 📼 Videos are recorded by the Freebox

---

## 🤔 When should you use select-freeboxos-docker?

Use this version if:

- you want a portable setup (Linux / Windows)
- you prefer Docker over manual installation
- you want a continuously running system
- you want consistent behavior across environments

---

## ⚠️ Limitations

- Requires Docker
- Requires Freebox OS
- Docker must be running at system startup
- Relies on browser automation (Selenium)

---

💡 Note:
This container is designed to run continuously (not as a one-shot task),
to ensure scheduled recordings are never missed.

---

## ⭐ Support

If you like this project:

- ⭐ Star it
- 🔁 Share it
- 🧠 Use it

---

## ⚠️ Disclaimer

For personal use only.
