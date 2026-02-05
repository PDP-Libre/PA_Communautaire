# outils de tests

TODO: documenter les aspects suivants:
- comment on teste un service en le lancant
- comment on peut tester avec une instance locale
- l'acces aux fichiers de doc/ref avec ~

Pour tester une instance PAC il faut que les services (briques) soit lancés.
Il y a plusieurs approches pour disposer de ces services :

- services éphémères : tester une instance pac0 qui sera créée, et détruite, automatiquement par les tests via une `fixture`
- services locaux : tester une instance pac0 déjà lancée localement via `localhost`
- services déployés : tester directement une instance pac0 déjà déployé via son `FQDN`

## services éphémères

C'est le fonctionnement par défaut, il n'y a rien à préciser.
Les instances pac0 seront créées à la volée.

```shell
cd packages/pac0
uv run pytest -v
```

## services locaux


Dans ce particulier, on souhaite pouvoir utiliser les services pac0 qui sont déjà lancés localement.
Cette approche facilite le développement.

```shell
cd packages/pac0
# lancement des services localement
docker-compose up
# variable d'environnement pour indiquer aux tests de ne pas instancier les services
# mais d'utiliser les services locaux déjà lancés
export PP_XXXX_XXXX=1
uv run pytest -v
```

## services déployés


TODO: décrire comment surcharger la conf pour pointer vers des briques 01/02/10 spécifiées par leur FQDN
