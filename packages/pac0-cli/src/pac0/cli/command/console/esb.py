from faststream.nats import NatsBroker
from faststream import FastStream


broker = NatsBroker("nats://localhost:4222")


def app_factory():
    app = FastStream(broker)
    return app

@broker.subscriber("test")  # subject name
async def handle_msg(msg_body):
    print("recieved ....")
