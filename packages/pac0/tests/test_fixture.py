import pytest

from pac0.shared.test.fixture import world1pac, world4pac

@pytest.mark.asyncio
async def test_world1pac(
    world1pac,
) -> None:
    """
    world1pac fixture
    """
    async with world1pac.pac1.HttpxAsyncClient() as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

        response = await client.get("/healthcheck")
        assert response.status_code == 200
        assert response.json() == {"status": "OK", "rank": "test"}


@pytest.mark.asyncio
async def test_world4pac(
    world4pac,
) -> None:
    """
    world4pac fixture
    """
    for pac in world4pac.pacs:
        print(f"testing pac {pac} ...")

        async with pac.HttpxAsyncClient() as client:
            print(f"testing pac {pac} ...")
            print(pac.info())

            response = await client.get("/")
            assert response.status_code == 200
            assert response.json() == {"Hello": "World"}

            response = await client.get("/healthcheck")
            assert response.status_code == 200
            assert response.json() == {"status": "OK", "rank": "test"}
