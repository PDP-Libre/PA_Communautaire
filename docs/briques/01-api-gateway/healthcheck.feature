# language: fr
Fonctionnalité: healthcheck
    Section 4.4 de XP_Z12-013.pdf 
    L’API publiée par le Fournisseur API doit avoir une route GET / healthcheck
    permettant au Client API de vérifier si le service API est opérationnel.


    Scénario: healthcheck api ok
        Etant un utilisateur

        Quand j'appele l'API GET /healthcheck
        Alors j'obtiens le code de retour 200


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


