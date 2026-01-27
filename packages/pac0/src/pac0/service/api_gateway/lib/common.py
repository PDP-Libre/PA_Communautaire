# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any
from fastapi import Request


def broker(
    request: Request,
):
    """dependency shortcut to access the broker"""
    return request.app.state.broker


# global state from api router or broker router
#TODO: pour une meilleure "mémorisation" des messages reçus
# voir https://docs.nats.io/using-nats/developer/receiving/wildcards#python-1
global_state: dict[str, Any] = {
    'healthcheck_resp': [],
}

