from pac0.shared.esb import init_esb_app, QUEUE


SUBJECT_IN = "controle-formats-IN"
SUBJECT_OUT = "controle-formats-OUT"
SUBJECT_ERR = "controle-formats-ERR"

broker, app = init_esb_app()
publisher_out = broker.publisher(SUBJECT_OUT)
publisher_err = broker.publisher(SUBJECT_ERR)
publisher = broker.publisher("test")


@broker.subscriber(SUBJECT_IN, QUEUE)
async def process(message):
    await publisher_out.publish(message, correlation_id=message.correlation_id)
    # await publisher_err.publish(message, correlation_id=message.correlation_id)


# dummy handler
@broker.subscriber("test")
async def base_handler(body: str):
    print("xxxxxxxxxxxxxxxxx1")
    print(body)
    print("xxxxxxxxxxxxxxxxx2")


# dummy handler
@broker.subscriber("test2")
async def handle(message):
    await publisher.publish("Hi!", correlation_id=message.correlation_id)
