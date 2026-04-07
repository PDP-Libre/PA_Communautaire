# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
from datetime import datetime
from pathlib import Path

import dateutil
import typer
from pac0.service.api_gateway.config import Settings
from pydantic import BaseModel

from .. import utils
from ..lib.conf import DEFAULT_BRANCH, DEFAULT_REPO, SERVICES, Brique
from ..lib.process import install_run
from ..lib.settings import settings

app = typer.Typer()


@app.command(name="report", help="génère un rapport d'utilisation")
def _(
    source: str = "/tmp/pac0/proxy/store/",
    dest: str = "/tmp/pac0/proxy/report/",
    date_start: str | None = None,
    date_end: str | None = None,
):
    """
    Colonnes:
        - member_id from JWT payload
        - datetime of the request (YYYY-MM-DD HH:MM:SS)
        - verb of the request (GET, POST, PUT, DELETE)
        - endpoint of the request
        - path of the request
        - status code of the response
        - duration of the request in milliseconds
        - size of the request in bytes
        - size of the response in bytes
        - SHA256 hash of the request
        - SHA256 hash of the response
    """
    # d = datetime.strptime("2013-03-31", "%Y-%m-%d")
    one_month_ago = datetime.now() - dateutil.relativedelta.relativedelta(months=1)
    # month prefix as 202603 (YYYYMM)
    month_date_prefix = f"{one_month_ago.year}{one_month_ago.month:02d}"
    # TODO: in v2 adapt for s3
    # source_mounth_filter = Path(source) / one_month_ago.year f"{month_date_prefix}*.pac0"
    for f in Path(source).glob(f"{month_date_prefix}*.pac0"):
        print(f)
