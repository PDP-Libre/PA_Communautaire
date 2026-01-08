# language: fr
Fonctionnalité: Multiples PA
    Communication entre multiples PA
    Vérifier qu'une facture déposée sur un PA est bien transféré à un autre PA

    Scénario: 2 PA
        Soit la PA #pa1
        Et la PA #pa2
        Et l'entreprise #e1 enregistrée sur la PA #pa1
        Et l'entreprise #e2 enregistrée sur la PA #pa2
        Et la facture #f1 de #e1 à #e2

        Soit un utilisateur de la PA #pa1
        Quand je dépose la facture #f1
        Alors j'obtiens le statut #accepted

        Soit un utilisateur de la PA #pa2
        Quand je recherche la facture #f1
        Alors j'obtiens le statut #accepted
