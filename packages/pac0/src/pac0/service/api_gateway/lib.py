from typing import Union

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

class Incoming(BaseModel):
    m: dict


def call() -> bool:
    return True


"""
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
"""


@router.get("/")
async def read_root():
    return {"Hello": "World"}


@router.post("/flows")
async def flows_post():
    await router.broker.publish("Hello, NATS!", "test")
    return {"Hello": "World"}


@router.get("/flows/{flowId}")
async def flows_get():
    return {"Hello": "World"}


@router.get("/healthcheck")
async def healthcheck(
    request: Request,
):
    # await publisher.publish("Hi!", correlation_id=message.correlation_id)
    # TODO: see https://faststream.ag2.ai/latest/getting-started/observability/healthcheks/
    # await router.broker.publish("Hello, NATS!", "test")
    # await router.broker.publish("Hi!", correlation_id=message.correlation_id)
    await request.app.state.broker.publish("Hello, NATS!", "test")

    return {
        "status": "OK",
        "rank": request.app.state.rank,
    }


# TODO: remove
@router.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
