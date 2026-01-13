# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import functools

import httpx
from pac0.shared.test.world import WorldContext
from pytest_bdd import given, parsers, scenario, then, when


# TODO: move to shared
def async_to_sync(fn):
    """Convert async function to sync function."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))

    return wrapper



# Quand j'appele l'API GET /healthcheck
#@async_to_sync
@when(
    parsers.parse("j'appele l'API {verb} {path}"),
)
def api_call(
    world1pac: WorldContext,
    verb: str,
    path: str,
):
    #print(world1pac)

    response = httpx.get(world1pac.pac1.api_base_url)
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

    """
    async with world1pac.pac1.HttpxAsyncClient() as client:
        print(f"testing pac {world1pac.pac1} ...")
        print(world1pac.pac1.info())
        await asyncio.sleep(60)
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}
    """
    raise NotImplementedError()


# Alors j'obtiens le code de retour 200
@then(parsers.parse("j'obtiens le code de retour {code}"))
def api_return_code(code):
    #raise NotImplementedError()
    ...
