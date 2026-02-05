FROM selenium/standalone-firefox:131.0-geckodriver-0.35-grid-4.25.0-20241024

LABEL org.opencontainers.image.title="select-freeboxos"
LABEL org.opencontainers.image.description="Automated Freebox OS interactions using Selenium."
LABEL org.opencontainers.image.licenses="AGPL-3.0"
LABEL org.opencontainers.image.source="https://github.com/mediaselect/select-freeboxos-docker"
LABEL org.opencontainers.image.authors="MEDIA-select <media.select.fr@gmail.com>"

USER root

RUN apt update && \
    apt upgrade -y && \
    apt install -yq virtualenv nano unattended-upgrades \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /home/seluser/select-freeboxos

ENV TZ="Europe/Paris"
ENV PATH="/home/seluser/.venv/bin:$PATH"

COPY requirements.txt .

RUN virtualenv -p python3 /home/seluser/.venv \
    && . /home/seluser/.venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /home/seluser/.local/share/select_freeboxos \
    && mkdir -p /home/seluser/.config/select_freeboxos \
    && mkdir -p /var/log/select_freeboxos \
    && chown -R seluser:seluser /home/seluser/.local/share/select_freeboxos \
    && chown -R seluser:seluser /home/seluser/.config/ \
    && chown -R seluser:seluser /var/log/select_freeboxos \
    && cp freeboxos_record /etc/logrotate.d/freeboxos_record \
    && ln -s /home/seluser/.config/select_freeboxos/.netrc /home/seluser/.netrc \
    && chown -R seluser:seluser /home/seluser/select-freeboxos

VOLUME [ "/home/seluser/.config/select_freeboxos", "/home/seluser/.local/share/select_freeboxos" ]

CMD ["/home/seluser/select-freeboxos/startup.sh"]
