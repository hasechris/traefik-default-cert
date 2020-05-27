FROM docker:dind

COPY ["run.sh", "cron.sh", "on-change.sh", "acme-cert-dump.py", "/"]

RUN apk add --update \
    bash \
    python3 \
  && rm -rf /var/cache/apk/* \
  && mkdir /cert

ENV CRON_TIME="0 1 * * *"

CMD ["/run.sh"]

