# language: fr
Fonctionnalité: cycle de vie
    Les messages circulent de services en services.

    Scénario: cycle basique

        Quand je publie le message 'hello' sur le canal 'api-gateway-OUT'

        Alors j'obtiens le message 'hello' sur le canal 'controle-formats-IN'
        Et j'obtiens le message 'hello' sur le canal 'controle-formats-OUT'

        Alors j'obtiens le message 'hello' sur le canal 'validation-metier-IN'
        Et j'obtiens le message 'hello' sur le canal 'validation-metier-OUT'

