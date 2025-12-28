from pydantic import BaseModel
import pytest
from pytest_bdd import given, parsers, scenario, then, when

#TODO: move to pac0

class TestContext(BaseModel):
    ...

@given(
    parsers.parse("la PA #{pa}"),
)
def pa_given(pa):
    raise NotImplementedError()


@pytest.fixture
async def pac():
    # async with await nats.server.run(port=0) as server:
    #    assert server.is_running is True
    #    assert server.port > 0
    #    yield server
    ...


@pytest.fixture
def auth():
    return {}


@pytest.fixture
def author():
    return "bob"


# Etant un utilisateur
@given("un utilisateur")
def author_user(auth, author, pac):
    auth["user"] = author
    assert pac.is_running is True
