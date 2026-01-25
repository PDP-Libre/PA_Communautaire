_Section en cours de définition par la communauté_

Suivez les débats sur [le forum PDPLIBRE](https://forum.pdplibre.org/)

# Stack technologique (proposition initiale)

- **Backend** : À définir collectivement
- **Frontend** : À définir collectivement
- **Base de données** : À définir collectivement
- **Hébergement** : Compatible SecNumCloud
- **Sécurité** : Conformité ISO 27001

## 📚 Documentation

Le projet est découpé en 10 briques:

* [01-api-gateway](../briques/01-api-gateway/README.md)
* [02-esb-central](../briques/02-esb-central/README.md)
* [03-controle-formats](../briques/03-controle-formats/README.md)
* [04-validation-metier](../briques/04-validation-metier/README.md)
* [05-conversion-formats](../briques/05-conversion-formats/README.md)
* [06-annuaire-local](../briques/06-annuaire-local/README.md)
* [07-routage](../briques/07-routage/README.md)
* [08-transmission-fiscale](../briques/08-transmission-fiscale/README.md)
* [09-gestion-cycle-vie](../briques/09-gestion-cycle-vie/README.md)
* [10-stockage](../briques/10-stockage/README.md)

Vous trouverez également dans ce dépôt les [normes de référence](../norme/index.md).

D'autres liens sont disponibles sur [le projet awesome-facturation-electronique](https://github.com/PDP-Libre/awesome-facturation-electronique)

Le système utilise les services suivants:   
* un serveur de message [NATS](https://github.com/nats-io/nats-server)  
  pour encaisser un grand nombre de sollicitations et séquencer avec rigueur les différents traitements
* un serveur d'API FASTAPI  
  pour faciliter les appels entre les différentes applications
* un système de test basé sur la méthode [Behavior Driven Development](https://fr.wikipedia.org/wiki/Programmation_pilot%C3%A9e_par_le_comportement)  
  pour pouvoir vérifier le bon fonctionnement de tous les flux autours du projet et garantir une stabilité des fonctionnalités au fur et à mesure du développement.
* un stockage fichier S3  
  pour stocker un gros volume de fichier tel que les factures en pdf  
  Voir [seaweedfs](https://github.com/seaweedfs/seaweedfs)

On a choisi de mettre en place des tests en mode "Behavior Driven Development" pour permettre à des non programmeurs de pouvoir expliquer et valider le fonctionnement du système. 

## Sous-projets

Le présent projet est [un monorepo](https://en.wikipedia.org/wiki/Monorepo).
Les sous-projets sont dans le répertoire `/packages`:

* [packages/pac-bdd](../../packages/pac-bdd/README.md) permets d'exécuter les tests BDD.
* [packages/pac0](../../packages/pac0/README.md) est l'implémentation de référence.  

# Arborescence

Nous allons trouver l'arborescence suivante :

* /docker  
  Les fichiers de configuration de la version DOCKER
* /docs  
  les documentations diverses : métier et développeur
  * /docs/briques:  
  contient aussi de la doc métier et les tests BDD compréhensible pour tout le monde
  * /docs/norme:  
  les fichiers ou les liens de la norme de référence
* /packages  
  Les sources des applications  
  * pac-bdd  
  L'application qui fait tourner les tests BDD qui sont dans /docs/briques
  * pac0  
  Une application "proto" pour maquetter l'organisation en place.  
  Les choix d'architecture et de langage sont en cours de réflexions. 
* /report  
  Contient les rapports suite au lancement des tests. 
* /script  
  Diverses commandes a tout faire

