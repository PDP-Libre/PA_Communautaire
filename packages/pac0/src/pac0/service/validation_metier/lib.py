from pac0.shared.esb import QUEUE
from faststream.nats import NatsRouter


SUBJECT_IN = "controle-formats-IN"
SUBJECT_OUT = "controle-formats-OUT"
SUBJECT_ERR = "controle-formats-ERR"

router = NatsRouter()

publisher_out = router.publisher(SUBJECT_OUT)
publisher_err = router.publisher(SUBJECT_ERR)
publisher = router.publisher("test")


@router.subscriber(SUBJECT_IN, QUEUE)
async def process(message):
    await publisher_out.publish(message, correlation_id=message.correlation_id)
    # await publisher_err.publish(message, correlation_id=message.correlation_id)


# dummy handler
@router.subscriber("test")
async def base_handler(body: str):
    print("xxxxxxxxxxxxxxxxx1")
    print(body)
    print("xxxxxxxxxxxxxxxxx2")


# dummy handler
@router.subscriber("test2")
async def handle(message):
    await publisher.publish("Hi!", correlation_id=message.correlation_id)
