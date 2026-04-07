# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
from pathlib import Path

import typer

from .. import utils
from ..command import setup
from .settings import settings


def _call(
    service: str | None = None,
    envvar: dict[str, str | None] | None = None,
    cmd: list[str] | None = None,
    cwd: Path | None = None,
) -> int:

    if cmd is None:
        if service is None:
            raise ValueError("Either cmd or service must be provided")

    if cwd is None:
        base_folder = utils.get_app_base_folder()
        cwd = base_folder / "packages" / "pac0"

    typer.echo(f"pac0_package_base_folder: {cwd}")

    typer.echo(f"Commande: {' '.join(cmd)}")
    envvar_not_none = {
        # les variables actuelles
        **os.environ.copy(),
        # et uniquement les variables d'environnement surchargées non-nulles
        **{k: v for k, v in (envvar or {}).items() if v is not None},
    }
    return subprocess.call(
        args=cmd,
        cwd=cwd,
        env=envvar_not_none,
    )


def install_run(
    repo_url: str,
    branch: str,
    tools: list[str] | None,
    install_tools: bool,
    install_src: bool,
    envvar: dict[str, str | None],
    service: str | None = None,
    cmd: list[str] | None = None,
    cwd: Path | None = None,
):
    if install_tools and tools:
        setup.tool(tools)
    if install_src:
        setup.source(repo=repo_url, branch=branch)
    _ = _call(
        service=service,
        envvar=envvar,
        cmd=cmd,
        cwd=cwd,
    )
