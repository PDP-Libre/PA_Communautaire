# language: fr
Fonctionnalité: Rejet facture
    Rejet par défaut d'une facture

    Scénario: 3 pa
        On va tester le depot d'une facture sur un pa
        le pa2 ne recoit rien 
        le pa3 reçoit la facture

        Quand je dépose une facture #f1 "UC2_F202500004_00-INV_20250701.pdf" sur #pa1
        Alors j'obtiens un statut "accepté"

        Quand je consulte #pa2
        Alors je ne trouve pas la facture #f1

        Quand je consulte #pa3
        Alors je trouve la facture #f1

