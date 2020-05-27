## traefik-default-cert

Docker Hub: [cgoit/traefik-default-cert](https://hub.docker.com/r/cgoit/traefik-default-cert/)

Set default traefik 2 certificate.

Extracts a specific certificate from acme.json and restart traefik container on changed cert. Can be used to setup a default cert for traefik, so that non SNI clients like IE8 work correctly.

This is a fork of [ziezo/traefik-default-cert](https://github.com/ziezo/traefik-default-cert)

### Setup

- edit traefik.[toml|yml]
- touch acme.json
- edit docker-compose.yml
- docker-compose up -d

### traefik.toml example

```toml
[entryPoints]
  [entryPoints.web]
    address = ":80"

  [entryPoints.websecure]
    address = ":443"  
    [entryPoints.https.tls]  
      #define default cert to use when no SNI match is found  
      [[entryPoints.https.tls.certificates]]  
      certFile = "/cert/fullchain.pem"  
      keyFile = "/cert/privkey.pem"  
...
#configure router with default domain name
[http.routers]
  [http.routers.my-router]
    rule = "Host(`default.tld`)"
    [http.routers.my-router.tls]
      certResolver = "myresolver" # From static configuration
      [[http.routers.my-router.tls.domains]]
        main = "default.tld"
        sans = ["second.tld"]
...  
#configure default certificate
[tls.stores]
  [tls.stores.default]
    [tls.stores.default.defaultCertificate]
      certFile = "/cert/fullchain.pem"
      keyFile  = "/cert/privkey.pem"
...
#enable letsencrypt  
[certificatesResolvers.myresolver.acme]
  email = "your-email@example.com"
  storage = "acme.json"
  [certificatesResolvers.myresolver.acme.httpChallenge]
    # used during the challenge
    entryPoint = "web"
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
        #enable execution of docker inside container  
        - /var/run/docker.sock:/var/run/docker.sock  
        #acme.json  
        - ./traefik/vol/acme.json:/acme.json:ro  
        #treafik target for extracted cert 
        - ./traefik/vol/cert:/traefik
    environment:
        #domain to extract (MAIN domain, not SAN domain)  
        - "CERT_DOMAIN=default.tld"  
        #where to copy the cert files (separated by :)  
        - "COPY_FULLCHAIN=/traefik/fullchain.pem"
        - "COPY_PRIVKEY=/traefik/privkey.pem"
        - "COPY_CHAIN="
        - "COPY_CERT="  
        #containers to restart
        - "RESTART=traefik"
        #cron time to run cert extract  
        - "CRON_TIME=0 1 * * *"  
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
    restart: always
    ...
```
