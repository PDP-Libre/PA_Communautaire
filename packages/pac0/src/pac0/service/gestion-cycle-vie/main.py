from pac0.shared.esb import init_esb_app, QUEUE


# X="api-gateway-OUT"
SUBJECT_01_ERR = "api-gateway-ERR"
SUBJECT_01_OUT = "api-gateway-OUT"
SUBJECT_02_ERR = "esb-central-ERR"
SUBJECT_03_IN = "controle-formats-IN"
SUBJECT_03_OUT = "controle-formats-OUT"
SUBJECT_03_ERR = "controle-formats-ERR"
SUBJECT_04_IN = "validation-metier-IN"
SUBJECT_04_OUT = "validation-metier-OUT"
SUBJECT_04_ERR = "validation-metier-ERR"
SUBJECT_05_IN = "conversion-formats-IN"
SUBJECT_05_OUT = "conversion-formats-OUT"
SUBJECT_05_ERR = "conversion-formats-ERR"
SUBJECT_06_IN = "annuaire-local-IN"
SUBJECT_06_OUT = "annuaire-local-OUT"
SUBJECT_06_ERR = "annuaire-local-ERR"
SUBJECT_07_IN = "routage-IN"
SUBJECT_07_OUT = "routage-OUT"
SUBJECT_07_ERR = "routage-ERR"
SUBJECT_08_IN = "transmission-fiscale-IN"
SUBJECT_08_OUT = "transmission-fiscale-OUT"
SUBJECT_08_ERR = "transmission-fiscale-ERR"
SUBJECT_09_ERR = "gestion-cycle-vie-ERR"


broker, app = init_esb_app()

publisher_03_IN = broker.publisher(SUBJECT_03_IN)
publisher_04_IN = broker.publisher(SUBJECT_04_IN)
publisher_05_IN = broker.publisher(SUBJECT_05_IN)
publisher_06_IN = broker.publisher(SUBJECT_06_IN)
publisher_07_IN = broker.publisher(SUBJECT_07_IN)
publisher_08_IN = broker.publisher(SUBJECT_08_IN)

publisher_err = broker.publisher(SUBJECT_09_ERR)


@broker.subscriber(SUBJECT_01_OUT, QUEUE)
async def process_01_to_03(message):
    await publisher_03_IN.publish(message, correlation_id=message.correlation_id)


@broker.subscriber(SUBJECT_03_OUT, QUEUE)
async def process_03_to_04(message):
    await publisher_04_IN.publish(message, correlation_id=message.correlation_id)

@broker.subscriber(SUBJECT_04_OUT, QUEUE)
async def process_04_to_05(message):
    await publisher_05_IN.publish(message, correlation_id=message.correlation_id)

@broker.subscriber(SUBJECT_05_OUT, QUEUE)
async def process_05_to_06(message):
    await publisher_06_IN.publish(message, correlation_id=message.correlation_id)

@broker.subscriber(SUBJECT_06_OUT, QUEUE)
async def process_06_to_07(message):
    #TODO: ne faire le routage que si non présent dans l'annuaire
    # TODO: trouver `dans_annuaire_local` dans `message`
    dans_annuaire_local = True
    # soit on passe à 07 ou à 08
    next_publisher = publisher_07_IN if not dans_annuaire_local else publisher_08_IN
    await next_publisher.publish(message, correlation_id=message.correlation_id)

@broker.subscriber(SUBJECT_07_OUT, QUEUE)
async def process_07_to_08(message):
    await publisher_08_IN.publish(message, correlation_id=message.correlation_id)


@broker.subscriber(SUBJECT_01_ERR, QUEUE)
@broker.subscriber(SUBJECT_02_ERR, QUEUE)
@broker.subscriber(SUBJECT_03_ERR, QUEUE)
@broker.subscriber(SUBJECT_04_ERR, QUEUE)
@broker.subscriber(SUBJECT_05_ERR, QUEUE)
@broker.subscriber(SUBJECT_06_ERR, QUEUE)
@broker.subscriber(SUBJECT_07_ERR, QUEUE)
@broker.subscriber(SUBJECT_08_ERR, QUEUE)
async def process_err(message):
    # TODO: common err behaviour
    ...
