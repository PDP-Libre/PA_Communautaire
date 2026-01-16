import typer
from typing import Optional
#from pac_cli.cli.app import app as cli_app
from pac_cli.command.setup import app as setup_app
from pac_cli.command.run import app as run_app
from pac_cli.command.test import app as test_app
from pac_cli.command.console.app import ConsoleApp

app = typer.Typer()

# Ajout des commandes CLI
#app.add_typer(cli_app, name="cli")
app.add_typer(setup_app, name="setup")
app.add_typer(run_app, name="run")
app.add_typer(test_app, name="test")


@app.command()
def console():
    """Lance l'application console"""
    console_app = ConsoleApp()
    console_app.run()


@app.command()
def version():
    """Affiche la version de l'application"""
    typer.echo("pac-cli version 0.1.0")


if __name__ == "__main__":
    app()
