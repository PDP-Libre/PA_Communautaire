# language: fr
Fonctionnalité: healthcheck message

    Scénario: healthcheck message
        #Quand j'écoute le canal 'healthcheck_resp'
        Quand j'écoute le canal 'healthcheck'
        Quand je publie le message 'hello' sur le canal 'healthcheck'
        Alors j'obtiens sur le canal 'healthcheck_resp' le message 'toto'
        #Alors j'obtiens sur le canal 'healthcheck_resp' un message
        #    """
        #    healthcheck: ok
        #    from: esb-central
        #    msg: hello
        #    """


