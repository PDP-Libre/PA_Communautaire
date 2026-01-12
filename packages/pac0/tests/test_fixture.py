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
    world4pac fixture
    """
    await world.pa_new(4)
    # async with world.pas[0].api_gateway.get_client_async() as client:

    for pa in world.pas:
        print(f"testing pac {pa} ...")

        # async with pa.HttpxAsyncClient() as client:
        async with pa.api_gateway.get_client_async() as client:
            print(f"testing pac {pa} ...")
            # print(pa.info())

            response = await client.get("/")
            assert response.status_code == 200
            assert response.json() == {"Hello": "World"}

            response = await client.get("/healthcheck")
            assert response.status_code == 200
            assert response.json() == {"status": "OK", "rank": "dev"}
