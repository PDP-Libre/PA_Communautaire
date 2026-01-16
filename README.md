
# Plateforme Agréé Communautaire

[![License](https://img.shields.io/badge/License-%C3%80_d%C3%A9finir-blue.svg)](https://claude.ai/chat/1cb854ea-44d1-42ff-973e-27e5aca83066) [![Status](https://img.shields.io/badge/Status-En_d%C3%A9veloppement-yellow.svg)](https://claude.ai/chat/1cb854ea-44d1-42ff-973e-27e5aca83066) [![Contributions](https://img.shields.io/badge/Contributions-Bienvenues-green.svg)](https://claude.ai/chat/1cb854ea-44d1-42ff-973e-27e5aca83066)

## 🎯 À propos du projet

Ce repository héberge le développement collaboratif d'une **Plateforme Agréé (PA) communautaire**, créée en réponse à la réforme française de la facturation électronique obligatoire (septembre 2026-2027).

Notre objectif est de construire une alternative **open source, transparente et sans but lucratif** aux solutions commerciales existantes, agréée par l'État français conformément au cahier des charges de la DGFiP.

## 📋 Contexte réglementaire

À partir de septembre 2026, toutes les entreprises françaises assujetties à la TVA devront :

- **Recevoir** des factures électroniques (B2B domestique)
- **Émettre** des factures électroniques (calendrier échelonné jusqu'en 2027)
- **Transmettre** à l'État les données de facturation (e-reporting)

Cette plateforme répond aux exigences du cahier des charges des Plateformes de Dématérialisation Partenaire défini par la Direction Générale des Finances Publiques (DGFiP).

## 🌟 Vision et valeurs

### Notre vision

Créer une infrastructure numérique de confiance, démocratique et pérenne, qui serve l'intérêt général plutôt que des intérêts commerciaux.

### Nos valeurs fondamentales

- **🔓 Open Source** : Code ouvert et licences libres
- **🤝 Communautaire** : Gouvernance participative et transparente
- **🛡️ Souveraineté** : Indépendance vis-à-vis des acteurs commerciaux
- **✅ Conformité** : Respect strict des exigences réglementaires
- **🌍 Accessibilité** : Solution accessible à tous les types d'entreprises

## 🚀 Fonctionnalités

### Conformité minimale obligatoire

- ✅ Réception et émission de factures électroniques
- ✅ Support des 3 formats du socle (UBL, CII, Factur-X)
- ✅ Gestion du cycle de vie des factures
- ✅ Contrôles de conformité automatisés
- ✅ Connexion au Concentrateur de Données
- ✅ Interopérabilité avec toutes les autres PDP
- ✅ Hébergement sécurisé 
- ✅ Authentification sécurisée
- ✅ Certification ISO 27001
- ✅ Extraction et transmission des données e-reporting
- ✅ Gestion de l'annuaire central

### Fonctionnalités avancées (roadmap)

- 🔄 Intégration EDI multi-formats
- 📊 Tableaux de bord et reporting avancés
- 🔌 API ouvertes pour intégrations tierces
- 🌐 Support multi-entités et multi-devises
- 🤖 Automatisations et workflows personnalisables

## 🏗️ Architecture technique

_Section en cours de définition par la communauté_

### Stack technologique (proposition initiale)

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


## 🏗️ Sous-projets

Le présent projet est [un monorepo](https://en.wikipedia.org/wiki/Monorepo).
Les sous-projets sont dans le répertoire `/packages`:

* [packages/pac-bdd](packages/pac-bdd/README.md) permets d'exécuter les tests BDD.
* [packages/pac0](packages/pac0/README.md) est l'implémentation de référence.


## 🧪 Exécution des tests

Pour exécuter tous les tests et générer des rapports:

```bash
./script/test
```

Cette commande exécute pytest dans les deux packages (`pac0` et `pac-bdd`) et génère des rapports dans le dossier `/report`:

| Package | Rapport MD |Rapport HTML | Rapport JUnit XML |
|---------|--------------|--------------|-------------------|
| pac0 | [report.md](report/pac0/report.md) | [report.html](report/pac0/report.html) | [report/pac0/report.xml](report/pac0/report.xml) |
| pac-bdd | [report.md](report/pac-bdd/report.md)| [report.html](report/pac-bdd/report.html) | [report/pac-bdd/report.xml](report/pac-bdd/report.xml) |

Pour exécuter les tests d'un seul package:

```bash
# Tests pac0
cd packages/pac0 && uv run pytest

# Tests pac-bdd
cd packages/pac-bdd && uv run pytest
```


## 🤝 Contribution

Nous recherchons activement des contributeurs de tous horizons !

### Profils recherchés

- **Développeurs** (backend, frontend, DevOps)
- **Architectes** techniques
- **Experts** en facturation électronique et EDI
- **Juristes** et spécialistes conformité
- **Chefs de projet** et product owners
- **Testeurs** QA
- **Designers** UX/UI
- **Rédacteurs** techniques

### Comment contribuer ?

1. **Consultez les issues** pour identifier les tâches en cours
2. **Rejoignez les groupes de travail** sur le forum https://forum.pdplibre.org/
3. **Proposez des améliorations** via pull requests
4. **Participez aux discussions** communautaires https://forum.pdplibre.org/
5. **Partagez votre expertise** et vos retours d'expérience


## 🏛️ Gouvernance

_Section en cours de structuration_

Le projet est piloté de manière collaborative par la communauté selon des principes de :

- **Transparence** : Toutes les décisions sont publiques et documentées
- **Démocratie** : Participation de tous aux décisions majeures
- **Méritocratie** : Valorisation des contributions effectives

## 📞 Contact et communication

- **Forum communautaire** : https://forum.pdplibre.org/
- **Chat** : [Lien à définir]
- **Email** : [À définir]
- **Réunions** : Visioconférences bimensuelles : https://visio.octopuce.fr/b/phi-bgv-jnr-laa

## ⚖️ Licence

_Licence en cours de définition par la communauté_

Le code source sera publié sous une licence open source garantissant :

- La liberté d'utilisation
- La liberté de modification
- La liberté de distribution
- La protection contre l'appropriation commerciale

## 🙏 Remerciements

Ce projet est porté par une communauté engagée d'entrepreneurs, développeurs, juristes, experts métiers et citoyens convaincus qu'une alternative collective et transparente est possible.

Merci à tous les contributeurs qui rendent ce projet possible !
