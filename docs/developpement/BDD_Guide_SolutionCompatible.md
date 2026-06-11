<!--
SPDX-FileCopyrightText: 2026 PDP Libre

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Guide BDD — Logiciel Solution Compatible

> Public : experts métier, développeurs et agents qui poursuivent la couverture BDD des cas d'usage
> de la facturation électronique **du point de vue d'un Logiciel Solution Compatible**.
>
> Pré-requis : avoir lu [`BDD_Guide_Expert_Metier.md`](BDD_Guide_Expert_Metier.md) et
> [`BDD_Guide_Developpeur.md`](BDD_Guide_Developpeur.md).

## 1. Contexte et objectif

La plupart des tests BDD du dépôt (`docs/briques/`) testent une **brique** interne de la Plateforme
Agréée (PA). Ce guide décrit une autre famille de tests : ceux écrits du point de vue d'un
**Logiciel Solution Compatible** (SC) — un éditeur métier comme Dolibarr ou Factur-e — qui **pilote**
une PA via son API pour émettre et recevoir des factures.

Ces tests ont une **double vocation** :

1. Valider notre PA Communautaire une fois ses briques construites.
2. Valider une **PA tierce** déjà agréée, sans dépendre de son implémentation interne.

C'est aussi un point d'entrée pédagogique : on démarre la stratégie de test **avant** la construction
des briques, en partant de l'expérience utilisateur réelle (un éditeur qui envoie une facture et un
éditeur qui la reçoit).

## 2. Acteurs

| Acteur | Rôle | Outil |
|---|---|---|
| **VENDEUR** | Émet la facture | Logiciel Solution Compatible raccordé à sa **PA-E** (Plateforme Agréée Émettrice) |
| **ACHETEUR** | Reçoit la facture | Logiciel Solution Compatible raccordé à sa **PA-R** (Plateforme Agréée Réceptrice) |
| **PA-E / PA-R** | Plateformes Agréées | Posent les **statuts de transmission** |
| **CdD PPF** | Concentrateur de Données du Portail Public de Facturation | Reçoit les statuts obligatoires |

On instancie **deux** SC : un pour le VENDEUR (côté PA-E), un pour l'ACHETEUR (côté PA-R). Les tests
pilotent le SC du VENDEUR pour envoyer la facture, puis le SC de l'ACHETEUR pour vérifier la réception.

## 3. Les 7 étapes du cas nominal (XP Z12-014 §4.2)

| Étape | Nom | Acteur | Description |
|---|---|---|---|
| 1 | Création de la facture à destination de l'ACHETEUR | VENDEUR | Le VENDEUR crée la facture (flux 2) via son SI / SC et la transmet à sa PA-E. |
| 2 | Transmission du flux 1, de la facture et des statuts | PA-E | Après contrôles réglementaires, la PA-E transmet le flux 1 au CdD PPF, la facture à la PA-R, et pose le statut **Déposée** puis **Émise**. |
| 3 | Réception de la facture | PA-R | La PA-R reçoit la facture, pose les statuts **Reçue** puis **Mise à disposition**, et la met à disposition de l'ACHETEUR. |
| 4a / 4b | Traitement de la facture et statuts | ACHETEUR | L'ACHETEUR pose les statuts de traitement (**Prise en charge**, **Approuvée**, **Approuvée partiellement**, **En litige**, **Suspendue**…). |
| 4c | Réception des statuts | VENDEUR | Le VENDEUR réceptionne les statuts de traitement (peut poser **Complétée**). |
| 5a / 5b | Paiement et statut « Paiement transmis » | ACHETEUR / PA-R | L'ACHETEUR paie la facture et peut transmettre **Paiement transmis**. |
| 5c | Réception du statut « Paiement transmis » | VENDEUR / PA-E | Le VENDEUR reçoit **Paiement transmis**. |
| 6a / 6b | Encaissement et statut « Encaissée » | VENDEUR / PA-E | Si la TVA est exigible à l'encaissement, le VENDEUR pose **Encaissée** (transmis au CdD PPF et à la PA-R). |
| 6c | Réception du statut « Encaissée » | ACHETEUR / PA-R | L'ACHETEUR reçoit **Encaissée**. |
| 7 | Réception du statut « Encaissée » par le CdD PPF | CdD PPF | Le CdD PPF reçoit **Encaissée**. |

### Statuts de transmission vs statuts de traitement

- **Statuts de transmission** (posés par les PA) : *Déposée / Rejetée à l'émission*, *Émise*,
  *Reçue / Rejetée en réception*, *Mise à disposition*.
- **Statuts de traitement** (posés par les entreprises) : *Refusée*, *En litige*, *Suspendue*,
  *Complétée*, *Approuvée*, *Approuvée partiellement*, *Paiement transmis*, *Encaissée*.
- **4 statuts obligatoires** transmis au CdD PPF : **Déposée**, **Rejetée**, **Refusée**, **Encaissée**.

## 4. Où vivent les fichiers

```
packages/LogicielSolutionCompatible/
├── README.md
└── features/
    └── 01-echange_nominal.feature           # Cas nominal émission → réception

packages/pac-bdd/src/pac_bdd/
├── solution_compatible.py                   # Step definitions des scénarios SC
└── steps.py                                 # Importe solution_compatible (from .solution_compatible import *)
```

**Pourquoi cette répartition ?** Le runner `packages/pac-bdd/test_scenario.py` collecte
automatiquement **tout fichier `.feature` du dépôt** (`glob("../../**/*.feature")`). Les `.feature`
peuvent donc vivre dans `packages/LogicielSolutionCompatible/`, séparés des briques de la PA. En
revanche les step definitions ne sont chargées que via `from pac_bdd.steps import *` : elles vivent
donc dans `pac-bdd`, ce qui évite une dépendance circulaire `pac-bdd → LogicielSolutionCompatible`.

## 5. Conventions de rédaction

### Déclaratif et agnostique du canal

Décrire le **comportement métier**, jamais l'implémentation technique. Le pilotage réel d'un SC
pourra se faire via **Playwright** (IHM) ou via des **appels API** sur son backend — ce choix ne doit
**pas** transparaître dans le `.feature`.

```gherkin
# ✅ Déclaratif
Quand le VENDEUR envoie la facture "15" à son ACHETEUR depuis son Logiciel Solution Compatible

# ❌ Impératif / couplé à l'implémentation
Quand je fais un POST "/api/dolibarr/invoices/15/send" avec le token "..."
```

### Valeurs et statuts

- Variables entre guillemets : `"15"`, `"Déposée"`. On conserve la casse des statuts de la norme.
- Constantes (entités nommées partagées) préfixées `#` : `#pa1`, `#e1`, `#f1` (cf. `pa_multiple.feature`).
- Référencer la norme dans la description de la `Fonctionnalité` (ex. « Section 4.2 de XP Z12-014 v1.3 »).

### Spécification exécutable (pending)

Tant que la PA et un SC réel ne sont pas disponibles, les steps appellent `pytest.skip(...)` : les
scénarios sont **collectés et marqués SKIPPED**, jamais en `StepDefNotFound`. On tague les
fonctionnalités concernées `@wip`.

```python
import pytest
from pytest_bdd import when, parsers

_EN_ATTENTE = "En attente de la Plateforme Agréée et d'un Logiciel Solution Compatible réel"

@when(parsers.parse('le VENDEUR envoie la facture "{invoice}" ...'))
def _(invoice: str):
    pytest.skip(_EN_ATTENTE)
```

Quand la PA et le pilotage du SC seront disponibles, on remplacera le corps `pytest.skip(...)` par
l'appel réel (Playwright ou API) et on retirera le tag `@wip`.

### Exécuter les tests SC

```shell
cd packages/pac-bdd
uv run pytest -k echange_nominal -v          # le scénario apparaît en SKIPPED
uv run pytest -m "solution-compatible" -v    # tous les scénarios SC
```

## 6. État actuel (2026-06-10)

| Cas d'usage | Norme | Fichier | État |
|---|---|---|---|
| Échange nominal émission → réception | §4.2 (étapes 1-3) | `packages/LogicielSolutionCompatible/features/01-echange_nominal.feature` | ✅ Rédigé, `@wip` (pending) |

Statuts couverts : **Déposée → Émise → Reçue → Mise à disposition**.

## 7. Backlog — cas d'usage à couvrir

À traiter dans de prochains lots, en suivant la même méthode (un `.feature` par cas, steps déclaratifs,
pending jusqu'à disponibilité de la PA) :

| # | Cas d'usage | Norme | Idée de scénario |
|---|---|---|---|
| 1 | **Cycle de vie complet** (suite du nominal) | §4.2 (étapes 4-7) | Prise en charge → Approuvée → Paiement transmis → Encaissée, vérifiés côté VENDEUR et ACHETEUR |
| 2 | **Rejet à l'émission** | §4.2.2 | La PA-E détecte une erreur → statut « Rejetée » (code 213) avec motif ; annulation comptable côté VENDEUR |
| 3 | **Facture conforme NON_TRANSMISE** (absence de PA-R) | §4.2.3 | Destinataire sans PA active → « Déposée » avec MOTIF « NON_TRANSMISE » ; transmission d'un Duplicata |
| 4 | **Rejet en réception** | §4.2.4 | La PA-R détecte une erreur → « Rejetée » (code 213) transmise au VENDEUR |
| 5 | **Refus par l'ACHETEUR** | §4.2.5 | L'ACHETEUR pose « Refusée » avec un motif de la liste (XP Z12-012) |
| 6 | **Litige suivi d'un avoir** (partiel ou total) | §4.1 / annexe A | « En litige » puis émission d'un AVOIR |
| 7 | **Litige suivi d'une facture rectificative** | §4.1 / annexe A | « En litige » puis facture Rectificative, statut « Annulée » sur l'initiale |
| 8 | **Erreur de routage** | §4.2.1 | PA-R non en charge de l'adresse → « ERREUR_ROUTAGE » (code 221), rejeu après synchro annuaire |

### Méthode pour ajouter un cas

1. Lire la sous-section correspondante de `docs/norme/XP Z12-014-v1.3.pdf`.
2. Identifier les acteurs, les statuts et l'étape responsable (tableaux de la norme).
3. Créer `packages/LogicielSolutionCompatible/features/<NN>-<nom_du_cas>.feature` (`# language: fr`, tag `@wip`).
   Les features sont **préfixées d'un numéro d'ordre** (`01-`, `02-`…) pour conserver la chronologie
   des cas d'usage (le cas nominal d'abord, puis les déboulements).
4. Ajouter les step definitions manquantes dans `packages/pac-bdd/src/pac_bdd/solution_compatible.py`
   (corps `pytest.skip(_EN_ATTENTE)` tant que la PA / le SC ne sont pas branchés).
5. Vérifier la collecte : `cd packages/pac-bdd && uv run pytest -k <nom_du_cas> -v` (attendu : SKIPPED).
6. Mettre à jour le tableau « État actuel » de ce guide.

## 8. Références

- `docs/norme/XP Z12-014-v1.3.pdf` — Cas d'usage B2B (cas nominal §4.2)
- `docs/developpement/BDD_Guide_Expert_Metier.md` — Rédiger un `.feature`
- `docs/developpement/BDD_Guide_Developpeur.md` — Implémenter les steps
- `docs/briques/07-routage/pa_multiple.feature` — Exemple de test de bout en bout multi-PA
- `docs/superpowers/specs/2026-06-10-bdd-solution-compatible-cas-nominal-design.md` — Design de ce lot
