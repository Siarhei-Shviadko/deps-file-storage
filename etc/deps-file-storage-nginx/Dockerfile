ARG REPOSITORY_URL=""
FROM ${REPOSITORY_URL:+$REPOSITORY_URL/base/}nginx:1.20.2

RUN echo "deb http://deb.debian.org/debian bullseye main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y openssl libxml2 && \
    apt-get autoremove -y

ARG config=./nginx.dev.conf
ARG USER=deps

COPY $config /etc/nginx/nginx.conf

RUN chgrp -R root /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /var/cache/nginx /var/run /var/log/nginx && \
    useradd -Ms /bin/bash $USER

USER $USER
