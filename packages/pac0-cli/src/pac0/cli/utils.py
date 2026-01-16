import os
from pathlib import Path

import typer


def get_app_base_folder(
    up: str = "PA_Communautaire",
    create: bool = True,
    check: bool = True,
) -> Path:
    '''
    Détermine le chemin de l'application.
    up: si non vide, permets de *remonter* jusqu'à ce répertoire (utile en dev)
    create: crée le chemin de répertoire si besoin
    check: vérifie si le répertoire existe
    '''
    # env var ou répertoire courant
    repo_path = Path(os.environ.get("PAC0_BASE_PATH") or ".").resolve()

    if up != "":
        if (repo_path / up).is_dir():
            repo_path = repo_path / up
        elif up in (p := repo_path.parts):
            repo_path = Path('/'.join(p[0:p.index(up)+1])[1:])

    if create and not repo_path.exists():
        repo_path.mkdir(parents=True, exist_ok=True)

    if check and not repo_path.exists():
        typer.echo(
            "Erreur: Le dépôt n'est pas cloné. Exécutez 'pac-cli setup source' d'abord."
        )
        raise typer.Exit(code=1)

    return repo_path
