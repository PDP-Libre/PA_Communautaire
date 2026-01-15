# language: fr
Fonctionnalité: healthcheck message

    Scénario: healthcheck message

        Quand je publie le message 'hello' sur le canal 'healthcheck'
        Alors j'obtiens le message 'toto' sur le canal 'healthcheck_resp' 
        
        #Alors j'obtiens sur le canal 'healthcheck_resp' un message
        #    """
        #    healthcheck: ok
        #    from: esb-central
        #    msg: hello
        #    """


