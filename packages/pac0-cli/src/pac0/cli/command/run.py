# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later


from pathlib import Path

import typer

from ..lib.conf import DEFAULT_BRANCH, DEFAULT_REPO, SERVICES, Brique
from ..lib.process import install_run
from ..lib.settings import settings

app = typer.Typer()


BRIQUE_ENVARS: dict[Brique, dict[str, str | None]] = {
    "01-api-gateway": {
        "AWS_ACCESS_KEY_ID": settings.aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": settings.aws_secret_access_key,
        "NATS_URL": settings.nats_url,
        "S3_BUCKET": settings.s3_bucket,
        "S3_REGION": settings.s3_region,
        "S3_URL": settings.s3_url,
    },
    # TODO: ajouter les autres services
}


@app.command(name="10", help="lance le service 10-stockage")
@app.command(name="9", help="lance le service 09-gestion-cycle")
@app.command(name="8", help="lance le service 08-transmission-fiscale")
@app.command(name="7", help="lance le service 07-routage")
@app.command(name="6", help="lance le service 06-annuaire-local")
@app.command(name="5", help="lance le service 05-conversion-formats")
@app.command(name="4", help="lance le service 04-validation-metier")
@app.command(name="3", help="lance le service 03-controle-formats")
@app.command(name="2", help="lance le service 02-esb-central")
@app.command(name="1", help="lance le service 01-api-gateway")
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
    ctx: typer.Context = typer.Option(None, hidden=True),
):
    # Get the command name from the context
    command_name = ctx.info_name or "1"

    # Get the service name based on the command
    service = SERVICES[int(command_name) - 1]
    # get the envvar for this service
    envvar = BRIQUE_ENVARS[service]

    install_run(
        service=service,
        repo_url=repo,
        branch=branch,
        tools=["git"],
        install_tools=install_tools,
        install_src=install_src,
        envvar=envvar,
    )
