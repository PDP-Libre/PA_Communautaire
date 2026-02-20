# pac0-cli

Un outils en ligne de commande (CLI) est disponible.


Il est publie comme [paquet python dans le forge du projet forgejo](https://forgejo.org/docs/latest/user/packages/pypi/).


Comment appeler la commande :

pre-requis : seulement [uv](https://docs.astral.sh/uv/)

```shell
# on indique que le registry principal est forgejo
export UV_INDEX=https://git.pdplibre.org/api/packages/Construction_PA/pypi/simple
# on appele la commande (python et les dependances s'installent)
uvx pac0-cli version
# on récupère les sources
uvx pac0-cli setup source
```


## publication

Voir la [doc uv](https://docs.astral.sh/uv/guides/package/#building-your-package) sur le sujet.

```shell
> cd packages/pac0-cli
# version courante
> uv version
pac0-cli 0.12.0
# nouvelle version mineur
> uv version --bump minor
pac0-cli 0.12.0 => 0.13.0
# suppression des paquets générés précédemment
> rm -Rf dist
> uv clean
Cleaning up build artifacts...
# construction  du paquet
> uv build
Building source distribution (uv build backend)...
Building wheel from source distribution (uv build backend)...
Successfully built dist/pac0_cli-0.13.0.tar.gz
Successfully built dist/pac0_cli-0.13.0-py3-none-any.whl
# authentification depot cible
> export UV_PUBLISH_URL=https://git.pdplibre.org/api/packages/Construction_PA/pypi
# mettre ici un token avec le rôle package `read and write` role
> export UV_PUBLISH_TOKEN=XXXXX
# publication
> uv publish
Publishing 4 files to https://git.pdplibre.org/api/packages/Construction_PA/pypi
Uploading pac0_cli-0.13.0.tar.gz (6.3KiB)
Uploading pac0_cli-0.13.0-py3-none-any.whl (10.4KiB)
```

Package visible sur https://git.pdplibre.org/Construction_PA/-/packages
