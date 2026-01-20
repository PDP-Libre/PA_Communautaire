_Section en cours de définition par la communauté_

Suivez les débats sur [le forum PDPLIBRE](https://forum.pdplibre.org/)

# Stack technologique (proposition initiale)

- **Backend** : À définir collectivement
- **Frontend** : À définir collectivement
- **Base de données** : À définir collectivement
- **Hébergement** : Compatible SecNumCloud
- **Sécurité** : Conformité ISO 27001

## 📚 Documentation

Le projet est découpé en 9 briques:

* [01-api-gateway](docs/briques/01-api-gateway/index.md)
* [02-esb-central](docs/briques/02-esb-central/index.md)
* [03-controle-formats](docs/briques/03-controle-formats/index.md)
* [04-validation-metier](docs/briques/04-validation-metier/index.md)
* [05-conversion-formats](docs/briques/05-conversion-formats/index.md)
* [06-annuaire-local](docs/briques/06-annuaire-local/index.md)
* [07-routage](docs/briques/07-routage/index.md)
* [08-transmission-fiscale](docs/briques/08-transmission-fiscale/index.md)
* [09-gestion-cycle-vie](docs/briques/09-gestion-cycle-vie/index.md)

Vous trouverez également dans ce dépôt les [normes de référence](norme/README.md).

D'autres liens sont disponibles sur [le projet awesome-facturation-electronique](https://github.com/PDP-Libre/awesome-facturation-electronique)

Le système utilise les services suivants:   
* un serveur de message [NATS](https://github.com/nats-io/nats-server)  
  pour encaisser un grand nombre de sollicitations et séquencer avec rigueur les différents traitements
* un serveur d'API FASTAPI  
  pour faciliter les appels entre les différentes applications
* un système de test basé sur la méthode [Behavior Driven Development](https://fr.wikipedia.org/wiki/Programmation_pilot%C3%A9e_par_le_comportement)  
  pour pouvoir vérifier le bon fonctionnement de tous les flux autours du projet et garantir une stabilité des fonctionnalités au fur et à mesure du développement.
* un stockage fichier S3  
  pour stocker un gros volume de fichier i.e les factures en pdf  
  Voir [seaweedfs](https://github.com/seaweedfs/seaweedfs)

On a choisi de mettre en place des tests en mode BDD pour permettre à des non programmeurs de pouvoir expliquer et valider le fonctionnement du système. 

## 🏗️ Sous-projets

Le présent projet est [un monorepo](https://en.wikipedia.org/wiki/Monorepo).
Les sous-projets sont dans le répertoire `/packages`:

* [packages/pac-bdd](packages/pac-bdd/README.md) permets d'exécuter les tests BDD.
* [packages/pac0](packages/pac0/README.md) est l'implémentation de référence.
