# language: fr
Fonctionnalité: service esb central
    Le service 02-esb-central.


    Scénario: démarrage/arrêt service esb central

        Quand le service "02-esb-central" n'est pas prêt
        Et je lance le service "02-esb-central"
        Alors le service "02-esb-central" est prêt
