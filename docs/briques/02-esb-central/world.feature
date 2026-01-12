# language: fr
Fonctionnalité: Gestion du monde de test (WorldContext)
    Le monde de test permet de configurer un environnement complet avec:
    - Un service NATS (broker de messages)
    - Un service Peppol (recherche d'entreprises)
    - Plusieurs instances PA (plateformes agréées)

    Tous les services respectent le ServiceProtocol pour une gestion
    uniforme du cycle de vie (démarrage, arrêt, détection de disponibilité).

    Références:
    - ServiceProtocol: pac0.shared.test.protocol
    - WorldContext: pac0.shared.test.world

    # =========================================================================
    # Scénarios de base: Services individuels
    # =========================================================================

    Scénario: Démarrage d'un service NATS local
        Etant donné un service NATS local
        Alors le service NATS est en cours d'exécution
        Et le service NATS a un endpoint valide
        Et le service NATS est de type local

    Scénario: Connexion à un service NATS distant
        Etant donné un service NATS local comme référence
        Et un service NATS connecté à l'endpoint de référence
        Alors le service NATS distant est en cours d'exécution
        Et le service NATS distant est de type distant

    Scénario: Démarrage d'un service Peppol mock
        Etant donné un service Peppol en mode mock
        Alors le service Peppol est en cours d'exécution
        Et le service Peppol utilise le mode mock

    Scénario: Configuration des réponses Peppol mock
        Etant donné un service Peppol en mode mock
        Et une entreprise avec le SIREN "123456789" enregistrée sur Peppol
        Quand je recherche l'entreprise avec le SIREN "123456789" sur Peppol
        Alors le lookup Peppol réussit
        Et l'endpoint retourné est "https://ap.mock.peppol/as4"

    Scénario: Recherche Peppol d'une entreprise non enregistrée
        Etant donné un service Peppol en mode mock
        Quand je recherche l'entreprise avec le SIREN "999999999" sur Peppol
        Alors le lookup Peppol échoue
        Et le code erreur est "PARTICIPANT_NOT_FOUND"

    Scénario: Démarrage d'un service PA
        Etant donné un service PA
        Alors le service PA est en cours d'exécution
        Et le service PA a un endpoint API valide
        Et le service PA répond au healthcheck

    # =========================================================================
    # Scénarios WorldContext: Configuration de base
    # =========================================================================

    Scénario: Création d'un monde avec 1 PA
        Etant donné un monde avec 1 PA
        Alors le monde est en cours d'exécution
        Et le monde contient 1 PA
        Et le service NATS du monde est en cours d'exécution
        Et le service Peppol du monde est en cours d'exécution

    Scénario: Création d'un monde avec 2 PA
        Etant donné un monde avec 2 PA
        Alors le monde contient 2 PA
        Et la PA #1 est en cours d'exécution
        Et la PA #2 est en cours d'exécution

    Scénario: Création d'un monde avec 4 PA
        Etant donné un monde avec 4 PA
        Alors le monde contient 4 PA

    # =========================================================================
    # Scénarios WorldContext: Partage des services
    # =========================================================================

    Scénario: Les PA partagent le même service NATS
        Etant donné un monde avec 2 PA
        Alors la PA #1 utilise le service NATS du monde
        Et la PA #2 utilise le service NATS du monde

    Scénario: Les PA ont des ports API distincts
        Etant donné un monde avec 3 PA
        Alors chaque PA a un port API différent

    # =========================================================================
    # Scénarios WorldContext: Healthcheck et communication
    # =========================================================================

    Scénario: Toutes les PA répondent au healthcheck
        Etant donné un monde avec 2 PA
        Quand j'appelle le healthcheck de la PA #1
        Alors j'obtiens le code de retour 200
        Et le statut est "OK"
        Quand j'appelle le healthcheck de la PA #2
        Alors j'obtiens le code de retour 200
        Et le statut est "OK"

    Scénario: Information du monde
        Etant donné un monde avec 2 PA
        Quand je demande les informations du monde
        Alors les informations contiennent le service NATS
        Et les informations contiennent le service Peppol
        Et les informations contiennent 2 PA

    # =========================================================================
    # Scénarios WorldContext: Cycle de vie
    # =========================================================================

    Scénario: Arrêt propre du monde
        Etant donné un monde avec 2 PA démarré
        Quand j'arrête le monde
        Alors toutes les PA sont arrêtées
        Et le service NATS est arrêté
        Et le service Peppol est arrêté

    # =========================================================================
    # Scénarios avancés: Configuration personnalisée
    # =========================================================================

    Scénario: Monde avec NATS externe
        Etant donné un service NATS local comme référence
        Et un monde utilisant le service NATS de référence avec 1 PA
        Alors le monde utilise le service NATS de référence
        Et le service NATS de référence reste actif après l'arrêt du monde

    Scénario: Monde avec Peppol personnalisé
        Etant donné un service Peppol en mode mock comme référence
        Et un monde utilisant le service Peppol de référence avec 1 PA
        Alors le monde utilise le service Peppol de référence

    # =========================================================================
    # Scénarios inter-PA: Communication
    # =========================================================================

    Scénario: Dépôt de facture entre 2 PA via Peppol
        Etant donné un monde avec 2 PA
        Et l'entreprise #E1 avec le SIREN "111111111"
        Et l'entreprise #E2 avec le SIREN "222222222"
        Et l'entreprise #E1 enregistrée sur la PA #1
        Et l'entreprise #E2 enregistrée sur la PA #2 via Peppol
        Et une facture #F1 de #E1 vers #E2
        Quand un utilisateur de la PA #1 dépose la facture #F1
        Alors le lookup Peppol pour #E2 réussit
        Et la facture est routée vers la PA #2
