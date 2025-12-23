from typing import Union

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from faststream.nats.fastapi import NatsRouter, Logger


app = FastAPI()

router = NatsRouter("nats://localhost:4222")
app.include_router(router)

# publisher = broker.publisher("test")


class Incoming(BaseModel):
    m: dict


def call() -> bool:
    return True


@router.after_startup
async def test(app: FastAPI):
    await router.broker.publish("Startup!!!", "test")


@router.subscriber("test3")
@router.publisher("response")
async def hello(
    message: Incoming,
    logger: Logger,
    dependency: bool = Depends(call),
):
    logger.info("Incoming value: %s, depends value: %s" % (message.m, dependency))
    return {"response": "Hello, NATS!"}


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/flows")
async def flows_post():
    await router.broker.publish("Hello, NATS!", "test")
    return {"Hello": "World"}


@app.get("/flows/{flowId}")
async def flows_get():
    return {"Hello": "World"}


@app.get("/healthcheck")
async def healthcheck():
    # await publisher.publish("Hi!", correlation_id=message.correlation_id)
    await router.broker.publish("Hello, NATS!", "test")
    await publisher_pong.publish("Hi!", correlation_id=message.correlation_id)

    return {"status": "OK"}



#TODO: remove
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
