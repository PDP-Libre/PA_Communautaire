import subprocess
from pathlib import Path

import typer

from .. import utils


app = typer.Typer()

DEFAULT_REPO_URL = "https://github.com/paxpar-tech/PA_Communautaire"


@app.command()
def tool(
    install: bool = False,
):
    """Vérifie les versions d'outils et les installe si besoin"""
    typer.echo("Vérification des outils...")
    # TODO: check dependencies (some pytest)

    # raise NotImplementedError()


@app.command()
def source(
    repo_url: str = DEFAULT_REPO_URL,
    uv_sync: bool = True,
):
    """Clone le dépôt git"""

    target_dir: Path = utils.get_app_base_folder()
    # Vérifier que le dépôt est cloné
    # git pull ??

    if not (target_dir / ".git").is_dir():
        subprocess.call(["git", "clone", repo_url], cwd=target_dir)
        # target_dir has changed since git clone created a new dir
        target_dir: Path = utils.get_app_base_folder()
    else:
        print("git pull ...")
        subprocess.call(["git", "pull"], cwd=target_dir)

    # TODO: loop over all packages
    # app_base_dir = Path(target_dir) / Path(repo_url).name / "packages" / "pac0"
    app_base_dir = Path(target_dir) / "packages" / "pac0"
    if uv_sync:
        subprocess.call(["uv", "sync", "--all-packages"], cwd=app_base_dir)
