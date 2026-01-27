import asyncio
from faststream.nats import NatsBroker
from faststream import FastStream, Context


broker = NatsBroker("nats://localhost:4222")


app = FastStream(broker)


@broker.subscriber(">")  # subject name
async def handle_msg(
    msg_body,
    #m: str = Context("message"),
    s: str = Context("message.raw_message.subject"),
):
    print("test recieved ....", s)
    await broker.publish("xxxx", "test2")


async def main():
    await broker.start()
    await broker.publish("hello", "test2")
    await asyncio.sleep(2)
    await broker.stop()


if __name__ == "__main__":
    print("dummy faststream run  ....")
    # asyncio.run(app.run())
    asyncio.run(main())
