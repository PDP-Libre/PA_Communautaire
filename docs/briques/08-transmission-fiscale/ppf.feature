# language: fr
Fonctionnalité: service esb central
    Le service 02-esb-central.


    Scénario: transmission e-invoicing

        Quand j'utilise une instance PAC
        Et un service PPF fictif

        Et je dépose la facture #f604.pdf

        Alors le service PPF reçoit une transmission


    Scénario: transmission e-invoicing detail

        Quand j'utilise une instance PAC
        Et un service PPF fictif

        Et je dépose la facture #f604.pdf

        Alors le service PPF reçoit une transmission contenant:
            id_facture: FA-604
            montant_ht: 2000.00
            montant_tva: 400.00



    Scénario: transmission e-invoicing detail

        Quand j'utilise une instance PAC
        Et un service PPF fictif

        Et je dépose la facture à la volée:
            id_facture: 608
            montant_ht: 2000.00
            taux_tva: 200%
            montant_tva: 4000.00
            
        Alors le service PPF rejette la transmission


  
    Scénario: transmission e-reporting

        Quand j'utilise une instance PAC
        Et un service PPF fictif

        Et je dépose le z de fin de journée #z1890.txt

        Alors le service PPF reçoit une transmission