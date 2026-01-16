import typer
import yaml
from pathlib import Path
from pac_cli.utils.git import clone_repository
from pac_cli.utils.version_checker import check_versions, display_versions
import subprocess

app = typer.Typer()

DEFAULT_REPO_URL = "https://github.com/paxpar-tech/PA_Communautaire"


@app.command()
def tool():
    """Vérifie les versions d'outils et les installe si besoin"""
    typer.echo("Vérification des outils...")
    raise NotImplementedError()

    # Charger la configuration depuis le fichier YAML
    config_file = Path("tools.yaml")
    if config_file.exists():
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        tools = [tool["name"] for tool in config["tools"]]
    else:
        # Fallback sur une liste par défaut
        tools = ["nats-server", "natscli", "seaweedfs"]

    versions = check_versions(tools)
    display_versions(versions)


@app.command()
def source(
    repo_url: str = DEFAULT_REPO_URL,
    target_dir: str = '.',
    uv_sync: bool = True,
):
    """Clone le dépôt git"""
    subprocess.call(["git", "clone", repo_url], cwd=target_dir)
    app_base_dir = Path(target_dir) / Path(repo_url).name
    if uv_sync:
        subprocess.call(["uv", "sync", "--all-packages"], cwd=app_base_dir)
