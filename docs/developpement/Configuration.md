# Configurer le stockage S3

TODO expliquer comment utiliser S3 en local avec docker pour le dev, utiliser S3 avec un fournisseur externe tel SCALEWAY ou xxxCloud

Expliquer comment gérer l'authentification


## variables d'environnements


* `API_URL`: adresse de la brique 01 de l'API, exemples:
    - `http://localhost:8000`
* `AWS_ACCESS_KEY_ID`: clé d'accès à la brique 10 de stockage
* `AWS_SECRET_ACCESS_KEY`: secret d'accès à la brique 10 de stockage
* `BRIQUE_EXTERNE`: indique lors des tests de ne pas instancier les briques car déjà présentes en externe
* `NATS_URL`: adresse de la brique 02 de messagerie, exemples:
    - `nats://02-esb-central:4222`
    - `nats://localhost:4222`
* `NAMESPACE`: nom du namespace pour le déploiement kubernetes
* `S3_BUCKET`: nom du bucket S3, valeur par défaut `pac0-bucket`
* `S3_DATA`: chemin pour le stockage seaweedfs (defaut: `/data`)
* `S3_REGION`: région S3, valeur par défaut `fr-par`
* `S3_URL`: adresse de la brique 10 de stockage, exemples:
    - `http://localhost:8333`
    - `https://store.document.legal`
* `UV_PUBLISH_TOKEN`: token pour publier le package CLI sur pypi


Variables à déclarer par brique (✅) et par environnement (✔️):

| variable \ brique       | 01 | 02 | 03..09 | 10 | prod | dev | test |
|-------------------------|----|----|--------|----|------|-----|------|
| API_URL                 |    |    |        |    |      | ✔️  |  ✔️  |
| API_CAPTURE             | ✅ |    |        |    |      | ✔️  |  ✔️  |
| AWS_ACCESS_KEY_ID       |    |    |        | ✅ |  ✔️  | ✔️  |  ✔️  |
| AWS_SECRET_ACCESS_KEY   |    |    |        | ✅ |  ✔️  | ✔️  |  ✔️  |
| BRIQUE_EXTERNE          |    |    |   ✅   |    |      | ✔️  |  ✔️  |
| NATS_URL                | ✅ |    |   ✅   |    |  ✔️  | ✔️  |  ✔️  |
| S3_BUCKET               | ✅ |    |        |    |      | ✔️  |  ✔️  |
| S3_DATA                 | ✅ |    |        |    |      | ✔️  |  ✔️  |
| S3_REGION               | ✅ |    |        |    |      | ✔️  |  ✔️  |
| S3_URL                  | ✅ |    |        |    |  ✔️  | ✔️  |  ✔️  |
| UV_PUBLISH_TOKEN        |    |    |        |    |      | ✔️  |      |
| NAMESPACE               |    |    |        |    |      | ✔️  |      |


