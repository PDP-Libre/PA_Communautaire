# Utilisation de Forgejo pour le build

Ce document décrit l'organisation du projet **PA_Communautaire** dans Forgejo : gestion des issues, décomposition Epic → User Story → tâches, démarche BDD, et automatisation CI.

---

## 1. Hiérarchie des issues

### Labels

Forgejo n'a pas de champs typés comme Jira. Toute la structuration passe par des labels à préfixes normalisés :

| Catégorie | Labels | Rôle |
|-----------|--------|------|
| Type | `type/epic`, `type/story`, `type/task`, `type/bug` | Nature de l'issue |
| Brique | `brique/01-api-gateway`, `brique/02-esb-central`, …, `brique/10-stockage` | Composant concerné |
| Priorité | `priority/high`, `priority/medium`, `priority/low` | Urgence |
| Statut | `status/blocked`, `status/needs-review`, `status/ready` | État courant |
| Profil | `contributor/dev`, `contributor/expert-metier` | Public cible |

### Epic → User Story → Tâches

```
Epic (label type/epic)
 └── User Story (label type/story)
      ├── Tâche implémentation (label type/task)
      ├── Tâche implémentation (label type/task)
      └── Scénarios BDD : rédigés DANS la User Story
```

---

## 2. Epic

Une Epic est une issue Forgejo standard avec le label `type/epic`. Elle agrège des User Stories via une task list :

```markdown
## Epic : Conformité EN 16931 pour la validation métier

Objectif : couvrir les règles de validation de la norme XP Z12-012
pour la brique 04-validation-metier.

### User Stories

- [ ] #42 US: Valider la structure XML CII d'une facture
- [ ] #43 US: Vérifier les règles de calcul des montants
- [ ] #44 US: Contrôler la conformité des identifiants SIRET/SIREN
- [ ] #45 US: Rejeter une facture avec champs obligatoires manquants
```

Forgejo affiche automatiquement la progression (`2/4`). Chaque `#xx` est un lien cliquable vers la User Story.

---

## 3. User Story avec scénarios BDD

### Template d'issue

Fichier `.gitea/ISSUE_TEMPLATE/user-story.yaml` :

```yaml
name: User Story
about: User Story avec critères d'acceptance BDD (Gherkin)
labels:
  - type/story
body:
  - type: input
    id: epic
    attributes:
      label: Epic parente
      placeholder: "#numéro de l'epic"

  - type: textarea
    id: story
    attributes:
      label: Story
      placeholder: "En tant que ... je veux ... afin de ..."
    validations:
      required: true

  - type: dropdown
    id: brique
    attributes:
      label: Brique
      options:
        - 01-api-gateway
        - 02-esb-central
        - 03-controle-formats
        - 04-validation-metier
        - 05-conversion-formats
        - 06-annuaire-local
        - 07-routage
        - 08-transmission-fiscale
        - 09-gestion-cycle-vie
        - 10-stockage
    validations:
      required: true

  - type: textarea
    id: scenarios
    attributes:
      label: Scénarios BDD (Gherkin)
      render: gherkin
      value: |
        # language: fr
        Fonctionnalité: [titre]

        Scénario: cas nominal
          Soit ...
          Quand ...
          Alors ...

        Scénario: cas d'erreur
          Soit ...
          Quand ...
          Alors ...

  - type: textarea
    id: tasks
    attributes:
      label: Décomposition technique
      value: |
        - [ ] ...
        - [ ] ...

  - type: dropdown
    id: complexity
    attributes:
      label: Complexité
      options:
        - XS
        - S
        - M
        - L
        - XL
```

### Exemple concret

```markdown
**Story** : En tant qu'émetteur de facture, je veux que le système
rejette une facture CII dont le montant TTC est incohérent avec
les lignes, afin de garantir la conformité EN 16931.

**Brique** : 04-validation-metier

**Scénarios BDD :**

# language: fr
Fonctionnalité: Validation des montants

Scénario: Montant TTC cohérent
  Soit une facture CII avec 2 lignes à 100€ HT chacune
  Et un taux de TVA de 20%
  Quand je soumets la facture à la validation métier
  Alors la facture est acceptée
  Et le statut de traitement est "validé"

Scénario: Montant TTC incohérent
  Soit une facture CII avec un montant TTC de 999€
  Et des lignes totalisant 200€ HT à 20% de TVA
  Quand je soumets la facture à la validation métier
  Alors la facture est rejetée
  Et le motif de rejet contient "BR-CO-15"

**Décomposition technique :**

- [ ] #60 Implémenter la règle BR-CO-15 dans validation_metier/main.py
- [ ] #61 Ajouter les steps BDD dans pac_bdd/api.py
- [ ] #62 Créer compliance_montants.feature dans docs/briques/04-validation-metier/
```

---

## 4. Où vivent les scénarios BDD

Le projet adopte une séparation claire entre contrat métier et code exécutable :

| Emplacement | Rôle | Modifié par |
|-------------|------|-------------|
| **Issue Forgejo** (User Story) | Rédaction et discussion des scénarios avant implémentation. C'est le contrat entre expert métier et développeur. | Expert métier + dev |
| `docs/briques/<NN-nom>/*.feature` | Source of truth exécutable. Les fichiers `.feature` font partie de la documentation fonctionnelle. | Expert métier (Gherkin) |
| `packages/pac-bdd/src/pac_bdd/*.py` | Step definitions Python qui implémentent les steps Gherkin. | Développeur |
| `packages/pac0/src/pac0/shared/test/` | Fixtures partagées (WorldContext, PacServiceContext, mocks). | Développeur |

### Flux de bout en bout

```
Issue US (Gherkin discuté)
    │
    ▼
docs/briques/04-validation-metier/compliance_montants.feature
    │
    ▼
packages/pac-bdd/test_scenario.py          ← découverte auto (glob **/*.feature)
    │
    ▼
packages/pac-bdd/src/pac_bdd/steps.py      ← import central
    ├── api.py                              ← steps REST
    ├── service.py                          ← steps services
    └── ...
    │
    ▼
packages/pac0/src/pac0/service/validation_metier/main.py   ← SUT
```

### Règle de contribution

Une PR liée à une User Story **doit** contenir :

1. Le fichier `.feature` dans `docs/briques/<brique>/` (ou sa modification)
2. Les step definitions dans `packages/pac-bdd/src/pac_bdd/`
3. L'implémentation dans `packages/pac0/src/pac0/service/<brique>/`

Le reviewer vérifie la cohérence entre les scénarios de l'issue et le `.feature` livré.

---

## 5. Project Board Kanban

Colonnes recommandées :

```
Backlog → Refinement → Ready → In Progress → Review → Done
```

| Colonne | Critère d'entrée | Critère de sortie |
|---------|-------------------|-------------------|
| **Backlog** | Issue créée avec label `type/story` | — |
| **Refinement** | Story en cours de rédaction des scénarios Gherkin | Scénarios validés par l'équipe (expert métier + dev) |
| **Ready** | Scénarios figés, tâches décomposées, milestone assigné | Un dev prend la story |
| **In Progress** | Branche créée, dev en cours | PR ouverte |
| **Review** | PR ouverte, tests CI passent | PR approuvée et mergée |
| **Done** | PR mergée, tous les scénarios passent en CI | — |

**Definition of Ready** : pas de scénarios Gherkin acceptés = la story ne quitte pas Refinement.

**Definition of Done** : tous les scénarios du `.feature` passent en CI + PR mergée.

---

## 6. Milestones

Les milestones remplacent les Fix Versions / Sprints Jira. Utilisation recommandée :

- Un milestone par **release** (ex: `v0.2.0 - Couverture briques 05-06`)
- Chaque User Story est assignée à un milestone
- La date cible du milestone correspond à la date de release prévue
- Forgejo affiche le pourcentage de complétion (issues fermées / total)

---

## 7. Automatisation CI (Forgejo Actions)

### 7.1 Déclenchement des tests

Le couplage `docs/` ↔ `packages/` impose de déclencher les tests BDD dès qu'un fichier pertinent change :

```yaml
# .forgejo/workflows/test-bdd.yaml
name: Tests BDD
on:
  push:
    paths:
      - 'docs/briques/**/*.feature'
      - 'packages/pac0/**'
      - 'packages/pac-bdd/**'
      - 'docker/Dockerfile.bdd'
  pull_request:
    paths:
      - 'docs/briques/**/*.feature'
      - 'packages/pac0/**'
      - 'packages/pac-bdd/**'

jobs:
  test-bdd:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Run BDD tests
        run: |
          cd packages/pac-bdd
          uv sync
          uv run pytest test_scenario.py \
            --junitxml=../../report/pac-bdd/report.xml \
            --html=../../report/pac-bdd/report.html \
            --md-report --md-report-output=../../report/pac-bdd/report.md

      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: bdd-reports
          path: report/pac-bdd/
```

### 7.2 Tests unitaires pac0

```yaml
# .forgejo/workflows/test-unit.yaml
name: Tests unitaires pac0
on:
  push:
    paths:
      - 'packages/pac0/**'
  pull_request:
    paths:
      - 'packages/pac0/**'

jobs:
  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Run unit tests
        run: |
          cd packages/pac0
          uv sync
          uv run pytest tests/ \
            --junitxml=../../report/pac0/report.xml \
            --html=../../report/pac0/report.html

      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: unit-reports
          path: report/pac0/
```

### 7.3 Vérification de la présence de .feature dans les PR

```yaml
# .forgejo/workflows/check-feature.yaml
name: Vérification BDD
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  check-bdd-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Vérifier la présence de .feature
        run: |
          # Ne vérifie que les PR portant le label type/story
          CHANGED=$(git diff --name-only origin/main...HEAD)

          # Si du code service a changé, un .feature devrait aussi changer
          if echo "$CHANGED" | grep -q 'packages/pac0/src/pac0/service/'; then
            if echo "$CHANGED" | grep -q '\.feature'; then
              echo "✅ Fichiers .feature mis à jour"
            else
              echo "⚠️ Code service modifié sans mise à jour de .feature"
              echo "Si c'est un refactoring interne, ignorez cet avertissement."
            fi
          fi
```

### 7.4 Publication des rapports

Les rapports de tests doivent être publiés comme artefacts CI plutôt que commités dans `report/`. L'artefact `upload-artifact` ci-dessus les rend téléchargeables depuis l'interface Forgejo.

Pour aller plus loin, Forgejo supporte la publication de pages statiques — les rapports HTML peuvent être déployés sur Forgejo Pages pour un accès permanent.

---

## 8. Templates d'issues complémentaires

### Bug report

Fichier `.gitea/ISSUE_TEMPLATE/bug-report.yaml` :

```yaml
name: Bug Report
about: Signaler un dysfonctionnement
labels:
  - type/bug
body:
  - type: dropdown
    id: brique
    attributes:
      label: Brique concernée
      options:
        - 01-api-gateway
        - 02-esb-central
        - 03-controle-formats
        - 04-validation-metier
        - 05-conversion-formats
        - 06-annuaire-local
        - 07-routage
        - 08-transmission-fiscale
        - 09-gestion-cycle-vie
        - 10-stockage
    validations:
      required: true

  - type: textarea
    id: reproduce
    attributes:
      label: Étapes de reproduction
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Comportement attendu

  - type: textarea
    id: actual
    attributes:
      label: Comportement observé

  - type: textarea
    id: scenario
    attributes:
      label: Scénario BDD de non-régression (optionnel)
      render: gherkin
      placeholder: |
        # language: fr
        Scénario: ...
          Soit ...
          Quand ...
          Alors ...
```

### Tâche technique

Fichier `.gitea/ISSUE_TEMPLATE/task.yaml` :

```yaml
name: Tâche technique
about: Tâche d'implémentation, refactoring, infra
labels:
  - type/task
body:
  - type: input
    id: parent
    attributes:
      label: Issue parente (US ou Epic)
      placeholder: "#numéro"

  - type: textarea
    id: description
    attributes:
      label: Description
    validations:
      required: true

  - type: textarea
    id: acceptance
    attributes:
      label: Critères d'acceptance
      value: |
        - [ ] ...
        - [ ] ...
```

---

## 9. Migration des templates GitHub existants

Le repo contient actuellement des templates dans `.github/issue_template/`. Pour Forgejo :

1. Copier et adapter les templates dans `.gitea/ISSUE_TEMPLATE/` (format YAML identique à GitHub)
2. Adapter le PR template dans `.gitea/PULL_REQUEST_TEMPLATE.md`
3. Conserver les templates `.github/` tant que le miroir GitHub est actif

---

## 10. Couverture BDD — axes de travail

4 briques n'ont actuellement aucun `.feature` :

| Brique | Priorité | Action |
|--------|----------|--------|
| 05-conversion-formats | Haute | Scénarios de conversion CII ↔ UBL ↔ Factur-X |
| 06-annuaire-local | Haute | Scénarios de résolution d'identifiants (SIRET, PEPPOL) |
| 08-transmission-fiscale | Moyenne | Scénarios de transmission vers la DGFiP |
| 10-stockage | Moyenne | Scénarios CRUD SeaweedFS / archivage légal |

Ces briques nécessitent des Epics dédiées, décomposées en User Stories avec scénarios Gherkin, suivant le processus décrit dans ce document. Le label `contributor/expert-metier` permet d'identifier les issues accessibles aux experts métier pour la rédaction des `.feature`.

---

## 11. Récapitulatif du workflow

```
1. Créer l'Epic (type/epic) avec la liste des US
2. Créer chaque US (type/story) avec le template
3. Refinement : rédiger les scénarios Gherkin dans l'issue
4. Ready : scénarios validés → décomposer en tâches (type/task)
5. In Progress : branche feature/xxx, implémenter
   - .feature dans docs/briques/<brique>/
   - Steps dans packages/pac-bdd/src/pac_bdd/
   - Code dans packages/pac0/src/pac0/service/<brique>/
6. PR → CI lance les tests BDD + unitaires
7. Review → merge → Done
8. Quand toutes les US de l'Epic sont Done → fermer l'Epic
```
