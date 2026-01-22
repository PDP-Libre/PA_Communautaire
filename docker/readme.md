# PAC0 Services - Docker Infrastructure

Ce dépôt contient la configuration Docker Compose pour orchestrer les 9 services du projet **PA_Communautaire** via l'outil CLI `pac0-cli`.

## 📌 Architecture de la Solution

L'infrastructure est composée de 9 conteneurs basés sur l'image `astral/uv:python3.12-bookworm-slim`. Chaque conteneur exécute un service spécifique défini dans la liste `services` du fichier `run.py` :

* **01-api-gateway** : Point d'entrée FastAPI exposé sur le port 8000.
* **02-esb-central** : Serveur de messages NATS (`nats-server -V -js`).
* **03 à 09** : Services de traitement (FastStream) gérant le contrôle, la validation, le routage et le cycle de vie.



## ⚙️ Points Clés de Configuration

### 1. Gestion des Dépendances et Sources
Chaque conteneur utilise l'outil `uvx` pour lancer `pac0-cli`. Au démarrage, le script `setup.py` effectue les opérations suivantes :
* **Installation des outils** : Vérifie et installe les outils nécessaires comme `git` ou `nats-server`.
* **Clonage/Mise à jour** : Clone le dépôt GitHub `PA_Communautaire` ou effectue un `git pull` s'il est déjà présent.
* **Synchronisation** : Exécute `uv sync --all-packages` pour garantir que l'environnement Python est à jour.

### 2. Optimisation via Volumes
Un volume nommé `uv_cache` est partagé entre tous les services. Cela permet de :
* Persister les téléchargements de bibliothèques Python.
* Éviter que chaque service ne réinstalle intégralement ses dépendances à chaque redémarrage.

### 3. Ordonnancement
Le service `02-esb-central` est le pivot de l'infrastructure. Tous les autres services dépendent de lui (`depends_on`) car ils nécessitent que le bus NATS soit actif pour fonctionner.

## 🚀 Utilisation

### Démarrage global
Pour lancer l'ensemble de la stack en arrière-plan :
```bash
docker compose up -d
```


### Accès à l'API
Le service 01-api-gateway est accessible sur :

http://localhost:8000

### 🔄 Mise à jour
Code source : Le script setup.py détecte automatiquement si le répertoire contient un dépôt Git et exécute un git pull. Un simple docker compose restart permet donc de récupérer les dernières versions du code.

Nettoyage complet : Pour forcer une réinstallation complète (clonage et dépendances), supprimez les conteneurs et les volumes associés :



```Bash 
docker compose down -v
```