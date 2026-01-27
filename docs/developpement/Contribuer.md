# 🚀 Contribuer à PA_Communautaire

Bienvenue ! Nous sommes ravis que vous envisagiez de contribuer au projet **PA_Communautaire**.  
Ce projet repose sur l'implication de sa communauté, et chaque contribution — petite ou grande — nous aide à construire un outil plus performant et ouvert.

---

## 🌟 Pourquoi nous rejoindre ?

Rejoindre ce projet, c'est participer à une initiative **Open Source** concrète. Que vous souhaitiez corriger un bug, proposer une nouvelle fonctionnalité ou améliorer la documentation, votre aide est la bienvenue.

### 🛠️ Compétences recherchées
Le projet évolue et nous avons besoin de profils variés :

- **Développeurs** (backend, frontend, DevOps)
- **Architectes** techniques
- **Experts** en facturation électronique et EDI
- **Juristes** et spécialistes conformité
- **Chefs de projet** et product owners
- **Testeurs** QA
- **Designers** UX/UI
- **Rédacteurs** techniques

> **Débutant ?** Ne soyez pas intimidé ! Nous accueillons avec plaisir les développeurs juniors. Cherchez les issues avec le label `good first issue` pour commencer.

### Comment contribuer ?

1. **[Consultez les tickets](https://git.pdplibre.org/Construction_PA/PA_Communautaire/issues)** pour identifier les tâches en cours
2. **[Rejoignez les groupes de travail](https://forum.pdplibre.org/)** sur le forum https://forum.pdplibre.org/
3. **Proposez des améliorations** via pull requests
4. **[Participez aux discussions](https://forum.pdplibre.org/)** communautaires

---

## Architecture du projet

- [Architecture et choix techniques](Architecture.md)

## 💻 Installation de l'environnement de développement

Suivez ces étapes pour mettre en place votre environnement local et commencer à contribuer en quelques minutes.

Vous pouvez installer le projet en fonction de votre profil technique:  

* avec Docker  
  Version rapide qui fonctionne avec tous les OSs
* sous Linux avec chaque service  
  Cette version permet d'être dans une configuration la plus proche de la production et de comprendre tous les composants en place.
  
### 1. Prérequis

Avant de commencer, assurez-vous d'avoir installé :
* **Git** (pour versionner votre code)
* **Python**
* Eventuellement un bucket S3 pour stocker les factures en transit.  
  * vous pouvez utiliser un serveur S3 dans le cloud
  * ou utiliser le serveur local fourni dans la version Docker
  * ou utiliser le bucket S3 communautaire dédiés aux développeurs. (TODO adresse à définir)

  
### 2. Clonage du dépôt

Le projet principal est hébergé sur GITHUB: https://github.com/PDP-Libre/PA_Communautaire  
Ce dépot est utilisé pour publier les releases finales. Ne l'utilisez pas pour vos développements.

Pour participer au développement, vous devez utiliser la copie du projet hébergé sur Forgejo: https://git.pdplibre.org/

On utilise Foregejo pour profiter d'un dépot qui va automatiser certains process de livraisons et permet de respecter certaines contraintes légales qui sont floues coté Github : intégration continue, automatisation des tests, respects des licences ...

Le dépot Forgejo est synchronisé avec le projet principal à chaque livraison d'une release.


* Pour accéder à Forgejo, faites unde demande d'invitation sur le forum : [Forum PDPLibre/lancement projet](https://forum.pdplibre.org/t/lancement-du-projet-de-creation-de-notre-pa-communautaire/260)
* Ensuite créez votre propre copie (Fork) du projet:  
  ```git clone https://git.pdplibre.org/Construction_PA/PA_Communautaire.git```
* mettez vous dans le bon dossier
```bash
cd PA_Communautaire
```

* consultez [le document sur l'Architecture](Architecture.md) qui explique comment sont organisez les dossiers. 

### 3. Configuration

#### 3.1 installation avec Docker

Version recommandée pour démarrer rapidement avec tous les services en place et un serveur de stockage local.

Voir [Installation Docker](Installation_Docker.md)

#### 3.2 installation sous Linux

Voir [Installation Linux](Installation_Linux.md)

## Tester

- [Comment utiliser les tests ?](BDD_README.md)

## 🚦 Cycle de contribution

En cours de rédaction 

Pour garantir la qualité du code, merci de respecter ce flux :

* Forker le projet.
* Créer une branche thématique 
``` 
git checkout -b feature/ma-super-idee
```
* vérifiez les tests
```
cd packages/pac-bdd
uv run pytest -v
```
* Commiter vos changements avec des messages explicites.
```
git commit -m "Amélioration de la documentation"
```
* Pousser votre branche 
```
git push origin feature/ma-super-idee
```
* Ouvrir une Pull Request sur le dépôt principal en décrivant précisément vos modifications.
* Suivez les recommandations du modérateur.

---

## 💬 Contact & Communauté
Si vous avez des questions ou si vous bloquez sur l'installation :

* Ouvrez une Issue pour signaler un problème ou poser une question.  
  Adresse: https://github.com/PDP-Libre/PA_Communautaire/issues
* Rejoignez notre forum de discussion  
  https://forum.pdplibre.org/


Merci de contribuer à rendre PA_Communautaire meilleur !