# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from pac0.shared.test.world import world, WorldContext


async def test_world1pac(
    world,
) -> None:
    """
    world1pac fixture
    """
    await world.pa_new()
    async with world.pas[0].api_gateway.get_client_async() as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

        response = await client.get("/healthcheck")
        assert response.status_code == 200
        assert response.json() == {"status": "OK", "rank": "dev"}


@pytest.mark.asyncio
async def test_world4pac(
    world,
) -> None:
    """
    world with pas fixture
    """
    await world.pa_new(4)
    for pa in world.pas:
        print(f"testing pac {pa} ...")

        async with pa.api_gateway.get_client_async() as client:
            print(f"testing pac {pa} ...")
            # print(pa.info())

            response = await client.get("/")
            assert response.status_code == 200
            assert response.json() == {"Hello": "World"}

            response = await client.get("/healthcheck")
            assert response.status_code == 200
            assert response.json() == {"status": "OK", "rank": "dev"}
