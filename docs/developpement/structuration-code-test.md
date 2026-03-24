# Structuration du code et des tests - Synthèse pour Forgejo

Document destiné à un expert en structuration de dépôt pour formuler des recommandations
d'organisation dans Forgejo (branches, CI, labels, protections, workflows).

---

## 1. Vue d'ensemble du monorepo

```
PA_Communautaire/                  # Racine du monorepo
├── docker-compose.yml             # Orchestration complète (10 services + infra)
├── docker/                        # Dockerfiles par service + config
│   ├── Dockerfile.01-api-gateway
│   ├── Dockerfile.03-controle-formats
│   ├── Dockerfile.04-validation-metier
│   ├── Dockerfile.05-conversion-formats
│   ├── Dockerfile.06-annuaire-local
│   ├── Dockerfile.07-routage
│   ├── Dockerfile.08-transmission-fiscale
│   ├── Dockerfile.09-gestion-cycle-vie
│   ├── Dockerfile.bdd             # Image pour exécuter les tests BDD
│   ├── env                        # Variables d'environnement
│   ├── secret.example             # Template pour les secrets
│   └── seaweedfs-config.json
├── docs/                          # Documentation (détail section 3)
├── packages/                      # Code source (détail section 2)
├── report/                        # Rapports de tests générés
│   ├── pac0/report.{html,md,xml}
│   └── pac-bdd/report.{html,md,xml}
├── script/test                    # Script de lancement des tests avec rapports
├── CLAUDE.md                      # Instructions pour IA assistant
├── README.md
├── REUSE.toml                     # Conformité licences REUSE/SPDX
└── LICENSES/
```

---

## 2. Les 3 packages

### 2.1 `packages/pac0/` — Implémentation de référence

Contient les 9 microservices de la plateforme. Package Python géré par `uv`.

```
packages/pac0/
├── pyproject.toml                 # Dépendances : fastapi, faststream, nats-py, s3fs
├── src/pac0/
│   ├── service/
│   │   ├── api_gateway/           # Brique 01 - FastAPI (point d'entrée REST)
│   │   │   ├── main.py
│   │   │   └── lib/
│   │   │       ├── api.py         # Routes API
│   │   │       ├── bus.py         # Communication ESB
│   │   │       ├── common.py
│   │   │       └── trace.py       # Traçabilité
│   │   ├── controle_formats/      # Brique 03 - FastStream
│   │   │   └── main.py
│   │   ├── validation_metier/     # Brique 04 - FastStream
│   │   │   └── main.py
│   │   ├── conversion_formats/    # Brique 05 - FastStream
│   │   │   └── main.py
│   │   ├── annuaire_local/        # Brique 06 - FastStream
│   │   │   └── main.py
│   │   ├── routage/               # Brique 07 - FastStream
│   │   │   ├── main.py
│   │   │   ├── lib.py
│   │   │   ├── models.py
│   │   │   └── peppol.py
│   │   ├── transmission_fiscale/  # Brique 08 - FastStream
│   │   │   └── main.py
│   │   ├── gestion_cycle_vie/     # Brique 09 - FastStream
│   │   │   └── main.py
│   │   └── peppol_dns_fake/       # Service utilitaire de test (mock DNS PEPPOL)
│   │       └── main.py
│   └── shared/
│       ├── esb.py                 # Utilitaires ESB partagés
│       ├── peppol.py              # Utilitaires PEPPOL partagés
│       ├── test/                  # Fixtures de test partagées (voir section 4)
│       │   ├── world.py           # WorldContext (environnement multi-PA)
│       │   └── service/
│       │       ├── base.py
│       │       ├── dns.py
│       │       ├── fastapi.py
│       │       ├── faststream.py
│       │       ├── group.py
│       │       ├── nats.py
│       │       ├── pac.py         # PacServiceContext
│       │       └── seaweedfs.py
│       └── tools/
│           └── api.py
├── tests/                         # Tests unitaires / intégration du package
│   ├── test_asyncio.py
│   ├── test_faststream.py
│   ├── test_fixture.py
│   ├── test_nats.py
│   ├── test_s3fs.py
│   ├── test_service_lifecycle.py
│   ├── test_test.py
│   └── test_world.py
└── deploy/
    ├── docker/README.md
    └── k8s/                       # Manifestes Kubernetes (10 briques + ingress)
        ├── deploy_01-api-gateway.yaml
        ├── ...
        └── serviceaccount.yaml
```

**Point clé** : la brique 02 (ESB Central) n'a pas de code applicatif propre — c'est NATS server, déployé tel quel.

### 2.2 `packages/pac-bdd/` — Moteur de tests BDD

Exécute les scénarios Gherkin `.feature` situés dans `docs/briques/`. Dépend de `pac0` via un workspace uv.

```
packages/pac-bdd/
├── pyproject.toml                 # Dépendances : pytest-bdd, pytest-asyncio, pac0
├── test_scenario.py               # Point d'entrée : charge TOUS les .feature du repo
├── test_fixture.py                # Tests des fixtures
├── test_openapi.py                # Tests de conformité OpenAPI/Swagger
├── test_pac0.py                   # Tests d'intégration pac0
└── src/pac_bdd/
    ├── steps.py                   # Import central de tous les modules de steps
    ├── api.py                     # Steps : appels REST API
    ├── peppol.py                  # Steps : routage PEPPOL
    ├── service.py                 # Steps : services et lifecycle
    ├── esb.py                     # Steps : bus de messages NATS
    ├── user.py                    # Steps : contexte utilisateur
    ├── world_steps.py             # Steps : setup du monde de test
    ├── demo.py                    # Steps : démonstration/tutoriel
    └── tobeimplemented.py         # Steps en attente d'implémentation (pytest.skip)
```

**Mécanisme de découverte** : `test_scenario.py` scanne `../../**/*.feature` (récursif depuis la racine) et enregistre chaque fichier `.feature` trouvé via `scenarios()`.

### 2.3 `packages/pac0-cli/` — CLI utilitaire

Outil CLI pour installer les dépendances et lancer les services.

```
packages/pac0-cli/
├── pyproject.toml
└── src/pac0/cli/
    ├── main.py
    ├── command/
    │   ├── run.py                 # Lancement des services
    │   ├── setup.py               # Installation des outils (nats-server, etc.)
    │   ├── test.py                # Lancement des tests
    │   └── console/app.py
    └── lib/
        ├── conf.py
        └── setup.py
```

Utilisable via `uvx pac0-cli@latest run <N>` (N = numéro de brique).

---

## 3. Documentation

```
docs/
├── 00_onboarding/                 # Parcours d'onboarding (scenario.md + slides)
├── briques/                       # Documentation fonctionnelle + tests BDD par brique
│   ├── README.md
│   ├── 01-api-gateway/
│   │   ├── README.md              # Specs de la brique (routes API, normes)
│   │   ├── healthcheck.feature    # Scénarios BDD
│   │   ├── service.feature
│   │   ├── sha256.feature
│   │   └── trackingId.feature
│   ├── 02-esb-central/
│   │   ├── README.md
│   │   ├── esb.feature
│   │   ├── healthcheck.feature
│   │   ├── service.feature
│   │   ├── service_lifecycle.feature
│   │   └── world.feature
│   ├── 03-controle-formats/
│   │   ├── README.md
│   │   ├── format.feature
│   │   └── service.feature
│   ├── 04-validation-metier/
│   │   ├── README.md
│   │   ├── compliance.feature
│   │   └── todo.md
│   ├── 05-conversion-formats/
│   │   └── README.md              # Pas de .feature (à couvrir)
│   ├── 06-annuaire-local/
│   │   └── README.md              # Pas de .feature (à couvrir)
│   ├── 07-routage/
│   │   ├── README.md
│   │   ├── peppol.feature
│   │   ├── peppol_live.feature
│   │   ├── pa_multiple.feature
│   │   └── peppol.md
│   ├── 08-transmission-fiscale/
│   │   └── README.md              # Pas de .feature (à couvrir)
│   ├── 09-gestion-cycle-vie/
│   │   ├── README.md
│   │   ├── demo.feature
│   │   ├── facture.feature
│   │   └── workflow.feature
│   └── 10-stockage/
│       └── README.md              # Pas de .feature (à couvrir)
├── developpement/
│   ├── Architecture.md
│   ├── BDD_README.md              # Point d'entrée doc tests
│   ├── BDD_Guide_Expert_Metier.md # Guide rédaction Gherkin
│   ├── BDD_Guide_Developpeur.md   # Guide implémentation steps
│   ├── Contribuer.md              # Workflow de contribution
│   ├── Configuration.md
│   ├── Installation_Docker.md
│   ├── Installation_Linux.md
│   ├── cli.md
│   └── TODO_docs.md
├── norme/                         # Normes AFNOR et annexes
│   ├── index.md
│   ├── XP_Z12-012.pdf
│   ├── XP_Z12-013.pdf
│   ├── XP_Z12-014.pdf
│   ├── XP_Z12-012_Annexes.../     # Excel règles métier + exemples XML
│   ├── XP_Z12-013_SWAGGER_.../    # Swagger JSON (Flow + Directory)
│   ├── XP_Z12-014_CAS_USAGE.../   # Cas d'usage UC1-UC5 + exemples
│   └── CDAR_D22B/                 # Schémas XSD accusés de réception
├── test/                          # Exemples BDD commentés (tutoriel)
│   ├── index.md
│   ├── demo_test.feature
│   └── demo_test_comment.feature
└── IA/
    └── politique-utilisation-ia.md
```

---

## 4. Architecture des tests

### 4.1 Deux suites de tests indépendantes

| Suite | Package | Commande | Quoi |
|-------|---------|----------|------|
| Tests unitaires/intégration | `packages/pac0` | `cd packages/pac0 && uv run pytest` | Tests techniques des services, fixtures, NATS, S3 |
| Tests BDD (comportement) | `packages/pac-bdd` | `cd packages/pac-bdd && uv run pytest` | Scénarios Gherkin de `docs/briques/` + `docs/test/` |

Les deux sont lancés par `./script/test` qui génère les rapports dans `report/`.

### 4.2 Flux d'un test BDD

```
docs/briques/<NN-nom>/*.feature       Scénarios Gherkin (écrits par le métier)
        │
        ▼
packages/pac-bdd/test_scenario.py     Découverte automatique (glob **/*.feature)
        │
        ▼
packages/pac-bdd/src/pac_bdd/steps.py Import central des step definitions
        │
        ├── api.py                    Steps REST API
        ├── peppol.py                 Steps PEPPOL/routage
        ├── service.py                Steps services
        ├── esb.py                    Steps bus de messages
        ├── user.py                   Steps contexte utilisateur
        ├── world_steps.py            Steps setup monde
        └── tobeimplemented.py        Steps non implémentés (pytest.skip)
                │
                ▼
packages/pac0/src/pac0/shared/test/   Fixtures partagées
        ├── world.py                  WorldContext (multi-PA, mock DNS PEPPOL)
        └── service/
            ├── pac.py                PacServiceContext (9 services)
            ├── nats.py               NatsServiceContext
            ├── fastapi.py            FastAPI test client
            ├── faststream.py         FastStream test broker
            └── seaweedfs.py          S3 mock
                │
                ▼
packages/pac0/src/pac0/service/       Système sous test (les 9 services)
```

### 4.3 Couverture BDD par brique

| Brique | .feature existants | Nb scénarios (approx) |
|--------|-------------------|-----------------------|
| 01 - API Gateway | healthcheck, service, sha256, trackingId | 4 fichiers |
| 02 - ESB Central | esb, healthcheck, service, service_lifecycle, world | 5 fichiers |
| 03 - Contrôle Formats | format, service | 2 fichiers |
| 04 - Validation Métier | compliance | 1 fichier |
| 05 - Conversion Formats | *(aucun)* | 0 |
| 06 - Annuaire Local | *(aucun)* | 0 |
| 07 - Routage | peppol, peppol_live, pa_multiple | 3 fichiers |
| 08 - Transmission Fiscale | *(aucun)* | 0 |
| 09 - Gestion Cycle de Vie | demo, facture, workflow | 3 fichiers |
| 10 - Stockage | *(aucun)* | 0 |

Total : **18 fichiers .feature** dans `docs/briques/` + 2 dans `docs/test/` (tutoriel).

### 4.4 Tests unitaires pac0

8 fichiers dans `packages/pac0/tests/` :

| Fichier | Périmètre |
|---------|-----------|
| test_asyncio.py | Mécanismes async |
| test_faststream.py | Broker FastStream |
| test_fixture.py | Fixtures de test |
| test_nats.py | Connexion NATS |
| test_s3fs.py | Stockage S3 |
| test_service_lifecycle.py | Cycle de vie des services |
| test_test.py | Infrastructure de test |
| test_world.py | WorldContext multi-PA |

---

## 5. Relations entre code, doc et tests

```
docs/briques/01-api-gateway/
├── README.md                         ◄── Specs fonctionnelles (routes, normes)
├── healthcheck.feature               ◄── Tests BDD (comportement attendu)
└── ...

packages/pac0/src/pac0/service/
└── api_gateway/main.py               ◄── Implémentation du service

packages/pac-bdd/src/pac_bdd/
└── api.py                            ◄── Step definitions (code de test)
```

**Particularité importante** : les fichiers `.feature` (tests BDD) sont dans `docs/briques/` et non dans `packages/`. C'est un choix volontaire : les scénarios Gherkin font partie de la documentation fonctionnelle et sont rédigés par des experts métier qui ne touchent pas au code.

---

## 6. Stack technique

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| API | FastAPI | Brique 01 (REST, Swagger auto) |
| Microservices | FastStream | Briques 03-09 (consommateurs NATS) |
| Message broker | NATS (JetStream) | Brique 02 (orchestration) |
| Stockage fichiers | SeaweedFS (S3) | Brique 10 |
| Package manager | uv | Gestion dépendances Python |
| Tests BDD | pytest-bdd + Gherkin FR | Scénarios comportementaux |
| Tests unitaires | pytest + pytest-asyncio | Tests techniques |
| Conteneurisation | Docker / Podman | Déploiement |
| Orchestration prod | Kubernetes | Manifestes dans deploy/k8s/ |
| CI rapports | pytest-html, pytest-md-report | HTML + MD + JUnit XML |
| Licences | REUSE / SPDX | GPL-3.0-or-later |

---

## 7. Dépôts et workflow actuel

- **Forgejo** (développement) : https://git.pdplibre.org/Construction_PA/PA_Communautaire
- **GitHub** (releases) : https://github.com/PDP-Libre/PA_Communautaire
- **Forum** : https://forum.pdplibre.org/

Workflow actuel :
1. Fork sur Forgejo
2. Branche thématique (`feature/...`, `fix/...`, `chore/...`)
3. PR toujours liée à une Issue (préfixe WIP tant qu'en cours)
4. Tests avant merge
5. Synchronisation Forgejo → GitHub aux releases

Templates existants :
- `.github/issue_template/1_Bug_report.yaml`
- `.github/issue_template/2_Feature_request.yaml`
- `.github/PULL_REQUEST_TEMPLATE.md`

---

## 8. Points d'attention pour la structuration Forgejo

### Couplage doc/test/code
Les `.feature` sont dans `docs/` mais exécutés par `packages/pac-bdd/`. Une modification d'un `.feature` peut casser un test sans toucher au code. Inversement, une modification de code peut casser un `.feature` existant. La CI doit déclencher les tests BDD dès qu'un `.feature` OU un fichier `packages/pac0/` OU un fichier `packages/pac-bdd/` change.

### Deux profils de contributeurs
- **Développeurs** : modifient `packages/` et `docker/`
- **Experts métier** : modifient uniquement `docs/briques/**/*.feature` et `docs/briques/**/README.md`

Les experts métier doivent pouvoir contribuer (PR sur `.feature`) sans avoir à comprendre le code Python.

### Workspace uv
`pac-bdd` dépend de `pac0` en tant que workspace member. Les deux packages partagent un même virtualenv lors de l'exécution des tests. Le `uv.lock` de `pac-bdd` est le fichier de référence pour la résolution de dépendances.

### Rapports de tests
Le script `./script/test` génère des rapports dans `report/`. Ces rapports sont commités dans le repo pour suivi historique. La CI devrait idéalement les publier comme artefacts plutôt que les commiter.

### Briques sans couverture
4 briques n'ont aucun test BDD (05, 06, 08, 10). C'est un axe de travail prioritaire pour les experts métier.
