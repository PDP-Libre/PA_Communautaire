# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# voir https://docs.nats.io/using-nats/developer/receiving/wildcards#python-1

from faststream.nats import NatsBroker
from faststream import FastStream


#TODO: move to conf
broker = NatsBroker("nats://localhost:4222")


def app_factory():
    app = FastStream(broker)
    return app

@broker.subscriber("test")  # subject name
async def handle_msg(msg_body):
    print("recieved ....")
