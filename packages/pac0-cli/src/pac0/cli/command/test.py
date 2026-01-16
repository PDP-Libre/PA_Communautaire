import typer
import subprocess

app = typer.Typer()


@app.command()
def all():
    """Lance tous les tests"""
    typer.echo("Lancement de tous les tests...")
    subprocess.call(["pytest", "-v"])
