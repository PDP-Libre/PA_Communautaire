---
theme: default
title: Onboarding contributeur — Construction PA
info: |
  Parcours d'onboarding pour les contributeurs de la PA Communautaire.
  Février 2026
drawings:
  persist: false
transition: slide-left
---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;">

# Onboarding contributeur

Construction PA

Février 2026

<img src="./LogoPDP.png" style="width:160px;margin-top:2rem;" />

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>1</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Parcours d'onboarding</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

`./docs/00_onboarding`

<div class="grid grid-cols-3 gap-4 mt-4">
<div>

### Tronc commun

1. Contexte et vision du projet
2. Architecture : les 10 briques
3. Les normes de référence
4. Organisation du dépôt
5. Stratégie BDD

</div>
<div>

### Parcours DEV

7. Installation environnement
8. Le code : packages et services
9. Implémenter un test BDD

### Parcours MÉTIER

6. Rédiger un scénario BDD
12. Focus par brique

</div>
<div>

### Finalisation commune

10. Rapports de tests
11. Contribuer

</div>
</div>

> Renvoi vers une documentation du repo : `./<rep>/<document>`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>2</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 1 — Contexte et vision du projet

[TOUS] Comprendre pourquoi ce projet existe

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>3</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">La réforme facturation électronique</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

**Qu'est-ce qu'une PA — Plateforme Agréée** (anciennement PDP) ?

- Point d'entrée obligatoire pour émettre/recevoir des factures électroniques
- Positionnement vis-à-vis du PPF (Portail Public de Facturation)

**Calendrier de la réforme :**

- **Sept. 2026** : obligation de réception pour toutes les entreprises
- **2027** : obligation d'émission (échelonné par taille)
- 3 obligations : réception, émission, e-reporting (transmission fiscale)

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>4</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Vision PA Communautaire</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

**Trajectoire du projet PDP Libre :**

- Choix d'une PA partenaire pour septembre 2026
- En parallèle : construction d'une PA Communautaire open source

**Valeurs fondamentales :**

- **Open source** : code ouvert, licences libres (GPL-3.0-or-later)
- **Souveraineté** : indépendance vis-à-vis des acteurs commerciaux
- **Communautaire** : gouvernance participative et transparente
- **Sans but lucratif** : au service de l'intérêt général

Ce projet est porté par des bénévoles. L'objectif cible est de produire tout ou partie du code d'une Plateforme Agréée candidat à être exploité par l'association PDP Libre ou toute entité qui le déciderait.

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>5</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Parcours d'une facture (vue simplifiée)</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

1. L'émetteur dépose une facture sur sa PDP
2. La PDP contrôle le format (UBL, CII, Factur-X)
3. La PDP valide les règles métier
4. La PDP route la facture vers la PA du destinataire (via PEPPOL dans certains cas)
5. Le destinataire reçoit la facture et gère son cycle de vie
6. Les données fiscales sont transmises à l'État (e-reporting)

> Ressources : `./README.md`, forum https://forum.pdplibre.org/

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>6</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 2 — Architecture fonctionnelle

[TOUS] Les 10 briques de la plateforme

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>7</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Vue d'ensemble de l'architecture</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

<img src="./Architecture_Plateforme_Factures_Electroniques_v03.png" style="height:380px;margin:0 auto;display:block;" />

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>8</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Les 10 briques</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

| # | Brique | Description |
|---|--------|-------------|
| 01 | API Gateway (FastAPI) | Point d'entrée REST, norme XP Z12-013 |
| 02 | ESB Central (NATS) | Orchestration des flux, message queue |
| 03 | Contrôle Formats | Validation UBL / CII / Factur-X |
| 04 | Validation Métier | Règles métier, vérification destinataire |
| 05 | Conversion Formats | Conversion entre UBL, CII, Factur-X |
| 06 | Annuaire Local | Cache local, synchronisation PPF |
| 07 | Routage (PEPPOL) | Acheminement inter-PDP |
| 08 | Transmission Fiscale | E-reporting vers l'État |
| 09 | Gestion Cycle de Vie | Statuts : déposée, reçue, approuvée… |
| 10 | Stockage (S3 / SeaweedFS) | Persistance des fichiers factures |

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>9</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Flux type d'une facture</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

1. Dépôt facture via **API Gateway** (01)
2. Publication sur l'**ESB Central** (02)
3. **Contrôle du format** (03) puis **validation métier** (04)
4. **Conversion** si nécessaire (05)
5. Consultation de l'**annuaire** (06) pour trouver le destinataire
6. **Routage** vers la PA destinataire via PEPPOL (07)
7. **Transmission fiscale** à l'État (08)
8. Gestion du **cycle de vie** et statuts (09)
9. **Stockage** des fichiers en S3 (10)

> Documentation par brique : `./docs/briques/<NN-nom>/README.md`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>10</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 3 — Les normes de référence

[TOUS] AFNOR, UN/CEFACT et cas d'usage

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>11</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">3 normes AFNOR incluses dans le repo</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

**XP Z12-012 — Formats et cycle de vie**

- Formats : UBL, CII, Factur-X (EN16931)
- Profils de messages, règles métier, statuts de cycle de vie
- Annexe A (Excel) : règles métier, code lists, mappings
- Annexe B : exemples de factures et statuts

**XP Z12-013 — API REST**

- Swagger en annexe (Flow Service, Directory Service)
- Routes : `/healthcheck`, `/flows`, `/directory-line`, `/search`…

**XP Z12-014 — Cas d'usage B2B**

- UC1 à UC5 avec exemples XML complets
- Scénarios nominaux et d'erreur

> `./docs/norme/index.md` — **Commencer par là**

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>12</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">XP Z12-014 — Cas d'usage B2B</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
<img src="./Cas_Usage_Nominal_A.png" style="height:220px;" />
<img src="./Cas_Usage_Nominal_B.png" style="height:220px;" />
</div>

**Autres cas documentés :**

- Rejet à l'émission d'une facture e-invoicing
- Facture Déposée NON_TRANSMISE pour absence de PA-R
- Rejet d'une facture en réception
- Refus d'une facture par l'ACHETEUR
- Facture en litige, suivie d'un AVOIR partiel ou total
- Facture en litige, suivie d'une Facture Rectificative

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>13</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Autres références</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

- **CDAR D22B (UN/CEFACT)** — Cross Domain Acknowledgement and Response. Format des accusés de réception entre PDP.
- **BRS - CDAError Acknowledgement Process** — Processus de gestion des erreurs d'accusé.
- **Standard FACTUR-X 1.07.3** (2025-05-15) — Disponible sur le site de la [FNFE](https://fnfe-mpe.org/).

<img src="./XFacture.png" style="height:190px;margin:1rem auto 0;display:block;" />

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>14</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 4 — Organisation du dépôt

[TOUS] Où trouver quoi dans le monorepo

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>15</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Structure du monorepo</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

Un seul référentiel pour tous les projets.

```
./docs/
  briques/         → doc + .feature par brique
  développement/   → guides dev, BDD, install
  norme/           → normes AFNOR et annexes
  test/            → exemples BDD commentés

./packages/          → un sous-répertoire par « projet »
  pac0/            → implémentation de référence
  pac-bdd/         → moteur de tests BDD
  pac0-cli/        → CLI utilitaire (pilotage de la PA)

./docker/            → docker-compose, Dockerfiles (10 services + test-bdd)
./report/            → rapports de tests (HTML, MD, XML)
./script/            → scripts utilitaires (./script/test)
```

**Dépôts :** GitHub (releases publiques) · Forgejo (développement quotidien)

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>16</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 5 — Stratégie BDD

[TOUS] Pourquoi et comment on teste

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>17</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Le BDD : un langage commun</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

> Le « Behavior Driven Development » est une méthode Agile dans laquelle le produit est conçu autour du comportement qu'un utilisateur s'attend à expérimenter.

- **Spécifications exécutables** : langage commun entre métier et développeur
- Vision communautaire : outils de tests pour les éditeurs de logiciels métier et de PA

**La boucle « Trois Amigos » :** Expert métier + Développeur + Testeur

**Gherkin en français :** `Fonctionnalité`, `Scénario`, `Soit`, `Quand`, `Alors`

**Cycle de vie d'un test :**

1. Rédaction par l'expert métier (`.feature`)
2. Implémentation par le développeur (step definitions)
3. Exécution automatique (`pytest-bdd`)

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>18</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Lien feature → steps → système</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

- Fichiers `.feature` dans `./docs/briques/<NN-nom>/` — rédigés en Gherkin français
- Code des steps dans `packages/pac-bdd/src/pac_bdd/` — `api.py`, `peppol.py`, `service.py`, `esb.py`…
- Le moteur `pytest-bdd` fait le lien :
  - Lit une étape Gherkin (ex : `Quand j'appelle l'API GET /healthcheck`)
  - Cherche le step definition correspondant
  - Exécute la fonction Python associée

> Rapports : `./report/pac-bdd/`

> Ressources : `./docs/developpement/BDD_README.md`, `BDD_Guide_Developpeur.md`, `BDD_Guide_Expert_Metier.md`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>19</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 6 — Rédiger un scénario BDD

[MÉTIER] Guide pour l'expert métier

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>20</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Structure d'un fichier .feature</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

- **Entête obligatoire** : `# language: fr`
- **Fonctionnalité** : titre unique + description libre (peut référencer la norme)
- **Contexte** : étapes exécutées avant chaque scénario
- **Scénario** : un cas de test concret
  - `Soit` / `Étant donné` : précondition (Given)
  - `Quand` : action effectuée (When)
  - `Alors` : résultat attendu (Then)
  - `Et` / `Mais` : continuation

**Conventions du projet :**

- Variables entre guillemets : `"valeur"`
- Constantes préfixées : `#pa1`, `#accepted`

> Exemple : `./docs/briques/01-api-gateway/healthcheck.feature`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>21</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Bonnes pratiques et anti-patterns</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

**Déclaratif, pas impératif :**

- ✅ `Quand Bob se connecte avec des identifiants valides`
- ❌ `Quand je saisis bob@test.com dans le champ email`

**Un scénario = un comportement (3-5 étapes)**

**Utiliser des valeurs concrètes :**

- ✅ `Alors l'identification par SIRET porte le code "0002"`
- ❌ `Alors l'identification est correcte`

**Anti-patterns à éviter :**

- Détails non essentiels (adresses, CB…)
- Logique conditionnelle (`si… alors…`) → 2 scénarios

Fonctionnalités avancées : Plan du Scénario, tableaux, Doc Strings, tags.

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>22</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Exemples concrets du projet</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

- **Healthcheck simple** (`01-api-gateway/healthcheck.feature`) — Contexte + 2 scénarios courts, référence norme
- **Calculs PEPPOL** (`07-routage/peppol.feature`) — Plusieurs scénarios avec valeurs concrètes
- **Communication inter-PA** (`07-routage/pa_multiple.feature`) — Références `#pa1`, `#e1`, `#f1` — test bout en bout
- **Cycle de vie facture** (`09-gestion-cycle-vie/facture.feature`) — Workflow asynchrone : dépôt puis interrogation

> **Exercice** : écrire un scénario pour la brique 05, 06 ou 08

> Ressources : `./docs/developpement/BDD_Guide_Expert_Metier.md`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>23</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 7 — Installation de l'environnement

[DEV] Mettre en place son poste de développement

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>24</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Accéder au repo</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

```bash
mkdir <repertoire_racine>
cd <repertoire_racine>
git clone https://git.pdplibre.org/Construction_PA/PA_Communautaire.git
cd PA_Communautaire
```

Accès navigateur : https://git.pdplibre.org/Construction_PA/PA_Communautaire.git

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>25</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Installer l'environnement : Docker vs Linux natif</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;">
<div>

### Docker (recommandé)

- Prérequis : Docker / Podman
- `cd docker && docker compose up -d`
- 10 services + test-bdd en un seul compose
- Vérification : http://localhost:8000/docs
- Cible : branche `dev_docker_v2`
- S3 inclus (SeaweedFS, port 8333)

</div>
<div>

### Linux natif

- Python 3.13+, `uv` (pas pip !)
- `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `uv sync` dans chaque package
- NATS Server : `nats-server -V -js`
- Lancement séquentiel :
  1. `nats-server -V -js`
  2. `uv run fastapi dev ...`
  3. `uv run faststream run ...`

</div>
</div>

> `./docs/developpement/Installation_Linux.md`, `./docs/developpement/Installation_Docker.md`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>26</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Vérification de l'installation</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

```bash
# Lancer les tests BDD
cd packages/pac-bdd && uv run pytest -v

# Lancer tous les tests avec rapport
./script/test

# Vérifier l'API Gateway
# http://localhost:8000/docs (interface Swagger FastAPI)
```

> Ressources : `docs/developpement/Installation_Docker.md`, `Installation_Linux.md`, `Configuration.md`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>27</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 8 — Le code : packages et services

[DEV] Comprendre l'implémentation

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>28</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Conventions du code</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

- Python 3.13+ avec `async/await` partout
- Package manager : `uv` (jamais pip)
  - `uv sync` pour installer, `uv run` pour exécuter
- `pytest-asyncio` avec `asyncio_mode = "auto"`
- Licence GPL-3.0-or-later avec headers SPDX
- Chaque nouveau module de steps doit être importé dans `steps.py`

> Ressources : `packages/pac0/README.md`, `packages/pac-bdd/README.md`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>29</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 9 — Implémenter un test BDD

[DEV] Coder les step definitions

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>30</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Flux : .feature → step → système</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

1. **Identifier l'étape manquante** — `StepDefNotFound: "je vérifie le format UBL"`
2. **Choisir le bon module** — `api.py` (REST), `peppol.py` (routage), `service.py`, `esb.py`
3. **Écrire le step** :
   ```python
   @when(parsers.parse('j\'appelle l\'API {verb} {path}'))
   ```
   - `parsers.parse` pour les patterns simples
   - `parsers.re` pour les regex complexes
4. **Gérer Data Tables et Doc Strings** :
   - `datatable` : liste de dictionnaires
   - `docstring` : texte brut du bloc `"""..."""`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>31</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Fixtures et exécution</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

- **WorldContext** : environnement multi-PA — `world1.pa1.api_gateway.get_client()`
- **Contexte local Pydantic** (`LocalTestCtx`) — Partage de données entre steps
- **Pattern async → sync** : `@async_to_sync`

```bash
uv run pytest                                     # tous les tests
uv run pytest test_scenario.py::test_xxx -v        # un seul
uv run pytest -v -s --log-cli-level=DEBUG          # mode debug
uv run pytest --collect-only                       # collecter sans exécuter
```

> Ressources : `docs/developpement/BDD_Guide_Developpeur.md`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>32</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 10 — Rapports de tests

[TOUS] Vérifier que ça marche

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>33</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Lancer et lire les rapports</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

```bash
./script/test                                  # lancer tous les tests
cd packages/pac-bdd && uv run pytest           # lancer un package
```

**Rapports générés dans `./report/` :**

- `report/pac0/` : tests unitaires de l'implémentation
- `report/pac-bdd/` : tests BDD (scénarios Gherkin)

**3 formats :** HTML (visuel, navigable) · Markdown (texte brut) · XML JUnit (intégration continue)

**Interpréter un échec :**

- `StepDefNotFound` : step manquant (à implémenter)
- `AssertionError` : bug dans le code ou le scénario

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>34</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 11 — Contribuer

[TOUS] Workflow et bonnes pratiques

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>35</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Cycle de contribution</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

1. **Accès Forgejo** : demande d'invitation via le [forum](https://forum.pdplibre.org/)
2. **Fork + clone** du projet depuis Forgejo
   ```bash
   git clone https://git.pdplibre.org/Construction_PA/PA_Communautaire.git
   ```
3. **Créer une branche thématique** : `feature/ma-fonctionnalite`, `fix/mon-correctif`
4. **Vérifier les tests** avant de commiter :
   ```bash
   cd packages/pac-bdd && uv run pytest -v
   ```
5. **Ouvrir une Pull Request** — toujours en lien avec une Issue, préfixe `WIP` tant que le travail est en cours
6. **Licence GPL-3.0-or-later**, headers SPDX obligatoires

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>36</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Bloc 12 — Focus par brique

[MÉTIER] Couvrir le périmètre fonctionnel

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>37</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Couverture actuelle (février 2026)</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

**Briques avec `.feature` existants (incomplets) :**

- 01-API Gateway : healthcheck, service, sha256, trackingId
- 02-ESB Central : healthcheck, esb, service, lifecycle, world
- 03-Contrôle Formats : format, service
- 04-Validation Métier : compliance
- 07-Routage : peppol, pa_multiple, peppol_live
- 09-Gestion Cycle Vie : facture, workflow, demo

**Briques à couvrir (prioritaires) :** 05-Conversion Formats, 06-Annuaire Local, 08-Transmission Fiscale, 10-Stockage.

**Méthode :** Lire le README → Identifier la section de norme → Lister les comportements → Rédiger les `.feature`

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>38</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

# Synthèse

Récap des parcours et ressources

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>39</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Récapitulatif des parcours</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

| Bloc | DEV | MÉTIER | Thème |
|------|:---:|:------:|-------|
| 1 — Contexte et vision | ✓ | ✓ | Pourquoi ce projet existe |
| 2 — Architecture 10 briques | ✓ | ✓ | Organisation du système |
| 3 — Normes de référence | ✓ | ✓ | Sur quoi on s'appuie |
| 4 — Organisation du dépôt | ✓ | ✓ | Où trouver quoi |
| 5 — Stratégie BDD | ✓ | ✓ | Comment on teste |
| 6 — Rédiger un scénario BDD | | ✓ | Écrire un .feature |
| 7 — Installation environnement | ✓ | | Mettre en place son poste |
| 8 — Le code : packages | ✓ | | Comprendre l'implémentation |
| 9 — Implémenter un test BDD | ✓ | | Coder les steps |
| 10 — Rapports de tests | ✓ | ✓ | Vérifier que ça marche |
| 11 — Contribuer | ✓ | ✓ | Pousser ses changements |
| 12 — Focus par brique | | ✓ | Couvrir le périmètre |

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>40</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><h1 style="margin:0;flex:1;">Ressources et contacts</h1><img src="./LogoPDP.png" style="width:96px;height:48px;margin-left:1rem;" /></div>

**Documentation :**

- `docs/developpement/Architecture.md` — Architecture technique
- `docs/developpement/Contribuer.md` — Guide de contribution
- `docs/developpement/BDD_Guide_Expert_Metier.md` — Guide BDD métier
- `docs/developpement/BDD_Guide_Developpeur.md` — Guide BDD dev
- `docs/norme/index.md` — Normes de référence

**Communauté :**

- Forum : https://forum.pdplibre.org/
- Forgejo : https://git.pdplibre.org/Construction_PA/PA_Communautaire
- GitHub : https://github.com/PDP-Libre/PA_Communautaire
- Visio bimensuelle

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>41</span></div>

---

<div style="position:absolute;top:0;left:0;right:0;height:5px;background:#4ecdc4;z-index:20;"></div>

<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#2c3e50,#34495e);color:white;">

<img src="./LogoPDP.png" style="width:160px;margin-bottom:2rem;" />

# Merci

**pdplibre.org** · contact@pdplibre.org

*Association à but non lucratif*

</div>

<div style="position:absolute;bottom:0;left:0;right:0;height:36px;background:#2c3e50;color:#9ca3af;font-size:12px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:20;"><span>Février 2026</span><span>42</span></div>
