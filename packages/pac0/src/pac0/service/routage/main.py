"""
Service de routage - Point d'entrée.

Ce service est responsable du routage des factures vers les PA distantes
via le réseau PEPPOL ou vers le PPF en fallback.
"""

from pac0.shared.esb import init_esb_app

from .lib import router


# Initialisation de l'application FastStream
broker, app = init_esb_app()

# Inclure le router de routage
broker.include_router(router)


if __name__ == "__main__":
    import asyncio

    asyncio.run(app.run())
