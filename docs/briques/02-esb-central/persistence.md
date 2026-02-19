# persistence

Voici les [streams](https://docs.nats.io/nats-concepts/jetstream/streams) à définir:
    - stream conservation longue pour 01-IN et 09-OUT
    - stream conservation moyenne pour les autres flux des briques
    - stream conservation moyenne pour les appels externes (peppol, api fiscal, ...)
    - stream éphémère pour les messages info/système (persistance activée pour les tests)
    - stream pour les fichiers générés (avant stockage s3)


TODO:
- durée de conservation à définir
