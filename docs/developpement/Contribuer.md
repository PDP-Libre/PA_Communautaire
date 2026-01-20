# 🚀 Contribuer à PA_Communautaire

Bienvenue ! Nous sommes ravis que vous envisagiez de contribuer au projet **PA_Communautaire**. Ce projet repose sur l'implication de sa communauté, et chaque contribution — petite ou grande — nous aide à construire un outil plus performant et ouvert.

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

1. **Consultez les issues** pour identifier les tâches en cours
2. **Rejoignez les groupes de travail** sur le forum https://forum.pdplibre.org/
3. **Proposez des améliorations** via pull requests
4. **Participez aux discussions** communautaires https://forum.pdplibre.org/
5. **Partagez votre expertise** et vos retours d'expérience

---

## Architecture du projet

- [Architecture et choix techniques](/docs/developpement/Architecture.md)

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

### 2. Clonage du dépôt

Le projet principal est hébergé sur GITHUB: https://github.com/PDP-Libre/PA_Communautaire

Pour participer au développement, vous devez utiliser la copie du projet hébergé sur Forgejo: https://git.pdplibre.org/

On utilise Foregejo pour profiter d'un dépot qui va automatiser certains process de livraisons et permet de respecter certaines contraintes légales : intégration continue, automatisation des tests ...

Le dépot Forgejo est synchronisé avec le projet principal chaque jour. En fait seulement la branche principale. 


* Pour accéder à Forgejo, demander une invitation à ....@....
* Ensuite créez votre propre copie (Fork) du projet:  
  ```git clone ...PA_Communautaire.git```
* mettez vous dans le bon dossier
```bash
cd PA_Communautaire
```

Nous allons trouver l'arborescence suivante : 

* /docs  
  les documentations diverses : métier et développeur
  * /docs/briques:  
  contient aussi de la doc métier et les tests BDD compréhensible pour tout le monde
* /packages  
  Les sources des applications  
  * pac-bdd  
  L'application qui fait tourner les tests BDD qui sont dans /docs/briques
  * pac0  
  Une application "proto" pour maquetter l'organisation en place.  
  Les choix d'architecture et de langage sont en cours de réflexions. 
* /report  
  ???
* /script  
  Diverses commandes a tout faire

Vous trouverez dans le document xxx les liens de téléchargement de la norme XXXX.


### 3. Configuration

#### 3.1 installation sous Linux
Testé sur Ubuntu 24.04

Nous allons installer les composants un par un. 

Après avoir cloné le projet en local et s'être placé dans le dossier **PA_Communautaire**.


##### Installation des dépendances PYTHON avec UV

Au lieu d'utiliser l'ancien gestionnaire de package PIP, on a préféré utiliser uv qui est plus rapide et plus complet. 

Sous ubuntu, préférer utiliser l'installation manuelle plutôt que la version SNAP.

La doc: [astral-sh/uv](https://github.com/astral-sh/uv)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
cd packages/pac-bdd
# on installe les packages définis dans pyproject.toml
uv sync

cd ../pac0
uv sync
```

##### Installation du broker de message NATS
NATS est un service optimisé pour recevoir, stocker et distribuer une grande quantité de message. Il est écrit en GO, facile a installer et performant. 

La doc: https://github.com/nats-io/nats-server

```bash
wget https://github.com/nats-io/nats-server/releases/download/v2.12.3/nats-server-v2.12.3-linux-amd64.tar.gz
tar -xzf nats-server-v2.12.3-linux-amd64.tar.gz
# important de mettre le binaire dans un dossier accessible dans le PATH
cd nats-server-v2.12.3-linux-amd64
cp nats-server ~/.local/bin/nats-server
chmod +x ~/.local/bin/nats-server
```

On peut aussi installer le client NATS pour voir ce qu'il se passe: 

```bash
NATS_CLI_VERSION=0.3.0
wget https://github.com/nats-io/natscli/releases/download/v${NATS_CLI_VERSION}/nats-${NATS_CLI_VERSION}-linux-amd64.zip
unzip nats-${NATS_CLI_VERSION}-linux-amd64.zip 
cd nats-${NATS_CLI_VERSION}-linux-amd64/
cp nats ~/.local/bin/nats
chmod +x ~/.local/bin/nats
````

Testons que nats accepte des messages : 

* dans un premier terminal, lancer le serveur:  
  ```bash
  nats-server  
  ```
* dans un second terminal, regardons ce qu'il se passe:  
  ```bash
  nats subscribe demo
  ```
* dans un troisème terminal, essayons d'envoyer des messages: 
  ```bash
  nats publish demo "Hello world"
  ```

Dans le second terminal on doit avoir : 
```
15:09:08 Subscribing on demo 
[#1] Received on "demo"
Hello world
```

NATS est maintenant en place. On peut arrêter le serveur avec CTRL+C, il sera lancé automatiquement plus tard. 

##### Serveur d'API fastAPI

Après s'être placé dans le dossier **PA_Communautaire**.

```bash
cd packages/pac0
uv run fastapi dev src/pac0/service/api_gateway/main.py
```

L'application devrait maintenant être accessible sur http://localhost:8080/docs


#### 3.2 installation avec Docker

EN COURS DE REDACTION

Utilisez Docker pour monter l'infrastructure complète :

```Bash
cd conf/docker
docker compose -f docker-compose.yml up -d
```

Une fois les conteneurs actifs, l'application devrait maintenant être accessible sur http://localhost:xxxx.

## Tester

Voir cet article : "Comment rédiger un test BDD ?"

Pour lancer les tests et vérifier que tout marche bien : 

```bash
cd PA_Communautaire/packages/pac-bdd
uv run pytest -v
```

Si on veut lancer un test seulement sur une partie du projet : 

```bash
uv run pytest -v test_scenario.py
```

## 🚦 Cycle de contribution
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

## Pour en savoir plus
* Comment rédiger un test BDD ?
* Comment programmer un test BDD ?

## 💬 Contact & Communauté
Si vous avez des questions ou si vous bloquez sur l'installation :

* Ouvrez une Issue pour signaler un problème ou poser une question.  
  Adresse: https://github.com/PDP-Libre/PA_Communautaire/issues
* Rejoignez notre forum de discussion  
  https://forum.pdplibre.org/

Merci de contribuer à rendre PA_Communautaire meilleur !