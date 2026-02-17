# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
from pathlib import Path

import typer
from pydantic_settings import BaseSettings

from .. import utils
from ..lib.conf import DEFAULT_BRANCH, DEFAULT_REPO
from . import setup

app = typer.Typer()


class SettingsCLI(BaseSettings):
    """
    les settings CLI
    via .env ou variables d'environnement
    """

    api_url: str | None = None
    nats_url: str | None = None
    s3_bucket: str | None = None
    s3_region: str | None = None
    s3_url: str | None = None
    s3_data: str | None = None
    uv_publish_token: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None


settings = SettingsCLI(
    _env_file=".env",
    # _env_prefix="PAC0_",
)


def _run_service(
    service: str,
    repo_url: str,
    branch: str,
    tools: list[str],
    install_tools: bool,
    install_src: bool,
    envvar: dict[str, str | None],
):
    if install_tools:
        setup.tool(tools)
    if install_src:
        setup.source(repo=repo_url, branch=branch)
    _ = _call(service, envvar)


def _call(
    service: str,
    envvar: dict[str, str | None],
) -> int:
    # service folder: "05-conversion-formats" -> "conversion_formats"
    service_folder = "_".join(service.split("-")[1:])
    base_folder = utils.get_app_base_folder()
    print(f"{base_folder=}")
    if service == "01-api-gateway":
        full_path = f"src/pac0/service/{service_folder}/main.py"
        cmd = ["uv", "run", "fastapi", "dev", "--host=0.0.0.0", str(full_path)]
    elif service == "02-esb-central":
        cmd = ["nats-server", "-V", "-js"]
    elif service == "10-stockage":
        # cmd = ["weed", "mini", "-dir=/tmp/data"]
        cmd = ["weed", "mini", f"-dir={settings.s3_data}"]

    else:
        # full_path = f"src/pac0/service/{service_folder}/main:app"
        full_path = f"pac0.service.{service_folder}.main:app"
        cmd = ["uv", "run", "faststream", "run", str(full_path)]

    pac0_package_base_folder = base_folder / "packages" / "pac0"
    typer.echo(f"Lancement du service {service}...")
    typer.echo(f"Commande: {' '.join(cmd)}")
    typer.echo(f"pac0_package_base_folder: {pac0_package_base_folder}")

    envvar_not_none = {
        # les variables actuelles
        **os.environ.copy(),
        # uniquement les variables d'environnement non-nulles
        **{k: v for k, v in envvar.items() if v is not None},
    }
    return subprocess.call(
        cmd,
        cwd=pac0_package_base_folder,
        env=envvar_not_none,
    )


@app.command(name="1", help="lance le service 01-api-gateway ...")
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
):
    _run_service(
        "01-api-gateway",
        repo,
        branch,
        ["git"],
        install_tools=install_tools,
        install_src=install_src,
        envvar={
            "AWS_ACCESS_KEY_ID": settings.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": settings.aws_secret_access_key,
            "NATS_URL": settings.nats_url,
            "S3_BUCKET": settings.s3_bucket,
            "S3_REGION": settings.s3_region,
            "S3_URL": settings.s3_url,
        },
    )


@app.command(name="2", help="lance le service 02-esb-central ...")
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
):
    _run_service(
        "02-esb-central",
        repo,
        branch,
        ["git"],
        install_tools=install_tools,
        install_src=install_src,
    )


@app.command(name="3", help="lance le service 03-controle-formats ...")
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
):
    _run_service(
        "03-controle-formats",
        repo,
        branch,
        ["git"],
        install_tools=install_tools,
        install_src=install_src,
    )


@app.command(name="4", help="lance le service 04-validation-metier ...")
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
):
    _run_service(
        "04-validation-metier",
        repo,
        branch,
        ["git"],
        install_tools=install_tools,
        install_src=install_src,
    )


@app.command(name="5", help="lance le service 05-conversion-formats ...")
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
):
    _run_service(
        "05-conversion-formats",
        repo,
        branch,
        ["git"],
        install_tools=install_tools,
        install_src=install_src,
    )


@app.command(name="6", help="lance le service 06-annuaire-local ...")
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
):
    _run_service(
        "06-annuaire-local",
        repo,
        branch,
        ["git"],
        install_tools=install_tools,
        install_src=install_src,
    )


@app.command(name="7", help='lance le service 07-routage") ...')
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
):
    _run_service(
        "07-routage",
        repo,
        branch,
        ["git"],
        install_tools=install_tools,
        install_src=install_src,
    )


@app.command(name="8", help="lance le service 08-transmission-fiscale ...")
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
):
    _run_service(
        "08-transmission-fiscale",
        repo,
        branch,
        ["git"],
        install_tools=install_tools,
        install_src=install_src,
    )


@app.command(name="9", help="lance le service 09-gestion-cycle ...")
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
):
    _run_service(
        "09-gestion-cycle-vie",
        repo,
        branch,
        ["git"],
        install_tools=install_tools,
        install_src=install_src,
    )


@app.command(name="10", help="lance le service 09-stockage ...")
def _(
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    install_tools: bool = False,
    install_src: bool = False,
):
    _run_service(
        "10-stockage",
        repo,
        branch,
        ["git"],
        install_tools=install_tools,
        install_src=install_src,
    )
