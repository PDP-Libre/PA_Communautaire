# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from pathlib import Path
from typing import Annotated

import typer

from .. import utils
from ..lib import setup
from rich.table import Table
from rich.console import Console


app = typer.Typer()
console = Console()

DEFAULT_REPO_URL = "https://github.com/paxpar-tech/PA_Communautaire"


@app.command()
def tool(
    tool: Annotated[list[str], typer.Argument()],
    install: bool = True,
    summary: bool = True,
):
    installed_tools: list[setup.SetupTool] = []
    if tool == ["all"]:
        tool = [t.name for t in setup.tools]
    for single_tool in tool:
        for t in setup.tools:
            if single_tool in (t.name, ""):
                installed_tools.append(t)
                if install:
                    t.setup()
                if single_tool != "":
                    # return only if single tool install, stay for all
                    break
        else:
            if single_tool != "":
                # only if ask for a specific tool
                print(f"tool {single_tool} not supported !")

    if summary:
        table = Table()

        table.add_column("tool", style="cyan", no_wrap=True)
        table.add_column("required", justify="right", style="magenta")
        table.add_column("installed", justify="right", style="green")

        for t in installed_tools:
            valid = t.check()
            table.add_row(
                t.name, t.version, t.checked_version, style="red" if not valid else None
            )

        console.print(table)


@app.command()
def source(
    repo_url: str = DEFAULT_REPO_URL,
    uv_sync: bool = True,
):
    """Clone le dépôt git"""

    target_dir: Path = utils.get_app_base_folder()
    # Vérifier que le dépôt est cloné
    # git pull ??

    if not (target_dir / ".git").is_dir():
        subprocess.call(["git", "clone", repo_url], cwd=target_dir)
        # target_dir has changed since git clone created a new dir
        target_dir: Path = utils.get_app_base_folder()
    else:
        print("git pull ...")
        subprocess.call(["git", "pull"], cwd=target_dir)

    # TODO: loop over all packages
    # app_base_dir = Path(target_dir) / Path(repo_url).name / "packages" / "pac0"
    app_base_dir = Path(target_dir) / "packages" / "pac0"
    if uv_sync:
        subprocess.call(["uv", "sync", "--all-packages"], cwd=app_base_dir)
