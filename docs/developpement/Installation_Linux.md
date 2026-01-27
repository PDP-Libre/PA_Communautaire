# Installation sous Linux

Testé sur Ubuntu 24.04

Nous allons installer les composants un par un. 

Après avoir cloné le projet en local et s'être placé dans le dossier **PA_Communautaire**.


## Installation des dépendances PYTHON avec UV

Au lieu d'utiliser l'ancien gestionnaire de package PIP, on a préféré utiliser uv qui est plus rapide et plus complet. 

Sous ubuntu, préférer utiliser l'installation manuelle plutôt que la version SNAP.

La doc: [astral-sh/uv](https://github.com/astral-sh/uv)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
cd packages/pac-bdd
# on installe les packages définis dans pyproject.toml
uv sync

cd ../pac0
uv sync
```

## Installation du broker de message NATS
NATS est un service optimisé pour recevoir, stocker et distribuer une grande quantité de message. Il est écrit en GO, facile a installer et performant. 

La doc: https://github.com/nats-io/nats-server

```bash
wget https://github.com/nats-io/nats-server/releases/download/v2.12.3/nats-server-v2.12.3-linux-amd64.tar.gz
tar -xzf nats-server-v2.12.3-linux-amd64.tar.gz
# important de mettre le binaire dans un dossier accessible dans le PATH
cd nats-server-v2.12.3-linux-amd64
cp nats-server ~/.local/bin/nats-server
chmod +x ~/.local/bin/nats-server
```

On peut aussi installer le client NATS pour voir ce qu'il se passe: 

```bash
NATS_CLI_VERSION=0.3.0
wget https://github.com/nats-io/natscli/releases/download/v${NATS_CLI_VERSION}/nats-${NATS_CLI_VERSION}-linux-amd64.zip
unzip nats-${NATS_CLI_VERSION}-linux-amd64.zip 
cd nats-${NATS_CLI_VERSION}-linux-amd64/
cp nats ~/.local/bin/nats
chmod +x ~/.local/bin/nats
````

Testons que nats accepte des messages : 

* dans un premier terminal, lancer le serveur:  
  ```bash
  nats-server  
  ```
* dans un second terminal, regardons ce qu'il se passe:  
  ```bash
  nats subscribe demo
  ```
* dans un troisème terminal, essayons d'envoyer des messages: 
  ```bash
  nats publish demo "Hello world"
  ```

Dans le second terminal on doit avoir : 
```
15:09:08 Subscribing on demo 
[#1] Received on "demo"
Hello world
```

NATS est maintenant en place. On peut arrêter le serveur avec CTRL+C, il sera lancé automatiquement plus tard. 

## Serveur d'API fastAPI

Après s'être placé dans le dossier **PA_Communautaire**.

```bash
cd packages/pac0
uv run fastapi dev src/pac0/service/api_gateway/main.py
```

L'application devrait maintenant être accessible sur http://localhost:8080/docs
