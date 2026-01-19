# déploiement kubernetes pac0

ATTENTION: Ce déploiement est orienté développement et non pas production !
A chaque lancement d'un container, **les sources et les dépendances sont téléchargées**.

Pré-requis: podman (ou docker).

```shell
export IMAGE=astral/uv:python3.12-bookworm-slim

# Pour éxécuter un service (03-controle-formats)
podman run -ti --rm --entrypoint uvx $IMAGE pac0-cli@latest run 3


# Pour avoir un shell de l'image
podman run -ti --rm --entrypoint /bin/bash $IMAGE

```