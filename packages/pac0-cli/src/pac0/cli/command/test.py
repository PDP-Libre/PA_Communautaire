import typer
from pac_cli.utils.subprocess_runner import run_command

app = typer.Typer()


@app.command()
def all():
    """Lance tous les tests"""
    typer.echo("Lancement de tous les tests...")
    run_command(["pytest"])

