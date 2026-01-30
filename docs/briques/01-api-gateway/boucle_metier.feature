# language: fr
Fonctionnalité: boucle métier
    Tester la boucle métier complète avec la dépose d'une facture
    et le parcours des briques.


    Scénario: flow des messages
        S'assurer que les messages circulent bien entre les différentes briques
        via la brique `gestion-cycle-vie`.

        Quand je dépose la facture ~doc/xxxx.pdf

        Alors un message arrive sur le canal "api-gateway-OUT"

        Et un message arrive sur le canal "controle-formats-IN"
        Et un message arrive sur le canal "controle-formats-OUT"

        Et un message arrive sur le canal "validation-metier-IN"
        Et un message arrive sur le canal "validation-metier-OUT"

        Et un message arrive sur le canal "conversion-formats-IN"
        Et un message arrive sur le canal "conversion-formats-OUT"

        Et un message arrive sur le canal "annuaire-local-IN"
        Et un message arrive sur le canal "annuaire-local-OUT"

        Et un message arrive sur le canal "routage-IN"
        Et un message arrive sur le canal "routage-OUT"

        Et un message arrive sur le canal "transmission-fiscale-IN"
        Et un message arrive sur le canal "transmission-fiscale-OUT"


    Scénario: stockage facture
        S'assurer que la facture déposée est bien stockée sur le service `stockage`
        et qu'un fichier de statut est bien présent.

        Quand je dépose la facture "xxxx/xxxx.pdf"
        Alors le fichier "aaa:aaa/2026/01/xxxx.pdf" est présent