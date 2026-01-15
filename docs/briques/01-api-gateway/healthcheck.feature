# language: fr
Fonctionnalité: healthcheck
    Section 4.4 de XP_Z12-013.pdf 
    L’API publiée par le Fournisseur API doit avoir une route GET / healthcheck
    permettant au Client API de vérifier si le service API est opérationnel.


    Contexte:
        Soit une pa communautaire

    
    Scénario: healthcheck

        Etant un utilisateur

        Quand j'appele l'API GET /healthcheck
        Alors j'obtiens le code de retour 200


    Scénario: healthcheck deep

        Quand j'appele l'API GET /healthcheck/deep
        Alors j'obtiens le code de retour 200
        Et la réponse a une clé "healthcheck_resp" avec 7 éléments

