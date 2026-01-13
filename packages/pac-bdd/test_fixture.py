# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest


@pytest.fixture
def myctx():
    return {}


def test_dummy_fixture(myctx):
    assert True


@pytest.fixture
async def myctx2():
    return {}


async def test_dummy_async_fixture(myctx2):
    assert True    