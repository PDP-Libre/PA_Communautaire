# TODO branche courante

* [x] faire le test principal BDD : boucle_metier.feature
* [x] pour les tests on a besoin de scruter les messages, il faut donc les *conserver* le temps du test
* [x] pour conserver les messages on peut avoir un tâche *spy* qui écoute tous les messages ; KO car BBD est sync et nats est async
* [ ] pour conserver les messages on peut s'appuyer sur la persistence nats jetstream
* [x] faire des tests pour scruter les messages
* [x] lister et nettoyer les variables d'environnement
* [ ] merge depuis main quand la branche docker sera intégrée
* [ ] créer des streams NATS pour persister les messages
* [x] doc sommaire stream et persistence
* [ ] faire des tests nats jetstream pour persistence
* [ ] faire des tests nats jetstream pour lecture synchrone BDD
