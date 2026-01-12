from pydantic import BaseModel
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from faststream import FastStream, TestApp, Context
from faststream.nats import NatsBroker, TestNatsBroker
from faststream.context import ContextRepo
import pytest_asyncio

# TODO: move to pac0 ??

broker = NatsBroker("nats://localhost:4222")


@broker.subscriber("*")
async def handle_all() -> None:
    print("<<<<<<<<<<<<<<<<<<<<< handle_all called !")


class PaContext(BaseModel):
    """
    See https://medium.com/@hitorunajp/asynchronous-context-managers-f1c33d38c9e3
    """

    _broker: NatsBroker
    _app: FastStream
    _test_broker: TestNatsBroker
    _test_app: TestApp

    @property
    def app(self) -> FastStream:
        return self._app

    @property
    def broker(self) -> NatsBroker:
        return self._broker

    @property
    def test_app(self) -> TestApp:
        return self._test_app

    @property
    def test_broker(self) -> TestNatsBroker:
        return self._test_broker

    def __init__(self, **data):
        print("vvvvv dbg 10")
        super().__init__(**data)
        print("vvvvv dbg 30")

    async def __aenter__(self):
        print("vvvvv dbg aenter 10")
        # TODO: get from args or env
        # broker = NatsBroker("nats://localhost:4222")
        self._broker = broker
        self._app = FastStream(broker, context=ContextRepo({"var1": "my-var1-value"}))
        # self._test_broker = TestNatsBroker(self._app.broker, connect_only=True)
        self._test_broker = TestNatsBroker(self._app.broker)
        self._test_app = TestApp(self._app)
        print("vvvvv dbg aenter 20")
        self._test_broker = await self._test_broker.__aenter__()
        await self._test_app.__aenter__()
        print("vvvvv dbg aenter 30")

        # @broker.subscriber("*")
        # async def handle_all() -> None:
        #    print("<<<<<<<<<<<<<<<<<<<<< handle_all called !")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("vvvvv dbg aexit 10")
        await self._test_app.__aexit__(exc_type, exc_val, exc_tb)
        await self._test_broker.__aexit__(exc_type, exc_val, exc_tb)
        print("vvvvv dbg aexit 20")


class WorldContextOld(BaseModel):
    # esb: None = None
    _pac: PaContext
    _pacs: list[PaContext]

    @property
    def pac(self) -> PaContext:
        return self._pac

    @property
    def pacs(self) -> list[PaContext]:
        return self._pacs

    def __init__(self, **data):
        super().__init__(**data)
        self._pac = PaContext()
        self._pacs = [self._pac]

    async def __aenter__(self):
        await self._pac.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._pac.__aexit__(exc_type, exc_val, exc_tb)


# TODO: use real broker/app
broker = NatsBroker("nats://localhost:4222")
app = FastStream(broker, context=ContextRepo({"var1": "my-var1-value"}))


# @pytest.fixture
@pytest_asyncio.fixture
async def world() -> WorldContextOld:
    print("vvvvv world fixture starts .......")

    async with (
        # TestNatsBroker(app.broker, connect_only=True) as br,
        # TestApp(app) as test_app,
        WorldContextOld() as w,
    ):
        print("vvvvv dbg async with 10")
        yield w
        print("vvvvv dbg async with 20")

    print("vvvvv world fixture ends .......")


@pytest.fixture
def user():
    return {}


# TODO: clean mess


class TestContext(BaseModel): ...


# Note: "la PA #{pa_id}" is now defined in peppol.py as pa_defined


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
@given(parsers.parse("un utilisateur de la PA #{pa}"))
def author_user_pa(pa): ...


# Etant un utilisateur
@given("un utilisateur")
def author_user(auth, author, pac):
    auth["user"] = author
    assert pac.is_running is True
