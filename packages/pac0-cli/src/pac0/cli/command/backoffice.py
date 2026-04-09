# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later


import typer

from ..lib import report

app = typer.Typer()


@app.command(name="report", help="génère un rapport d'utilisation")
def _(
    source: str = "/tmp/pac0/proxy/store/",
    dest: str = "/tmp/pac0/proxy/report/",
    delta: int = 0,
    rebuild: bool = False,
    # let multiple filter_member args
    filter_member: list[str] | None = None,
):
    res = report.do(source, dest, delta, rebuild, filter_member)
    # pretty print the result as a table
    print(res)


@app.command(name="jwt", help="génère les jetons JWT")
def _():
    raise NotImplementedError()
