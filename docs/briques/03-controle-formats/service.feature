# language: fr
Fonctionnalité: service controle formats

    Scénario: démarrage/arrêt service controle formats

        Quand le service "03-controle-formats" n'est pas prêt
        Et je lance le service "03-controle-formats"
        Alors le service "03-controle-formats" est prêt
