#!/usr/bin/env python

##############################################
# extract cert from traefik 1.7
##############################################

import argparse
import base64
import json
import os
import shlex
import subprocess
import sys

certificates_key = 'Certificates'

def main(raw_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Grab a certificate out of Traefik's acme.json file")
    parser.add_argument('acme_json', help='path to the acme.json file')
    parser.add_argument('domain', help='domain to get certificate for')
    parser.add_argument('dest_dir',
                        help='path to the directory to store the certificate')
    parser.add_argument(
        '--post-update', required=False,
        help='command to run after updating the certificate')

    args = parser.parse_args(raw_args)

    dest_dir = os.path.abspath(os.path.expanduser(args.dest_dir))
    if not os.path.exists(dest_dir) or not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)

    new_privkey, new_fullchain = read_domain_certs(args.acme_json, args.domain)
    start = new_fullchain.find(b'-----BEGIN CERTIFICATE-----', 1)
    new_cert = new_fullchain[0:start]
    new_chain = new_fullchain[start:]

    old_privkey = read_cert(args.dest_dir, 'privkey.pem')
    old_fullchain = read_cert(args.dest_dir, 'fullchain.pem')
    old_cert = read_cert(args.dest_dir, 'cert.pem')
    old_chain = read_cert(args.dest_dir, 'chain.pem');

    if new_privkey != old_privkey or new_fullchain != old_fullchain or new_cert != old_cert or new_chain != old_chain:
        print('Certificates changed! Writing new files...')
        write_cert(args.dest_dir, 'privkey.pem', new_privkey)
        write_cert(args.dest_dir, 'fullchain.pem', new_fullchain)
        write_cert(args.dest_dir, 'cert.pem', new_cert);
        write_cert(args.dest_dir, 'chain.pem', new_chain);

        if args.post_update is not None:
            print('Running post update command "%s"' % (args.post_update,))
            post_update(args.post_update)
    else:
        print('Certificates unchanged. Skipping...')

    print('Done')


def read_cert(storage_dir, filename):
    cert_path = os.path.join(storage_dir, filename)
    if os.path.exists(cert_path):
        with open(cert_path, 'rb') as cert_file:
            return cert_file.read()
    return None


def write_cert(storage_dir, filename, cert_content):
    cert_path = os.path.join(storage_dir, filename)
    with open(cert_path, 'wb') as cert_file:
        cert_file.write(cert_content)
    os.chmod(cert_path, 0o600)


def read_domain_certs(acme_json_path, domain):
    with open(acme_json_path) as acme_json_file:
        acme_json = json.load(acme_json_file)

    domain_certs = None

    for provider in acme_json:
        if provider in acme_json:
            provider = acme_json[provider]

            if certificates_key in provider:
                certs_json = provider[certificates_key]
                domain_certs = [cert for cert in certs_json
                                if cert['domain']['main'] == domain]

                if domain_certs is not None:
                    break

    if domain_certs is None:
        raise RuntimeError(
            'Unable to find certificate for domain "%s"' % (domain,))
    elif len(domain_certs) > 1:
        raise RuntimeError(
            'More than one (%d) certificates for domain "%s"' % (domain,))

    [domain_cert] = domain_certs
    return (base64.b64decode(domain_cert['key']),
            base64.b64decode(domain_cert['certificate']))


def post_update(command):
    subprocess.check_call(shlex.split(command))


if __name__ == '__main__':
    main()
