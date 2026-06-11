<!--
SPDX-FileCopyrightText: 2026 PDP Libre

SPDX-License-Identifier: GPL-3.0-or-later
-->

# LogicielSolutionCompatible

Tests BDD écrits du point de vue d'un **Logiciel Solution Compatible** (SC) — par exemple
[Dolibarr](https://www.dolibarr.org/) ou Factur-e — qui pilote une **Plateforme Agréée** (PA) via son API.

Contrairement aux briques de la PA (`docs/briques/`), ces scénarios ne testent pas un composant
interne de notre plateforme : ils simulent un éditeur métier qui **émet** et **reçoit** des factures
à travers une PA. Ils ont donc une double vocation :

1. Tester notre PA Communautaire une fois ses briques construites.
2. Tester une **PA tierce** déjà agréée (le SC reste l'angle d'attaque, indépendant de l'implémentation de la PA).

## Mise en scène

On instancie deux Logiciels Solution Compatible :

- un pour le **VENDEUR**, raccordé à sa **PA-E** (Plateforme Agréée Émettrice) ;
- un pour l'**ACHETEUR**, raccordé à sa **PA-R** (Plateforme Agréée Réceptrice).

Les tests pilotent le SC du VENDEUR pour envoyer une facture (via l'API de la PA déjà configurée dans
le SC) vers l'ACHETEUR, puis pilotent le SC de l'ACHETEUR pour vérifier la bonne réception.
Le pilotage se fera, selon l'implémentation, via **Playwright** (IHM du SC) ou via **appels API** sur
le backend du SC. Les steps actuels restent **agnostiques de ce canal**.

## Contenu

```
features/
└── 01-echange_nominal.feature   # Cas nominal émission → réception (XP Z12-014 §4.2)
```

Les fichiers `.feature` sont **préfixés d'un numéro d'ordre** (`01-`, `02-`…) afin de conserver la
chronologie des cas d'usage.

Les **step definitions** vivent dans `packages/pac-bdd/src/pac_bdd/solution_compatible.py`
(importées par `pac_bdd/steps.py`), conformément à l'architecture BDD du dépôt.

## État

Phase de **spécification exécutable** : la PA n'est pas encore construite et aucun SC réel n'est
branché. Les scénarios sont collectés par `pytest` mais **skippés** (`@wip`) en attendant
l'implémentation réelle.

```shell
cd packages/pac-bdd
uv run pytest -k echange_nominal -v        # le scénario apparaît en SKIPPED
```

## Pour aller plus loin

Voir [`docs/developpement/BDD_Guide_SolutionCompatible.md`](../../docs/developpement/BDD_Guide_SolutionCompatible.md)
pour la méthode et le backlog des cas d'usage restants (rejets, litiges, avoirs, cycle complet).
