# Installation DOCKER
## Pré-requis

* Avoir lu la documentation sur [documentation sur l'architecture](Architecture.md)
* Avoir docker sur sa machine.  
  Vous pouvez utiliser docker ou podman. 

> [!WARNING]
> Attention sous Ubuntu 24.04: les paquets APT sont trop anciens.  
> Préférez `snap install docker` ou la version depuis les dépots Docker.

Pour éviter de passé en root pour lancer les containers, il faut rajouter l'utilisateur courant dans le groupe docker :

```Bash
 sudo usermod -aG docker $USER
```
*Il faut se déconnecter, reconnecter pour que la modification prenne effet*

## Lancement des containers

Docker va monter l'infrastructure complète avec chacun des services du projet :

```Bash
docker compose up -d
```
ou avec podman :
```Bash
podman compose -f docker-compose.yml up -d
```


Une fois les conteneurs actifs, l'application devrait maintenant être accessible sur http://localhost:8000/docs.

Vous pouvez [lancer les tests](BDD_Guide_Developpeur.md) et commencer à developper.

## Vérifications

Permet de voir l'état des containers :
```Bash
docker compose ps
```

Commande permet de vérifier que les 10 containers tourne :
```Bash
count=$(docker compose ps | grep Up | wc -l); if [ "$count" -eq 10 ]; then echo -e "\033[32mOK ✅ Tous les conteneurs sont en cours d'exécution.\033[0m"; else echo -e "\033[31mKO ❌ $count conteneurs sont en cours d'exécution. Attendu : 10.\033[0m"; fi
```

Pour vérifier que la brique api fonctionne, aller sur http://localhost:8000/docs  
Les fichiers du serveur S3 sont vissible ici : http://localhost:8888/buckets  

### Test du serveur S3

S3 est un serveur de fichier qui va stocker les factures. On peut utiliser une version dans le cloud ou utiliser sa propre instance en local.

Test du fonctionnement du serveur S3 local en lancant le test test_s3fs 
```
docker compose exec 01-api-gateway uv run pytest tests/test_s3fs.py
```
Le fichier est visible ici : http://localhost:8888/buckets/my-bucket/my-file.txt


## Arret des containers

```Bash
docker compose stop
```

## Purge des containers

```Bash
docker compose down -v
```
*Ça supprime tous les containers et leurs volumes*
