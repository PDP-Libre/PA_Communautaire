import asyncio
import functools
import pytest
from pytest_bdd import given, parsers, then, when
from .pac0_fixture import WorldContext, handle_all


# TODO: move to shared
def async_to_sync(fn):
    """Convert async function to sync function."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))

    return wrapper


handle_GLOBAL = None

# Qnand j'écoute le canal 'pong'
@when(
    parsers.parse("j'écoute le canal '{canal}'"),
)
@async_to_sync
async def esb_sub(
    world: WorldContext,
    canal: str,
):
    global handle_GLOBAL

    print(f"esb_sub {canal=}...")
    #raise NotImplementedError()
    broker = world.pac.broker

    #@broker.subscriber(canal)
    #async def handle(msg: str) -> None:
    #    print('<<<<<<<<<<<<<<<<<<<<< handle called !', msg)

    #handle_GLOBAL = handle


# Quand je publie le message 'hello' sur le canal 'ping'
@when(
    parsers.parse("je publie le message '{msg}' sur le canal '{canal}'"),
)
@async_to_sync
async def esb_pub_msg(
    world: WorldContext,
    msg,
    canal: str,
):
    print(f"esb_pub_msg {msg=} sur le {canal=} ...")
    #await world.pac.broker.publish(msg, subject=canal)
    await world.pac.test_broker.publish(msg, subject=canal)



@then(parsers.parse("""j'obtiens sur le canal 'healthcheck_resp' le message 'toto'"""))
@async_to_sync
async def esb_sub_msg(
    world: WorldContext,
):
    #raise NotImplementedError()
    print("recieving message static ...")
    # await handle.wait_call(timeout=3)
    # handle.mock.assert_called_once_with({"name": "John", "user_id": 1})
    # await handle_GLOBAL.wait_call(timeout=3)
    # handle_GLOBAL.mock.assert_called_once_with({"name": "John", "user_id": 1})
    # await handle_all.wait_call(timeout=3)
    #handle_all.mock.assert_called_once_with({"name": "John", "user_id": 1})
    handle_all.mock.assert_called_once_with("toto")


# Alors j'obtiens sur le message 'hello' sur le canal 'pon'
@then(parsers.parse("""j'obtiens sur le canal '{canal}' un message"""))
@async_to_sync
async def esb_sub_msg1(
    world: WorldContext,
    canal: str,
):
    print('recieving message1 ...')
    #raise NotImplementedError()


'''
# Alors j'obtiens sur le message 'hello' sur le canal 'pong'
@then(parsers.parse("""j'obtiens sur le canal '{canal}' le message '{msg}'"""))
@then(parsers.parse("""j'obtiens le message '{msg}' sur le canal '{canal}'"""))
@async_to_sync
async def esb_sub_msg2(
    world: WorldContext,
    msg,
    canal: str,
):
    print("recieving message2 ...")
    raise NotImplementedError()
'''
