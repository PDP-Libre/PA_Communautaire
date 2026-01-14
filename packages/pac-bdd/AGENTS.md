# AGENTS.md

## Documentation des Agents - Projet pac-bdd

Ce fichier contient les informations essentielles pour le développement et la maintenance du projet pac-bdd.

### 🚀 Commandes Principales

```bash
# Exécution des tests BDD
uv run pytest

# Mode verbeux pour débogage
uv run pytest -v

# Script principal du projet
uv run pac-bdd
```

### 📋 Contexte Technique

- **Langage** : Python 3.13+
- **Framework de test** : pytest avec extensions BDD
- **Architecture** : Behavior Driven Development (BDD) avec Gherkin en français
- **Tests asynchrones** : pytest-asyncio
- **Gestionnaire de paquets** : uv (moderne, remplace pip/poetry)

### 🧪 Structure des Tests

**Fichiers principaux** :
- `src/pac_bdd/world_steps.py` - Steps BDD principaux (639 lignes)
- `src/pac_bdd/pac0_fixture.py` - Fixtures pour tests NATS/FastStream
- `test_*.py` - Fichiers de test racine

**Scénarios BDD** :
- Fichiers `.feature` contenant les scénarios en français
- Pattern Given/When/Then implémenté dans `world_steps.py`
- Support multi-PA (Prestataires d'Accès)

### 🔧 Services Testés

1. **NATS** - Système de messagerie asynchrone
   - Tests de démarrage/arrêt
   - Configuration des endpoints
   - Healthchecks

2. **Peppol** - Infrastructure d'échange de documents électroniques
   - Lookup par SIREN
   - Mode mock pour les tests

3. **Services pac0** - Framework principal
   - FastAPI endpoints
   - FastStream consumers
   - Communication inter-PA

### 📊 Types de Tests Disponibles

- **Démarrage/arrêt des services** - Cycle de vie
- **Configuration** - Endpoints et paramètres
- **Communication** - Routage entre PA
- **Lookup** - Recherche d'entreprises Peppol
- **Cycle de vie factures** - Dépôt et traitement

### ⚠️ Points d'Attention

**Outils manquants à configurer** :
- Linting (ruff/pylint/flake8)
- Formateur de code (black)
- Tri des imports (isort)
- Type checking (mypy)
- Pré-commit hooks

**Dépendances workspace** :
- Projet dépend de `pac0` (workspace local)
- Structure monorepo avec `../pac0`

### 📝 Bonnes Pratiques

1. **Avant de committer** :
   - Exécutez `uv run pytest` pour valider les tests
   - Vérifiez que les scénarios BDD passent
   - Testez les modifications avec différents contextes PA

2. **Ajout de nouveaux tests** :
   - Créez d'abord le fichier `.feature` avec le scénario
   - Implémentez les steps dans `world_steps.py`
   - Utilisez les fixtures existantes de `pac0_fixture.py`

3. **Débogage** :
   - Utilisez `pytest -v` pour plus de détails
   - Les logs sont disponibles via les fixtures
   - Mode mock disponible pour Peppol

4. **Documentation** :
   - Les scénarios BDD servent de documentation vivante
   - Maintenez les descriptions Gherkin claires et en français
   - Documentez les nouvelles fixtures si nécessaire

### 🔍 Commandes de Développement

```bash
# Lancer NATS localement pour les tests
nats-server

# Découvrir les tests disponibles
uv run pytest --collect-only

# Exécuter un test spécifique
uv run pytest test_scenario.py::test_world -v

# Nettoyer le cache pytest
uv run pytest --cache-clear
```

### 📚 Références

- **pytest-bdd** : Framework BDD pour pytest
- **FastStream** : Framework de messagerie asynchrone
- **Peppol** : Infrastructure européenne d'échange de documents
- **SPDX** : Headers de licence utilisés (GPL-3.0-or-later)