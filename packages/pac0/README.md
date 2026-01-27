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

Installation des sources, dépendances et lancement:

```shell
# lancement service 01-api-gateway
uvx pac0-cli@latest run 1
# lancement service 02-esb-central
uvx pac0-cli@latest run 2
# lancement service 03-controle-formats
uvx pac0-cli@latest run 3
# lancement service 04-validation-metier
uvx pac0-cli@latest run 4
# lancement service 05-conversion-formats
uvx pac0-cli@latest run 5
# lancement service 06-annuaire-local
uvx pac0-cli@latest run 6
# lancement service 07-routage
uvx pac0-cli@latest run 7
# lancement service 08-transmission-fiscale
uvx pac0-cli@latest run 8
# lancement service 09-gestion-cycle-vie
uvx pac0-cli@latest run 9
```

Lancement depuis un répertoire avec source et dépendances déjà installées:

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
uvx pac0-cli@latest setup tool nats-server
# or :
NATS_SERVER_VERSION=2.12.3
wget https://github.com/nats-io/nats-server/releases/download/v${NATS_SERVER_VERSION}/nats-server-v${NATS_SERVER_VERSION}-linux-amd64.tar.gz
tar xvf nats-server-v*-linux-amd64.tar.gz
mv nats-server-v*-linux-amd64/nats-server ~/.local/bin/
rm -Rf nats-server-v*-linux-amd64*

# install nats-cli
uvx pac0-cli@latest setup tool nats-cli
# or :
NATS_CLI_VERSION=0.3.0
wget https://github.com/nats-io/natscli/releases/download/v${NATS_CLI_VERSION}/nats-${NATS_CLI_VERSION}-linux-amd64.zip
unzip nats-*-linux-amd64.zip
mv nats-*-linux-amd64/nats ~/.local/bin/
rm -Rf nats-*-linux-amd64*

```

On peut installer plusieurs outils en une fois (utile dans les scripts):
```shell
❯ uvx pac0-cli@latest setup tool git nats-server nats-cli --summary
git>=2.43.0 ok (found 2.43.0)
nats-server>=2.12.3 ok (found 2.12.3)
nats-cli>=0.3.0 ok (found 0.3.0)
          installed pp tools
┏━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ tool        ┃ required ┃ installed ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ git         │ >=2.43.0 │    2.43.0 │
│ nats-server │ >=2.12.3 │    2.12.3 │
│ nats-cli    │  >=0.3.0 │     0.3.0 │
└─────────────┴──────────┴───────────┘
```