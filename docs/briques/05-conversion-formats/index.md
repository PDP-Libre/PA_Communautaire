# Specs conversion formats

Convertir la facture déposée dans les autres formats imposés par la norme (voir XP_Z12-012.pdf section 4.2).

Déterminer si cette conversion doit être faite à la demande ou systématiquement.
Il semble impératif de devoir disposer au moins du format PDF facturX.

Prévoir un modèle de facture au cas où un visuel ne serait pas déposé avec la facture.
Ce modèle peut être global à la plateforme PAC ou spécifique à une société.


## messages

- `SUBJECT_05_IN` : message consommé en situation nominale
- `SUBJECT_05_OUT` : message produit en situation nominale
- `SUBJECT_05_ERR` : message produit en cas d'erreur
- `<PACID>/<EID>/<IID>/facturx.xml` : fichier XML factur-x

## stockage

- `<PACID>/<EID>/<IID>/facturx.pdf` : facture au format factur-x
- `<PACID>/<EID>/<IID>/ubl.xml` : facture au format UBL


Stockage local des fichiers en cours de conversion.


## communication externe

Aucune communication externe.

