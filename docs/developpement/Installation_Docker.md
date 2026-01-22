# Installation DOCKER

Utilisez Docker pour monter l'infrastructure complète :

```Bash
cd conf/docker
docker compose -f docker-compose.yml up -d
```

Une fois les conteneurs actifs, l'application devrait maintenant être accessible sur http://localhost:xxxx.

Si vous pouvez tester que le clonage fonctionne dans le container 01-api-gateway : docker compose exec 01-api-gateway git clone https://git.pdplibre.org/Construction_PA/PA_Communautaire.git pl
