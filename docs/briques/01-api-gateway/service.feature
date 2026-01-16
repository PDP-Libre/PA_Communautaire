# language: fr
Fonctionnalité: service api gateway
    Le service 01-api-gateway dépends du service 02-esb-central.


    Scénario: démarrage/arrêt service api gateway

        Quand je lance le service "02-esb-central"
        Alors le service "02-esb-central" est prêt
        Et le service "01-api-gateway" n'est pas prêt

        Quand je lance le service "01-api-gateway"
        Alors le service "02-esb-central" est prêt
        Et le service "01-api-gateway" est prêt
