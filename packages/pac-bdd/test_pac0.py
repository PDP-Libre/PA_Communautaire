import pytest
import pac0

async def test_pac0_import_services():
    import pac0.service.api_gateway.main
    import pac0.service.gestion_cycle_vie.main
    import pac0.service.validation_metier.main
