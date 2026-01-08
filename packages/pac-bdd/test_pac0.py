import asyncio
import pytest
import pac0

async def test_pac0_import_services():
    import pac0.service.api_gateway.main as api_gateway_main
    import pac0.service.gestion_cycle_vie.main as gestion_cycle_vie_main
    import pac0.service.validation_metier.main as validation_metier_main

    #    asyncio.run(main_esb_app())
    # await asyncio.gather(
    #    api_gateway_main.app.run(),
    #    gestion_cycle_vie_main.app.run(),
    #    validation_metier_main.app.run(),
    # )

    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(api_gateway_main.app.run())
        task2 = tg.create_task(gestion_cycle_vie_main.app.run())
        task3 = tg.create_task(validation_metier_main.app.run())