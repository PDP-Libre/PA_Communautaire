# Specs brique  API gateway

C'est le document XP_Z12-013.pdf de la norme Afnor qui décrit le plus précisemment l'API à implémenter.


## Swagger / OpenAPI

L’API publiée par le Fournisseur API doit respecter le SWAGGER décrit dans l’Annexe A de la norme XP_Z12-013.pdf. Un test permets de vérifier ce respect.

Les définitions swagger/OpenAPI sont disponibles via swaggerhub:
* https://app.swaggerhub.com/apis/Generixgroup8/AFNOR-Flow_Service
* https://app.swaggerhub.com/apis/Generixgroup8/AFNOR-Directory_Service


## Route /api-keys  (GET)
## Route /api-keys (POST)
## Route /api-keys/{id} (DELETE)
## Route /api-keys/{id} (GET)
## Route /api-keys/{id} (PATCH)
## Route /directory-line (POST)
## Route /directory-line/code:{id} (GET)
## Route /directory-line/id-instance:{id} (DELETE)
## Route /directory-line/id-instance:{id} (GET)
## Route /directory-line/id-instance:{id} (PATCH)
## Route /directory-line/search (POST)
## Route /flows (POST)
## Route /flows/{flowId} (GET)
## Route /healthcheck (GET)
## Route /routing-code (POST)
## Route /routing-code/id-instance:{id} (GET)
## Route /routing-code/id-instance{id} (PATCH)
## Route /routing-code/id-instance{id} (PUT)
## Route /routing-code/search (POST)
## Route /routing-code/siret:{siret}/code:{id} (GET)
## Route /search (POST)
## Route /siren/code-insee:{siren} (GET)
## Route /siren/id-instance:{id} (GET)
## Route /siren/search (POST)
## Route /siret/code-insee:{siret} (GET)
## Route /siret/id-instance:{id} (GET)
## Route /siret/search (POST)
## Route /webhook (POST)
## Route /webhook/{id} (DELETE)
## Route /webhook/{id} (GET)
## Route /webhooks (GET)

## webhook

Cf 5.6 du document XP_Z12-013.pdf

La norme ne décrit comment gérer les webhook.

Voici les routes dédiées à la gestion des webhook:
* POST /webhook
* GET /webhooks
* GET /webhook/{id}
* DELETE /webhook/{id}

## API key 

Respect du [RFC6750](https://datatracker.ietf.org/doc/html/rfc6750) "The OAuth 2.0 Authorization Framework: Bearer Token Usage".

En-tête des requêtes: `Authorization: Bearer <api_key>`

Vérification de la clé API:

![](https://athroniaeth.github.io/fastapi-api-key/schema.svg)


Voici les routes dédiées à la gestion des clés API:
* POST /api-keys : Create a key and return the plaintext secret once.
* GET /api-keys : List keys with offset/limit pagination.
* GET /api-keys/{id} : Retrieve a key by identifier.
* PATCH /api-keys/{id} : Update name, description, or activation flag.
* DELETE /api-keys/{id} : Remove a key.