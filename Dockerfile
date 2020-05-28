FROM docker:dind

COPY ["run.sh", "on-change.sh", "acme-cert-dump.py", "/"]

RUN apk add --update \
    bash \
    python3 \
    inotify-tools \
  && rm -rf /var/cache/apk/* \
  && mkdir /cert

CMD ["/run.sh"]

