# language: fr
Fonctionnalité: Conformité métier
    Rejet car commande founisseur absente Dolibarr

    Scénario: Rejet Dolibarr
        Etant un utilisateur

        Quand je définis un contrôle de conformité métier fournisseur
        Et l'adresse de contrôle "https://dolibarr.com/supplier/order={supplier.id}"

        Quand je dépose la facture /data/FA-3647.pdf
        Alors j'obtiens le statut #rejected

        Quand je dépose la facture /data/FA-3648.pdf
        Alors j'obtiens le statut #accepted