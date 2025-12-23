from pac0.shared.esb import init_esb_app


broker, app = init_esb_app()

publisher = broker.publisher("test")


@broker.subscriber("test")
async def base_handler(body: str):
    print("xxxxxxxxxxxxxxxxx1")
    print(body)
    print("xxxxxxxxxxxxxxxxx2")


@broker.subscriber("test2")
async def handle(message):
    await publisher.publish("Hi!", correlation_id=message.correlation_id)
