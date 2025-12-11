# Specs brique Validation Métier

**ATTENTION** : Les fonctionnalités actuellement décrites n'ont pas été validées et sont succeptible de comporter des erreurs ou lacunes.

La brique de validation métier est responsable de la validation des opérations sur les aspects spécifiquement métier.
Chaque société peurt définir des règles de validation des factures fournisseurs ou factures client.
La validation des factures fournisseurs permets de refuser/accepter des factures conformes/non-conformes.
La validation des factures clients permets d'éviter d'émettre des factures qui seraient probablement rejetées par le client.
Les règles de validation sont définies pour chaque société.

Exemple de règles de validation:
- la facture doit contenir la référence au bon de livraison
- l'adresse de facturation doit être *fiscalement* compatible avec l'adresse de livraison
- la facture doit contenir la référence au bon de commande ou contrat ou devis ou contrat de sous-traitance ou contrat de prestation de service ou contrat de location ou contrat de garantie ou contrat de maintenance
- la référence au bon de livraison, ou autre document, doit être valide (existe dans la base de données via appel API)
- une analyse labo doit être attachée à la facture pour les produits sensibles
- les taux de TVA de chaque produit doivent être vérifié
- les produits facturés doivent correspondre à leur zone géographique (ex: un produit dermatologique doit avoir un libellé particulier pour les US pour éviter un risque de class action)

Example de contrôle qui n'entrent pas dans le champs de la validation métier car effectué préalablement à cette étape:
- la facture doit être au format factur-x
- le total doit être égale à la somme des lignes
- le tiers émetteur est connu
- le tiers destinataire est connu

## Cas d'utilisation

- [CU01 - Valider une facture](CU01.md)
- [CU02 - Refuser une facture](CU02.md)
- [CU03 - Valider par défaut une facture](CU03.md)

## Endpoints API / payload ESB

Est-ce utilie de définir des endpoints API pour cette brique si tous les échanges passent par l'ESB ?


## Questions

Questions en cours à arbitrer.

(éléments à conserver pour une future FAQ)

1. La validation concerne-t-elle aussi les factures émises ?

    **Oui**: celà permets de rejetter une facture non-conforme avant qu'elle ne le soit par le PA du client

1. La validité métier d'une facture peut-elle être testée même si la facture n'est pas dans le champs du PA (facture étrangère) ?

    **Oui**: les contrôles métiers ne sont pas limités aux restrictions actuelles des PA

1. Que devient une facture qui à échoue à l'étape de validation métier ?

    **???**

1. Puis-je définir des règles métier spécifiques à mon entreprise ?

    **Oui**: un système à définir de *webhook*, appels API

1. Mon outils de gestion peut-il être informé du rejet d'une facture ?

    **Oui**: votre système peut au choix consulter via un appel API l'état de la facture ou s'inscrire à une annonce **webhook**  