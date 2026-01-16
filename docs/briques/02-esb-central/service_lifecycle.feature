# language: fr
# TODO: deprecate !!
Fonctionnalité: Cycle de vie des services
    Tests du cycle de vie des services FastStream et NATS pour la plateforme PA.

    Ces scénarios vérifient que les services démarrent correctement,
    communiquent via NATS, et répondent aux requêtes API.

    Références:
    - FastStream: https://faststream.ag2.ai/latest/getting-started/lifespan/hooks/
    - NATS: https://nats.io/
    - pytest-bdd: https://pytest-bdd.readthedocs.io/

    # -------------------------------------------------------------------------
    # Scénarios de base: Infrastructure NATS
    # -------------------------------------------------------------------------

    Scénario: Démarrage d'un serveur NATS
        Etant donné un serveur NATS disponible
        Alors le serveur NATS est en cours d'exécution

    Scénario: Connexion d'un broker au serveur NATS
        Etant donné un serveur NATS disponible
        Quand je connecte un broker NATS
        Alors le broker est connecté

    # -------------------------------------------------------------------------
    # Scénarios multi-PA: Tests de plusieurs instances
    # -------------------------------------------------------------------------

    Scénario: Démarrage de plusieurs PA
        Etant donné 2 PA démarrées
        Alors chaque PA a son propre port NATS
        Et chaque PA a son propre port API

    # -------------------------------------------------------------------------
    # Note: Les scénarios API (test_appel_api_racine, test_healthcheck_de_lapi)
    # sont désactivés car ils nécessitent une solution pour le problème
    # d'interaction entre les fixtures async pytest-asyncio et les steps
    # synchrones de pytest-bdd lors des appels HTTP.
    #
    # Voir test_service_lifecycle.py pour les tests API équivalents qui
    # fonctionnent correctement avec des tests async purs.
    # -------------------------------------------------------------------------
