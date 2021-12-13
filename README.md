## traefik-default-cert

Docker Hub: [cgoit/traefik-default-cert](https://hub.docker.com/r/cgoit/traefik-default-cert/)

alternativly  
weekly auto-build (Gitlab online) for newest patches  
[hasechris-docker-images/traefik-default-cert](https://gitlab.com/hasechris-docker-images/traefik-default-cert)  
[![pipeline status](https://gitlab.com/hasechris-docker-images/traefik-default-cert/badges/master/pipeline.svg)](https://gitlab.com/hasechris-docker-images/traefik-default-cert/-/commits/master)


compose-diff for weekly auto-built:  
{- image: cgoit/traefik-default-cert -}  
{+ image: registry.gitlab.com/hasechris-docker-images/traefik-default-cert:latest +}  


Set default traefik 2 certificate.

Extracts a specific certificate from acme.json and restart traefik container on changed cert. Can be used to setup a default cert for traefik, so that non SNI clients like IE8 work correctly.

This is a fork of [ziezo/traefik-default-cert](https://github.com/ziezo/traefik-default-cert)

### Setup

- edit traefik.[toml|yml]
- edit dynamic configuration
- touch acme.json
- edit docker-compose.yml
- docker-compose up -d

### static configuration example (e.g. traefik.toml)

```toml
[entryPoints]
  [entryPoints.web]
    address = ":80"

  [entryPoints.websecure]
    address = ":443"  
    [entryPoints.websecure.http.tls]
      certResolver = "leresolver"
      [[entryPoints.websecure.http.tls.domains]]
        main = "default.tld"
        sans = ["sub1.default.tld", "sub2.default.tld"]
...
#enable letsencrypt  
[certificatesResolvers.leresolver.acme]
  email = "your-email@example.com"
  storage = "acme.json"
  [certificatesResolvers.leresolver.acme.httpChallenge]
    # used during the challenge
    entryPoint = "web"
```

### dynamic configuration example
```toml
[tls.stores]
  [tls.stores.default]
    [tls.stores.default.defaultCertificate]
      certFile = "/default-cert/fullchain.pem"
      keyFile  = "/default-cert/privkey.pem"
```

### docker-compose example

```yaml
version: "3.7"  
services:  
  
###################################################################################  
# traefik-default-cert  
###################################################################################  
  traefik-default-cert:
    container_name: traefik-default-cert
    image: cgoit/traefik-default-cert
    volumes:
        # enable execution of docker inside container
        - /var/run/docker.sock:/var/run/docker.sock
        # folder with LE json - also see env variable WATCH_FILE
        - ./letsencrypt:/letsencrypt:ro
        # traefik target for extracted cert
        - ./traefik/vol/cert:/traefik
    environment:
        # the file to be watched for changes
        - "WATCH_FILE=/letsencrypt/acme.json"
        # domain to extract (MAIN domain, not SAN domain)
        - "CERT_DOMAIN=default.tld"
        # where to copy the cert files (separated by :)
        - "COPY_FULLCHAIN=/traefik/fullchain.pem"
        - "COPY_PRIVKEY=/traefik/privkey.pem"
        - "COPY_CHAIN="
        - "COPY_CERT="
        # containers to restart
        - "RESTART=traefik"
    depends_on:
    - traefik
    restart: always
  
  
###################################################################################  
# traefik  
###################################################################################  
  traefik:  
    container_name: traefik  
    image: traefik:v2.2 
    ports:  
        - "80:80"  
        - "443:443"
    volumes:
        - ./traefik/vol/cert:/default-cert:ro
        ...
    restart: always
    ...
```
