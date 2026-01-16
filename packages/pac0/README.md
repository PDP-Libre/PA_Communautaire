# pac0

```
________________________________ 
__________________ ________  __ \
_______  __ \  __ `/  ___/  / / /
______  /_/ / /_/ // /__ / /_/ / 
_____  .___/\__,_/ \___/ \____/  
____/_/                          

  🇫🇷 🇪🇺 facturation électronique
 plateforme agréée communautaire
________________________________ 
```

Une implémentation de référence des specifications de PA Commmunautaire.


## lancement

```shell
cd packages/pac0
# lancement service 01-api-gateway
uv run fastapi dev src/pac0/service/api_gateway/main.py
# lancement service 02-esb-central
nats-server -V -js
# lancement service 03-controle-formats
uv run faststream run src/pac0/service/controle-formats/main:app
# lancement service 04-validation-metier
uv run faststream run src/pac0/service/validation_metier/main:app
# lancement service 05-conversion-formats
uv run faststream run src/pac0/service/conversion-formats/main:app
# lancement service 06-annuaire-local
uv run faststream run src/pac0/service/annuaire-local/main:app
# lancement service 07-routage
uv run faststream run src/pac0/service/routage/main:app
# lancement service 08-transmission-fiscale
uv run faststream run src/pac0/service/transmission-fiscale/main:app
# lancement service 09-gestion-cycle-vie
uv run faststream run src/pac0/service/gestion_cycle_vie/main:app
```

## tests

```
uv run pytest
```

## dépendances

* a light ESB: NATS: https://github.com/nats-io/nats-server/releases/download/v2.12.3/nats-server-v2.12.3-linux-amd64.tar.gz
* a light S3 storage: seeweedfs


```shell
# install nats-server
NATS_SERVER_VERSION=2.12.3
wget https://github.com/nats-io/nats-server/releases/download/v${NATS_SERVER_VERSION}/nats-server-v${NATS_SERVER_VERSION}-linux-amd64.tar.gz
tar xvf nats-server-v*-linux-amd64.tar.gz
mv nats-server-v*-linux-amd64/nats-server ~/.local/bin/
rm -Rf nats-server-v*-linux-amd64*

# install nats-cli
NATS_CLI_VERSION=0.3.0
wget https://github.com/nats-io/natscli/releases/download/v${NATS_CLI_VERSION}/nats-${NATS_CLI_VERSION}-linux-amd64.zip
unzip nats-*-linux-amd64.zip
mv nats-*-linux-amd64/nats ~/.local/bin/
rm -Rf nats-*-linux-amd64*
```