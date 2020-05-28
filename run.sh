#!/bin/bash
[ -z "${CERT_DOMAIN}" ] && { echo "=> CERT_DOMAIN cannot be empty" && exit 1; }
[ -z "${WATCH_FILE}" ] && { echo "=> WATCH_FILE cannot be empty" && exit 1; }

function oc() {
  inotifywait -m -q -e close_write,moved_to,create --format "%e %w%f" "${WATCH_FILE}" | while read -r events filename; do
    if [ "${filename}" == "${WATCH_FILE}" ]; then
      $1
    fi
  done
}

function startup() {
  if [[ ! -f "${WATCH_FILE}" ]]; then
    echo "=> Waiting for file ${WATCH_FILE}"

    ( inotifywait -m -q -e create,open,moved_to --format '%w%f' "$(dirname "${WATCH_FILE}")" & echo $! >&3 ) 3>pid | \
      while read i; do
        [ "$i" = "${WATCH_FILE}" ] && break
      done
    kill $(<pid)
  fi
}

startup

echo "=> Running inotifywait on file ${WATCH_FILE}"

# run once on startup to ensure that the certificates are stored
./acme-cert-dump.py --post-update /on-change.sh ${WATCH_FILE} ${CERT_DOMAIN} /cert

# watch for changes
oc "./acme-cert-dump.py --post-update /on-change.sh ${WATCH_FILE} ${CERT_DOMAIN} /cert"