# Specs annuaire local

Il faut déterminer si la facture déposée a été émise par une entreprise utilisatrice de la plateforme PAC.
Pour celà, nous disposon d'un annuaire local à la plateforme.

Peut-on interroger PEPPOL pour déterminer si l'entreprise est gérée par la plateforme ?

Quelles informations doivent être présentes dans cette plateforme ?

## messages

- `SUBJECT_06_IN` : message consommé en situation nominale
- `SUBJECT_06_OUT` : message produit en situation nominale
- `SUBJECT_06_ERR` : message produit en cas d'erreur
- `SUBJECT_LOCAL_DIRECTORY_UPDATE` : message écouté
- `KV_LOCAL_DIRECTORY` : fichier annuaire local

## stockage

Aucun accès à la brique `10-stockage`.

Stockage local d'une copie de l'annuaire local.

## communication externe

Aucune communication externe.
