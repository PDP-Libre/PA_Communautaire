# Specs brique routage


## Formats à utiliser

Les formats dépendent de la nature du flux transmis au Concentrateur de Données (CdD) du PPF :

    Flux de TVA (e-invoicing - Flux 1) : Ce flux est extrait de la facture commerciale (Flux 2) par la Plateforme Agréée (PA). Les formats structurés du socle minimal pour ce flux sont l’UBL 2.1 ou l’UN/CEFACT CII D22B.
    Flux des transactions (e-reporting - Flux 10) : Ce flux concerne les ventes B2C (tickets de caisse), le B2B international (export) et les données de paiement. Le format technique utilisé est la syntaxe FRR (FRench Reporting).
        UnitaryCustomerTransactionReport (10.1) : pour les ventes B2B internationales.
        AggregatedCustomerTransactionReport (10.3) : pour les cumuls quotidiens de ventes B2C.
    Factures rejetées (Flux 6) : Une facture rejetée par la PA (car irrecevable ou non conforme) ne génère pas de Flux 1 ou 10, mais la PA a l'obligation de transmettre au PPF un message de statut de cycle de vie au format UN/CEFACT CDAR avec le code statut « Rejetée » (code 213).


## Fréquence de transmission

    e-invoicing (Flux 1) : La PA doit transmettre les données fiscales au moment du dépôt de la facture par le vendeur. Les exemples de cinématique indiquent que la transmission au PPF doit se faire sous 24h après que la PA a posé le statut « Déposée ».
    e-reporting (Flux 10) :
        Pour les ventes B2C, les données sont souvent transmises sous forme de cumul quotidien pour chaque journée de la période de reporting.
        Pour les données de paiement (10.4), la transmission doit s'effectuer durant la période de e-reporting définie par le régime de TVA de l'entreprise (par exemple, avant le 10 du mois suivant pour les entreprises au régime normal).
    Statuts obligatoires (Flux 6) : Les statuts « Déposée », « Rejetée », « Refusée » et « Encaissée » (si TVA à l'encaissement) doivent être transmis au PPF dès leur création par la PA ou l'entreprise.


## Durée de conservation

Les sources fournies ne spécifient pas de durée légale de conservation (comme les 6 ou 10 ans habituels du Code de commerce ou fiscal). Elles mentionnent toutefois :

    Le rôle du Portail Public de Facturation (PPF) comme plateforme assurant la réception et la concentration de ces données pour l'État.
    La possibilité pour les entreprises d'utiliser des Solutions Compatibles (SC) ou des PA pour l'archivage.
    L'existence d'un statut spécifique « ArchiveOnly » recommandé pour les flux (comme des avoirs internes annulant une facture rejetée) qui ne doivent pas faire l'objet d'un traitement fiscal mais uniquement d'un archivage.

En résumé, la PA assure l'extraction et la transmission quasi-immédiate pour le e-invoicing (UBL/CII) et périodique pour le e-reporting (FRR), tout en notifiant systématiquement les rejets techniques via des messages CDAR.