# Installation DOCKER

Utilisez Docker pour monter l'infrastructure complète :

```Bash
cd docker
docker compose -f docker-compose.yml up -d
```

Une fois les conteneurs actifs, l'application devrait maintenant être accessible sur http://localhost:xxxx.

Si vous pouvez tester que le clonage fonctionne dans le container 01-api-gateway : docker compose exec 01-api-gateway git clone https://git.pdplibre.org/Construction_PA/PA_Communautaire.git pl

# Lancement et test du serveur S3

On peut utiliser un serveur S3 local.

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
