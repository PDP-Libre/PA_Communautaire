# Installation DOCKER
## Pré-requis

* Avoir lu la documentation sur [documentation sur l'architecture](Architecture.md)
* Avoir docker sur sa machine.  
  Vous pouvez utiliser docker ou podman. 

> [!WARNING]
> Attention sous Ubuntu 24.04: les paquets APT sont trop anciens.  
> Préférez `snap install docker` ou la version depuis les dépots Docker.

## Activation du projet

Docker va monter l'infrastructure complète avec chacun des services du projet:

```Bash
cd docker
sudo docker compose up -d
# ou avec podman
sudo podman compose -f docker-compose.yml up -d
```

Une fois les conteneurs actifs, l'application devrait maintenant être accessible sur http://localhost:8000/docs.

Vous pouvez [lancer les tests](BDD_Guide_Developpeur.md) et commencer à developper.

# Vérifications

## Vérification du lancement

```
docker compose ps
```

Aller sur http://localhost:8000/docs pour découvrir FastApi



## git clone automatique
Le container Docker va cloner le repository à chaque lancement pour avoir la dernière version du projet. 

Si vous voulez tester que le clonage fonctionne par exemple dans le container 01-api-gateway : 

```
docker compose exec 01-api-gateway git clone https://git.pdplibre.org/Construction_PA/PA_Communautaire.git pl
```

## Lancement et test du serveur S3

S3 est un serveur de fichier qui va stocker les factures. On peut utiliser une version dans le cloud ou utiliser sa propre instance en local.

Pour utiliser le serveur S3 local.

* lancement du serveur S3 local
  ```
  cd ????
  docker compose up
  docker compose logs -f
  ```
* test du fonctionnement du serveur S3 local 
  ```
  cd packages/pac0
  uv sync
  uv run pytest tests/test_s3fs.py
  ```
* les fichiers sont visible dans le dossier xxx
