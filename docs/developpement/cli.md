# pac0-cli

Un outils en ligne de commande (CLI) est disponible.


Il est publie comme [paquet python dans le forge du projet forgejo](https://forgejo.org/docs/latest/user/packages/pypi/).


TODO: expliquer l'invocation avec uvx

```shell
```

## publication

Voir la [doc uv](https://docs.astral.sh/uv/guides/package/#building-your-package) sur le sujet.

```shell
cd packages/pac0-cli
# version courqnte
uv version
# nouvelle version mineur
uv version --bump minor
# construction  du paquet
uv build
# authentification depot cible
export UV_PUBLISH_URL=
#export UV_PUBLISH_USERNAME=
#export UV_PUBLISH_PASSWORD=
export UV_PUBLISH_TOKEN=
# publication
uv publish
```