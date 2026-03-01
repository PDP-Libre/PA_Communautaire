# persistence

Certain des messages doivent être persistés pour une durée plus longue que celle des messages en cours de traitement.

Pour définir ces politiques de conservation, nous avons besoin de la notion de **stream** et de **consumer**.

## streams

Voici les [streams](https://docs.nats.io/nats-concepts/jetstream/streams) à définir:
    - stream conservation longue pour 01-IN et 09-OUT
    - stream conservation moyenne pour les autres flux des briques
    - stream conservation moyenne pour les appels externes (peppol, api fiscal, ...)
    - stream éphémère pour les messages info/système (persistance activée pour les tests)
    - stream pour les fichiers générés (avant stockage s3)

Avoir plusieurs **stream** distincts va permettre de mieux gérer les données et de les organiser en fonction de leur importance et de leur durée de conservation. Par exemple, les données sensibles ou les données à long terme peuvent être stockées dans un stream spécifique, tandis que les données temporaires ou les données de test peuvent être stockées dans un autre stream.

Le stockage à long terme est assuré par la brique **10-stockage** qui dispose également d'une notion de [persistence](/docs/briques/10-stockage/README.md#persistence).

TODO:
- durée de conservation à définir par stream
- fixer une taille maximale par stream ?

## consumers

Voici les [consumers](https://docs.nats.io/nats-concepts/jetstream/consumers) à définir:
- `consumer flow` pour consommer les messages en suivant le flux normal (dispatch push, durable)
- `consumer status` pour pouvoir suivre l'avancement du flux normal (dispatch push, durable)
- `consumer status1` pour pouvoir suivre l'avancement du flux normal pour un seule facture (dispatch push, durable)
- `consumer test` pour pouvoir consulter les messages déjà consommés (dispatch pull, ordered, ephemeral)
-

Propriétés d'un consumer:
- [durable/ephemeral](https://docs.nats.io/nats-concepts/jetstream/consumers#persistence-durable-ephemeral))
- [ordered](https://docs.nats.io/nats-concepts/jetstream/consumers#ordered-consumers)
- [dispatch push/pull](https://docs.nats.io/nats-concepts/jetstream/consumers#dispatch-type-pull-push)
