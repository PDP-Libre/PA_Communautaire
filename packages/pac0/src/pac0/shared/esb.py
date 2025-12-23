from pydantic_settings import BaseSettings
from faststream import FastStream, ContextRepo
from faststream.nats import NatsBroker


class SettingsService(BaseSettings):
    # any_flag: bool
    ...


def init_esb_app():
    # broker = NatsBroker("nats://demo.nats.io:4222")
    broker = NatsBroker("nats://localhost:4222")
    app = FastStream(broker)
    publisher_ping = broker.publisher("pong")
    publisher_pong = broker.publisher("pong")


    @app.on_startup
    async def setup(context: ContextRepo, env: str = ".env"):
        print("setup pac0 service ...")
        settings = SettingsService(_env_file=env)
        context.set_global("settings", settings)


    @broker.subscriber("ping")
    async def ping(message):
        await publisher_pong.publish("Hi!", correlation_id=message.correlation_id)

    return broker, app


#async def main_esb_app():
#    broker, app = init_esb_app()
#    await app.run()
#
#
# if __name__ == "__main__":
#    asyncio.run(main_esb_app())
