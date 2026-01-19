# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
import subprocess

app = typer.Typer()


@app.command()
def all():
    """Lance tous les tests"""
    typer.echo("Lancement de tous les tests...")
    subprocess.call(["pytest", "-v"])
