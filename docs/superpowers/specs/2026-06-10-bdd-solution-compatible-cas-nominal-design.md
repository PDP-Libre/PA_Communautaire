<!--
SPDX-FileCopyrightText: 2026 PDP Libre

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Design — BDD Logiciel Solution Compatible : cas nominal d'échange de facture

> Date : 2026-06-10
> Norme de référence : XP Z12-014 v1.3, section 4.2 « Description du cas nominal d'échange de factures »

## 1. Contexte et objectif

La PA Communautaire est en **phase de test, avant la construction des briques**. On amorce la
stratégie BDD non pas du côté des briques de la Plateforme Agréée (PA), mais du côté du
**Logiciel Solution Compatible** (SC) — par exemple Dolibarr ou Factur-e — qui pilote la PA via son API.

Ces tests ont une double vocation :

1. Tester l'ensemble des briques de **notre** plateforme agréée une fois construites.
2. Pouvoir tester une **plateforme agréée tierce** (le SC reste l'angle d'attaque, indépendant de l'implémentation de la PA).

Objectif de ce premier lot : décrire le **cas nominal « tout va bien »** (pas de litige, pas de rejet)
où un **VENDEUR** envoie une facture à son **ACHETEUR** et où l'ACHETEUR la réceptionne correctement.

## 2. Acteurs

| Acteur | Rôle | Outil |
|---|---|---|
| VENDEUR | Émet la facture | Logiciel Solution Compatible raccordé à sa **PA-E** (Plateforme Agréée Émettrice) |
| ACHETEUR | Reçoit la facture | Logiciel Solution Compatible raccordé à sa **PA-R** (Plateforme Agréée Réceptrice) |
| PA-E / PA-R | Plateformes Agréées | Posent les statuts de transmission |
| CdD PPF | Concentrateur de Données du PPF | Reçoit les statuts obligatoires (hors périmètre de ce lot) |

## 3. Périmètre retenu : Émission → Réception

Le cas nominal de la norme comporte 7 étapes (création → encaissement). **Ce premier lot s'arrête à la
phase de transmission**, conformément à l'objectif (« le vendeur envoie sa facture et son acheteur la
réceptionne bien »).

Statuts de transmission couverts :

| Côté | Statut | Sens |
|---|---|---|
| PA-E (VENDEUR) | Déposée | La facture a passé les contrôles réglementaires |
| PA-E (VENDEUR) | Émise | La plateforme a émis la facture vers la PA-R |
| PA-R (ACHETEUR) | Reçue | La PA-R a reçu la facture |
| PA-R (ACHETEUR) | Mise à disposition | La facture est mise à disposition de l'ACHETEUR |

Les phases de traitement (Prise en charge, Approuvée…), de paiement (Paiement transmis) et
d'encaissement (Encaissée) relèvent de lots ultérieurs documentés dans le guide.

## 4. Nature des tests : spécification exécutable (pending)

La PA n'existe pas encore et aucun SC réel n'est branché. Les `.feature` sont donc **collectés et
exécutés par pytest, mais skippés** (`pytest.skip`) tant que la plateforme et un SC réel ne sont pas
disponibles. Cela donne une **spécification vivante** : verte (skipped), jamais en `StepDefNotFound`.

Les steps sont **déclaratifs et agnostiques du canal** : ils décrivent le comportement métier
(« le VENDEUR envoie la facture »), sans préjuger de l'implémentation future (Playwright sur l'IHM du
SC ou appels API sur son backend). Ce choix sera tranché au moment de l'implémentation réelle des steps.

## 5. Architecture & placement

Le runner `packages/pac-bdd/test_scenario.py` collecte **tout `.feature` du dépôt** via
`glob("../../**/*.feature")`. Les step definitions, elles, sont chargées uniquement via
`from pac_bdd.steps import *`.

| Élément | Emplacement | Justification |
|---|---|---|
| Fichier `.feature` | `packages/LogicielSolutionCompatible/features/` | Sépare le SC des briques de la PA, tout en étant collecté automatiquement |
| `README.md` | `packages/LogicielSolutionCompatible/` | Documente le rôle du package |
| Step definitions | `packages/pac-bdd/src/pac_bdd/solution_compatible.py` | Suit le pattern existant (toute la mécanique BDD vit dans `pac-bdd`) ; évite une dépendance circulaire `pac-bdd → LogicielSolutionCompatible` |
| Import des steps | ajout dans `packages/pac-bdd/src/pac_bdd/steps.py` | `from .solution_compatible import *` |

### Arborescence créée

```
packages/LogicielSolutionCompatible/
├── README.md
└── features/
    └── 01-echange_nominal.feature           # préfixe numérique = chronologie des cas d'usage
packages/pac-bdd/src/pac_bdd/solution_compatible.py
packages/pac-bdd/src/pac_bdd/steps.py            (modifié : + import)
docs/developpement/BDD_Guide_SolutionCompatible.md
```

## 6. Scénario nominal

Un scénario end-to-end (style `docs/briques/07-routage/pa_multiple.feature`) sur la facture `"15"` :

```gherkin
# language: fr
@solution-compatible @cas-nominal @wip
Fonctionnalité: Échange nominal d'une facture entre Logiciels Solution Compatible

    Contexte:
        Soit un VENDEUR équipé d'un Logiciel Solution Compatible raccordé à sa PA-E
        Et un ACHETEUR équipé d'un Logiciel Solution Compatible raccordé à sa PA-R

    Scénario: Le VENDEUR émet la facture, l'ACHETEUR la réceptionne
        Quand le VENDEUR envoie la facture "15" à son ACHETEUR depuis son Logiciel Solution Compatible
        Alors le VENDEUR obtient le statut "Déposée" pour la facture "15"
        Quand le VENDEUR demande l'actualisation du statut de la facture "15"
        Alors le VENDEUR obtient le statut "Émise"
        Quand le VENDEUR demande l'actualisation du statut de la facture "15"
        Alors le VENDEUR obtient le statut "Mise à disposition"
        Quand l'ACHETEUR consulte ses factures reçues depuis son Logiciel Solution Compatible
        Alors l'ACHETEUR voit la facture "15" avec le statut "Reçue"
```

## 7. Le guide `BDD_Guide_SolutionCompatible.md`

Sert de base aux humains/agents pour couvrir l'ensemble des cas d'usage de la norme. Plan :

1. Contexte & objectif
2. Acteurs (VENDEUR/PA-E, ACHETEUR/PA-R, SC)
3. Les 7 étapes du cas nominal (tableau de la norme)
4. Où vivent les fichiers (arborescence)
5. Conventions de rédaction des steps SC (déclaratif, agnostique du canal, pending)
6. État actuel (cas nominal émission→réception, `@wip`)
7. **Backlog** des cas restants : rejet à l'émission (4.2.2), facture NON_TRANSMISE (4.2.3),
   rejet en réception (4.2.4), refus par l'ACHETEUR (4.2.5), litige + avoir, litige + facture
   rectificative, cycle de vie complet jusqu'à Encaissée.

## 8. Convention de nommage des statuts

Les statuts sont des **valeurs** entre guillemets (`"Déposée"`), conformément à la convention projet
(variables entre `"`, constantes préfixées `#`). On garde la casse de la norme.
