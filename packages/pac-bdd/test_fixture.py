import pytest


@pytest.fixture
def myctx():
    return {}


def test_a(myctx):
    assert True


@pytest.fixture
async def myctx2():
    return {}


async def test_b(myctx2):
    assert True    