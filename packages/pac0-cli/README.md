# pac cli

```
______________________________ 
________________ ________  __ \
_____  __ \  __ `/  ___/  / / /
____  /_/ / /_/ // /__ / /_/ / 
___  .___/\__,_/ \___/ \____/  
__/_/                          

```

Outil en ligne de commade (CLI) du projet pac (Plateforme Agréée Communautaire).
En plus de l'usage CLI, un mode application console est disponible.

Caractéristiques principales:
- utilise les librairies python typer et textual
- appelé par la commande `pac-cli` or `pac`
- publié sur pypi avec le nom `pac-cli`

Caractéristiques principales de la version CLI:
- commande `pac-cli setup tool` qui vérifie les versions d'outils et les installe si besoin (selon un fichier YAML de référence). Exemple: nats-server, natscli, seaweedfs ...
- commande `pac-cli setup source` qui clone le dépôt github https://github.com/paxpar-tech/PA_Communautaire
- commande `pac-cli run pac0` qui lance `uv run fastapi dev src/pac0/service/api_gateway/main.py` du dépôt cloné
- commande `pac-cli run pac0 --svc 01-api-gateway` qui lance `uv run fastapi dev src/pac0/service/api_gateway/main.py` du dépôt cloné ou un autre service selon la valeur de `--svc`
- commande `pac-cli test all` qui lance une commande via subprocess


Caractéristiques principales de la version console:
- commande `pac-cli` ou `pac-cli console` qui lance la version console
- reproduire l'ergonomie générale de l'application console [k9s](https://k9scli.io/)
- avoir une palette de commande
- avoir des raccourcis clavier
- avoir une page `services` où lister les services pac0
- pouvoir afficher le log d'un service
- avoir une page `stats` où afficher des compteurs (factures reçues, factures traitées, erreur, ...)
- avoir une page `tests` où lister les tests depuis un fichier xml testsuites