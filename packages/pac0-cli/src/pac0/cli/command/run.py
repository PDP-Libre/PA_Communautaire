# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess

import typer
from pydantic import BaseModel

from .. import utils
from ..lib.conf import DEFAULT_BRANCH, DEFAULT_REPO, SERVICES, Brique
from ..lib.process import install_run
from ..lib.settings import settings

app = typer.Typer()


class BriqueRunDef(BaseModel):
    envvars: dict[str, str | None]
    cmd: list[str]
    cwd: str | None = None


BRIQUE_RUN_DEF: dict[Brique, BriqueRunDef] = {
    "01-api-gateway": BriqueRunDef(
        envvars={
            "AWS_ACCESS_KEY_ID": settings.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": settings.aws_secret_access_key,
            "NATS_URL": settings.nats_url,
            "S3_BUCKET": settings.s3_bucket,
            "S3_REGION": settings.s3_region,
            "S3_URL": settings.s3_url,
        },
        cmd=[
            "uv",
            "run",
            "fastapi",
            "dev",
            "--host=0.0.0.0",
            "src/pac0/service/api_gateway/main.py",
        ],
    ),
    # TODO: ajouter les autres services
    "02-esb-central": BriqueRunDef(
        envvars={},
        cmd=["nats-server", "-V", "-js"],
    ),
    "03-controle-formats": BriqueRunDef(
        envvars={},
        cmd=[
            "uv",
            "run",
            "faststream",
            "run",
            "pac0.service.controle_formats.main:app",
        ],
    ),
    "04-validation-metier": BriqueRunDef(
        envvars={},
        cmd=[
            "uv",
            "run",
            "faststream",
            "run",
            "pac0.service.validation_metier.main:app",
        ],
    ),
    "05-conversion-formats": BriqueRunDef(
        envvars={},
        cmd=[
            "uv",
            "run",
            "faststream",
            "run",
            "pac0.service.conversion_formats.main:app",
        ],
    ),
    "06-annuaire-local": BriqueRunDef(
        envvars={},
        cmd=[
            "uv",
            "run",
            "faststream",
            "run",
            "pac0.service.annuaire_local.main:app",
        ],
    ),
    "07-routage": BriqueRunDef(
        envvars={},
        cmd=[
            "uv",
            "run",
            "faststream",
            "run",
            "pac0.service.routage.main:app",
        ],
    ),
    "08-transmission-fiscale": BriqueRunDef(
        envvars={},
        cmd=[
            "uv",
            "run",
            "faststream",
            "run",
            "pac0.service.transmission_fiscale.main:app",
        ],
    ),
    "09-gestion-cycle-vie": BriqueRunDef(
        envvars={},
        cmd=[
            "uv",
            "run",
            "faststream",
            "run",
            "pac0.service.gestion_cycle_vie.main:app",
        ],
    ),
    "10-stockage": BriqueRunDef(
        envvars={},
        cmd=["weed", "mini", f"-dir={settings.s3_data}"],
    ),
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
    service = SERVICES[int(command_name) - 1]

    install_run(
        service=service,
        repo_url=repo,
        branch=branch,
        tools=["git"],
        install_tools=install_tools,
        install_src=install_src,
        envvar=BRIQUE_RUN_DEF[service].envvars,
        cmd=BRIQUE_RUN_DEF[service].cmd,
        cwd=BRIQUE_RUN_DEF[service].cwd,
    )


@app.command(name="proxy", help="lance le proxy 01-api-gateway ...")
def _():
    # service folder: "05-conversion-formats" -> "conversion_formats"
    base_folder = utils.get_app_base_folder()
    pac0_package_base_folder = base_folder / "packages" / "pac0"
    full_path = "src/pac0/service/api_gateway/main.py"
    cmd = ["uv", "run", "fastapi", "dev", "--host=0.0.0.0", str(full_path)]
    typer.echo("Lancement du proxy...")
    typer.echo(f"Commande: {' '.join(cmd)}")
    typer.echo(f"pac0_package_base_folder: {pac0_package_base_folder}")

    subprocess.call(
        cmd,
        cwd=pac0_package_base_folder,
        env={
            **os.environ,
            "PAC0_PROXY_PROXY__ENABLED": "true",
        },
    )
