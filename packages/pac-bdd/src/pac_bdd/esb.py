# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import functools
from pytest_bdd import given, parsers, then, when
from pac0.shared.test.world import WorldContext, world1


handle_GLOBAL = None

# Qnand j'écoute le canal 'pong'
@when(
    parsers.parse("j'écoute le canal '{canal}'"),
)
def esb_sub(
    world1: WorldContext,
    canal: str,
):
    global handle_GLOBAL

    print(f"esb_sub {canal=}...")
    #raise NotImplementedError()
    broker = world1.pa.broker

    #@broker.subscriber(canal)
    #async def handle(msg: str) -> None:
    #    print('<<<<<<<<<<<<<<<<<<<<< handle called !', msg)

    #handle_GLOBAL = handle


# Quand je publie le message 'hello' sur le canal 'ping'
@when(
    parsers.parse("je publie le message '{msg}' sur le canal '{canal}'"),
)
def esb_pub_msg(
    world1: WorldContext,
    msg: str,
    canal: str,
):
    with world1.pa1.api_gateway.get_client() as client:
        # TODO: pass msg and canal
        response = client.post("/publish")
        assert response.status_code == 200


# Alors j'obtiens sur le message 'hello' sur le canal 'pon'
@then(parsers.parse("""j'obtiens sur le canal '{canal}' un message"""))
def esb_sub_msg1(
    world: WorldContext,
    canal: str,
):
    print('recieving message1 ...')
    raise NotImplementedError()


# Alors j'obtiens sur le message 'hello' sur le canal 'pong'
# @then(parsers.parse("""j'obtiens sur le canal '{canal}' le message '{msg}'"""))
@then(parsers.parse("""j'obtiens le message '{msg}' sur le canal '{canal}'"""))
def esb_sub_msg2(
    world1: WorldContext,
    msg: str,
    canal: str,
):
    traces = []
    with world1.pa1.api_gateway.get_client() as client:
        response = client.get("/trace")
        assert response.status_code == 200
        traces = response.json()

    for trace in traces:
        print(trace)
        if trace["subject"] == canal and trace["body"] == msg:
            return
    else:
        raise Exception("message not found !")
