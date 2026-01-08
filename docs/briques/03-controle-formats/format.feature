# language: fr
Fonctionnalité: Support format factur-X
    Controle de factures au format factur-X

    Scénario: Controle format factur-x
        Etant un utilisateur

        Quand je dépose pour contrôle la facture @FA213746_20251211_124749.pdf
        Alors j'obtiens le statut #valid

        Quand je dépose pour contrôle la facture @FA213747_20251211_124840.pdf
        Alors j'obtiens le statut #valid

        Quand je dépose pour contrôle la facture @UC1_F202500003_00-INV_20250701.pdf
        Alors j'obtiens le statut #valid
