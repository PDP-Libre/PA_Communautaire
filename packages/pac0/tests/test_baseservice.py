# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac0.shared.test.service.base import BaseServiceContext

from pac0.shared.tools.api import (
    find_available_port,
    is_port_available,
)


async def test_svc_internal():
    # start the service (default behaviour)
    BaseServiceContext()
    assert False

    
async def test_svc_external():
    # use an already started service (default behaviour)
    #TODO: subprocess ...
    BaseServiceContext()
    assert False

async def test_find_port():
    # find 3 different ports
    find_available_port

    is_port_available
    
    assert False