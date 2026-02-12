# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
import subprocess
from enum import Enum

app = typer.Typer()


class ServiceType(str, Enum):
    flow = "flow"
    directory = "directory"


@app.command()
def all():
    """Lance tous les tests"""
    typer.echo("Lancement de tous les tests...")
    subprocess.call(["pytest", "-v"])


@app.command()
def swagger(
    url: str = typer.Argument(..., help="URL du swagger à valider (ex: http://localhost:8000/openapi.json)"),
    service: ServiceType = typer.Option(ServiceType.flow, "--service", "-s", help="Type de service à valider"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Affiche plus de détails"),
):
    """
    Valide la conformité d'un swagger avec XP Z12-013.

    Compare le swagger distant avec les références AFNOR :
    - flow: Flow Service (dépôt/consultation factures)
    - directory: Directory Service (annuaire)

    Exemple:
        pac test swagger http://localhost:8000/openapi.json
        pac test swagger http://localhost:8000/openapi.json --service directory
    """
    from pac0.cli.lib.swagger_validator import validate_swagger

    typer.echo(f"Validation swagger {service.value.upper()} Service...")
    typer.echo(f"URL: {url}")
    typer.echo("-" * 50)

    report = validate_swagger(url, service.value)

    for result in report.results:
        typer.echo(str(result))

    typer.echo("-" * 50)

    if report.success:
        typer.secho(
            f"✅ {report.passed_count}/{report.total_count} tests passés - CONFORME",
            fg=typer.colors.GREEN,
            bold=True
        )
        raise typer.Exit(0)
    else:
        typer.secho(
            f"❌ {report.passed_count}/{report.total_count} tests passés - NON CONFORME",
            fg=typer.colors.RED,
            bold=True
        )
        raise typer.Exit(1)
