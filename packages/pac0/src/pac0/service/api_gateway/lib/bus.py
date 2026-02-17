# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

from fastapi import FastAPI
from faststream.nats.fastapi import NatsMessage, NatsRouter

from pac0.service.api_gateway.lib import trace
from pac0.service.api_gateway.lib.common import global_state
from pac0.shared.esb import get_nats_url

router = NatsRouter(get_nats_url())


# @router.on_startup()
# def _():
#    print("@router.on_startup ...")
#    #await app.broker.publish("startup api-gateway", "service")
#    #await app.broker.publish("shutdown api-gateway", "service")


# TODO: pour une meilleure "mémorisation" des messages reçus
# voir https://docs.nats.io/using-nats/developer/receiving/wildcards#python-1
if trace.TESTING:

    @router.subscriber("*")
    async def all_sub(
        body: Any,
        msg: NatsMessage,
    ):
        """
        NatsMessage(
            body=b'Startup!!!',
            content_type=text/plain,
            message_id=457bff6c-53fe-4b65-91ed-80c5af28541e,
            correlation_id=457bff6c-53fe-4b65-91ed-80c5af28541e,
            headers={
                'content-type': 'text/plain',
                'correlation_id': '457bff6c-53fe-4b65-91ed-80c5af28541e'
            },
            path={},
            committed=None,
            raw_message=Msg(
                _client=<nats client v2.12.0>,
                subject='test',
                reply='',
                data=b'Startup!!!',
                headers={
                    'content-type': 'text/plain',
                    'correlation_id': '457bff6c-53fe-4b65-91ed-80c5af28541e'
                },
                _metadata=None,
                _ackd=True,
                _sid=2
            )
        )
        """

        # TODO: pour une meilleure "mémorisation" des messages reçus
        # voir https://docs.nats.io/using-nats/developer/receiving/wildcards#python-1
        # print("****** all_sub ...", body, msg)
        trace.add(
            trace.MsgInfo(
                body=msg.body,
                content_type=msg.content_type,
                message_id=msg.message_id,
                correlation_id=msg.correlation_id,
                path=msg.path,
                committed=msg.committed,
                subject=msg.raw_message.subject,
                reply=msg.raw_message.reply,
            )
        )


@router.subscriber("healthcheck")
async def healthcheck_sub():
    await router.broker.publish("api-gateway is alive", "healthcheck_resp")


@router.subscriber("healthcheck_resp")
async def healthcheck_resp_sub():
    # TODO: pour une meilleure "mémorisation" des messages reçus
    # voir https://docs.nats.io/using-nats/developer/receiving/wildcards#python-1
    global_state["healthcheck_resp"].append("xx")
