# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess

import typer

from ..lib.conf import DEFAULT_BRANCH, DEFAULT_REPO
from ..lib.process import install_run
from ..lib.settings import settings

app = typer.Typer()


@app.command()
def all():
    """Lance tous les tests"""
    typer.echo("Lancement de tous les tests...")
    subprocess.call(["pytest", "-v"])


@app.command()
def bdd(
    repo: str = typer.Option(DEFAULT_REPO, help="URL du dépôt git"),
    branch: str = typer.Option(DEFAULT_BRANCH, help="Branche du dépôt git"),
    install_tools: bool = typer.Option(False, help="Installation des outils"),
    install_src: bool = typer.Option(False, help="Installation des sources"),
    pytest_args: list[str] = typer.Option(
        None, "--", help="Arguments supplémentaires pour pytest"
    ),
):
    """
    Lance les tests BDD

    example:
        uv run pac0 test bdd test_scenario.py::test_flow_des_messages
    est équivalent à :
        uv run pytest -vs test_scenario.py::test_flow_des_messages
    """
    typer.echo("Lancement des tests BDD...")
    pytest_cmd = ["pytest"] + (pytest_args or [])

    install_run(
        cmd=pytest_cmd,
        repo_url=repo,
        branch=branch,
        tools=["git"],
        install_tools=install_tools,
        install_src=install_src,
        envvar={
            "API_URL": settings.api_url,
            "AWS_ACCESS_KEY_ID": settings.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": settings.aws_secret_access_key,
            "BRIQUE_EXTERNE": "1" if settings.brique_externe else None,
            "NATS_URL": settings.nats_url,
            "S3_BUCKET": settings.s3_bucket,
            "S3_DATA": settings.s3_data,
            "S3_REGION": settings.s3_region,
            "S3_URL": settings.s3_url,
        },
    )
