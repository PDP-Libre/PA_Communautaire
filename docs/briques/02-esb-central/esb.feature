# language: fr
Fonctionnalité: ESB
    Service Entreprise Service Bus

    Scénario: Canal ping/pong
        Etant un utilisateur

        Quand j'écoute le canal 'pong'
        Quand je publie le message 'hello' sur le canal 'ping'
        Alors j'obtiens sur le message 'hello' sur le canal 'pong'


