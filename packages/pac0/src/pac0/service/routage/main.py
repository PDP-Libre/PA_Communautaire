from pac0.shared.esb import init_esb_app, QUEUE


SUBJECT_IN = "routage-IN"
SUBJECT_OUT = "routage-OUT"
SUBJECT_ERR = "routage-ERR"

broker, app = init_esb_app()
publisher_out = broker.publisher(SUBJECT_OUT)
publisher_err = broker.publisher(SUBJECT_ERR)


@broker.subscriber(SUBJECT_IN, QUEUE)
async def process(message):
    #TODO: appel API au PA distant
    await publisher_out.publish(message, correlation_id=message.correlation_id)
    # await publisher_err.publish(message, correlation_id=message.correlation_id)
