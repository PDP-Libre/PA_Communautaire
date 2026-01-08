# language: fr
Fonctionnalité: Rejet facture
    Rejet par défaut d'une facture

    Scénario: Facture rejetée
        Etant un utilisateur

        Quand je dépose une facture
        Alors j'obtiens un numéro de tâche

        Quand j'interroge la tâche

        Alors j'obtiens le statut #rejected