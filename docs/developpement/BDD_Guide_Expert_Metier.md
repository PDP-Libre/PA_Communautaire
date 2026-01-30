# Rédiger un test BDD - Guide pour l'expert métier

## Qu'est-ce que le BDD ?

Le **Behavior Driven Development** (BDD) permet de décrire le comportement attendu du système dans un langage naturel. Les scénarios sont écrits en **[Gherkin](https://www.artza-technologies.com/blog/langage-gherkin)**, un format structuré lisible par tous : experts métier, développeurs et testeurs.

```
┌────────────┐                 ┌──────────────┐                 ┌───────────┐
│   Étapes   │                 │   Code des   │                 │           │
│ en Gherkin ├─correspondance─>│    Steps     ├────manipule────>│  Système  │
└────────────┘                 └──────────────┘                 └───────────┘
```

Dans ce projet, les scénarios sont rédigés en **français** (`# language: fr`).

## Où écrire les scénarios ?

Les fichiers `.feature` sont situés dans `docs/briques/` selon la brique concernée :

```
docs/briques/
├── 01-api-gateway/      # API REST (healthcheck, sha256...)
├── 02-esb-central/      # Bus de messages NATS
├── 03-controle-formats/ # Validation des formats
├── 04-validation-metier/# Règles métier
├── 07-routage/          # Routage PEPPOL
└── 09-gestion-cycle-vie/# Cycle de vie facture
```

## Structure d'un fichier .feature

```gherkin
# language: fr
@api @critique
Fonctionnalité: Nom de la fonctionnalité
    Description libre de la fonctionnalité.
    Peut référencer une norme (ex: Section 4.4 de XP_Z12-013.pdf)

    Contexte:
        Soit une pa communautaire

    Règle: Les utilisateurs authentifiés accèdent au service

        Scénario: Healthcheck réussi
            Etant un utilisateur
            Quand j'appele l'API GET "/healthcheck"
            Alors j'obtiens le code de retour "200"

        Scénario: Healthcheck détaillé
            Quand j'appele l'API GET "/healthcheck/deep"
            Alors j'obtiens le code de retour "200"
            Et la réponse a une clé "healthcheck_resp" avec "8" éléments
```

## Conventions

* Les variables doivent être entourés par des "
* Les constantes doivent être précédées par des #


## Mots-clés Gherkin en français

Chacun de ces mots clefs permet de structurer l'expression du comportement.


| Français | Rôle |
|----------|------|
| `Fonctionnalité:` | Titre de la fonctionnalité testée |
| `Règle:` | Regroupe des scénarios sous une règle métier |
| `Contexte:` | Étapes exécutées avant chaque scénario |
| `Scénario:` | Un cas de test concret |
| `Plan du Scénario:` | Scénario paramétré avec plusieurs jeux de données |
| `Exemples:` | Tableau de données pour un Plan du Scénario |
| `Soit` / `Etant donné` | Pré-condition (Given) |
| `Quand` | Action effectuée (When) |
| `Alors` | Résultat attendu (Then) |
| `Et` | Continuation de l'étape précédente |
| `Mais` | Continuation négative |

Attention a bien vérifier que le titre de la fonctionnalité est bien unique et qu'il n'est pas utilisé dans un autre test. 

## Fonctionnalités avancées

### Plan du Scénario (tests paramétrés)

Évite la répétition en testant plusieurs combinaisons de données :

```gherkin
Plan du Scénario: Validation du mot de passe
    Quand je saisis le mot de passe "<motdepasse>"
    Alors je vois le message "<message>"

    Exemples:
        | motdepasse   | message                    |
        | court        | Mot de passe trop court    |
        | SANSMINUS    | Doit contenir une minuscule|
        | ValidPass1!  | Mot de passe accepté       |
```

### Tableaux de données

Pour passer des données structurées :

```gherkin
Soit les entreprises suivantes:
    | siren     | nom              | inscrit_peppol |
    | 123456789 | Entreprise A     | oui            |
    | 987654321 | Entreprise B     | non            |
```

### Blocs de texte (Doc Strings)

Pour du contenu multi-ligne :

```gherkin
Soit une facture au format JSON:
    """json
    {
        "numero": "F-2026-001",
        "montant": 1500.00
    }
    """
```

### Tags (étiquettes)

Organisent et filtrent les tests :

```gherkin
@smoke @critique
Fonctionnalité: Authentification

    @wip
    Scénario: Connexion avec 2FA
        ...

    @lent @base-de-donnees
    Scénario: Import massif d'utilisateurs
        ...
```

Tags courants : `@smoke`, `@critique`, `@wip` (work in progress), `@lent`, `@api`

## Bonnes pratiques

### 1. Décrire le comportement, pas l'implémentation

**Bien (déclaratif) :**
```gherkin
Quand Bob se connecte avec des identifiants valides
Alors il voit son tableau de bord personnalisé
```

**À éviter (impératif) :**
```gherkin
Quand je saisis "bob@test.com" dans le champ email
Et je saisis "motdepasse123" dans le champ mot de passe
Et je clique sur le bouton connexion
Alors je suis redirigé vers "/dashboard"
```

### 2. Un scénario = un comportement

Chaque scénario teste **un seul** comportement métier.

```gherkin
# Bien - comportements séparés
Scénario: L'utilisateur gratuit ne peut pas accéder au contenu premium
    Soit je suis connecté en tant qu'utilisateur gratuit
    Quand j'essaie d'accéder à un article premium
    Alors je vois une invitation à passer premium

Scénario: L'utilisateur premium accède à tout le contenu
    Soit je suis connecté en tant qu'utilisateur premium
    Quand j'accède à un article premium
    Alors je vois le contenu de l'article
```

### 3. Scénarios courts (3-5 étapes)

```gherkin
# Bien - focalisé et lisible
Scénario: Ajout d'un article au panier
    Soit je consulte un produit
    Quand je l'ajoute au panier
    Alors mon panier contient 1 article
```

### 4. Utiliser des valeurs concrètes

```gherkin
# Bien - valeurs explicites
Alors l'identification par SIRET porte le code "0002"
Alors l'identification par SIREN porte le code "0009"

# À éviter - trop vague
Alors l'identification est correcte
```

### 5. Référencer les normes

```gherkin
Fonctionnalité: healthcheck
    Section 4.4 de XP_Z12-013.pdf
    Un adresse /healthcheck doit permettre de vérifier la disponibilité du système.
```

## Anti-patterns à éviter

### ❌ Détails non essentiels

```gherkin
# Mauvais - trop de détails inutiles
Soit l'utilisateur "Jean Dupont" avec l'email "jean.dupont@example.com"
Et l'utilisateur habite "123 Rue Principale, 75001 Paris"
Et l'utilisateur a la carte bancaire "4111111111111111" expirant "12/25"

# Bien - l'essentiel uniquement
Soit Jean est un client enregistré
Et il a un moyen de paiement sauvegardé
```

### ❌ Logique conditionnelle

```gherkin
# Mauvais
Alors si les identifiants sont valides je vois le dashboard
Mais si les identifiants sont invalides je vois une erreur
```

Créez plutôt deux scénarios distincts.

## Collaboration : les Trois Amigos

Avant de rédiger les scénarios, réunissez :

1. **Expert métier** : Explique la fonctionnalité et les critères d'acceptation
2. **Développeur** : Identifie les considérations techniques
3. **Testeur** : Pose des questions sur les cas limites

## Vérifier vos scénarios

```bash
# Lister les tests sans les exécuter
cd packages/pac-bdd
uv run pytest --collect-only

# Exécuter un test spécifique
uv run pytest test_scenario.py::test_identification_france -v

# Exécuter les tests avec un tag
uv run pytest -m "smoke"
```

Si un test échoue avec `StepDefNotFound`, c'est qu'un développeur doit implémenter l'étape manquante.

## Exemples du projet

### Exemple simple : Healthcheck API

*Fichier : `docs/briques/01-api-gateway/healthcheck.feature`*

Un scénario minimal pour vérifier qu'un service est opérationnel.

```gherkin
# language: fr
Fonctionnalité: healthcheck
    Section 4.4 de XP_Z12-013.pdf
    L'API publiée par le Fournisseur API doit avoir une route GET /healthcheck
    permettant au Client API de vérifier si le service API est opérationnel.

    Contexte:
        Soit une pa communautaire

    Scénario: healthcheck
        Etant un utilisateur
        Quand j'appele l'API GET /healthcheck
        Alors j'obtiens le code de retour 200

    Scénario: healthcheck deep
        Quand j'appele l'API GET /healthcheck/deep
        Alors j'obtiens le code de retour 200
        Et la réponse a une clé "healthcheck_resp" avec 8 éléments
```

**Points clés :**
- `Contexte:` évite de répéter "Soit une pa communautaire" dans chaque scénario
- Référence à la norme AFNOR dans la description
- Étapes courtes et lisibles

---

### Exemple courant : Calculs PEPPOL

*Fichier : `docs/briques/07-routage/peppol.feature`*

Plusieurs scénarios testant des calculs métier avec différentes entrées.

```gherkin
# language: fr
Fonctionnalité: Requêtes PEPPOL
    PEPPOL est un service DNS.
    Je dois pouvoir interroger ce service
    et obtenir les informations utiles au routage des factures.

    Scénario: Identification France
        L'entreprise Française peut être identifiée de différentes façons

        Alors l'identification par SIRET porte le code "0002"
        Alors l'identification par SIREN porte le code "0009"
        Alors l'identification par TVA_FR porte le code "9957"

    Scénario: Empreinte participant
        L'empreinte participant dépend de l'identifiant et de son code

        Quand je calcule l'empreinte SIREN "222222222"
        Alors j'obtiens "3ddb2999105b666703fc700e14885016"

        Quand je calcule l'empreinte SIRET "222222222"
        Alors j'obtiens "6dbdf4f29451b37456ca48b550bdbaee"

        Quand je calcule l'empreinte TVA_FR "222222222"
        Alors j'obtiens "d0d6bafc0317e3e8baa9504a9a022f9c"

    Scénario: Hôte SML
        Le nom d'hôte pour la requête DNS est calculé à partir
        de l'empreinte et d'une racine SML.

        Soit la racine SML "ma.racine.local"

        Quand je calcule l'hôte SML pour SIREN "222222223"
        Alors j'obtiens "B-82b2b8c47a173b4be5e428bf8e5be1dc.iso6523-actorid-upis.ma.racine.local"

        Soit la racine SML "acc.edelivery.tech.ec.europa.eu"

        Quand je calcule l'hôte SML pour SIREN "222222222"
        Alors j'obtiens "B-3ddb2999105b666703fc700e14885016.iso6523-actorid-upis.acc.edelivery.tech.ec.europa.eu"
```

**Points clés :**
- Description libre dans chaque scénario pour expliquer le contexte
- `Soit` pour configurer l'environnement (racine SML)
- Valeurs concrètes pour vérifier les calculs
- Plusieurs assertions `Quand`/`Alors` enchaînées dans un même scénario

---

### Exemple complet : Communication inter-PA

*Fichier : `docs/briques/07-routage/pa_multiple.feature`*

Un scénario complexe impliquant plusieurs plateformes et entités.

```gherkin
# language: fr
Fonctionnalité: Multiples PA
    Communication entre multiples PA
    Vérifier qu'une facture déposée sur une PA est bien transférée à une autre PA

    Scénario: 2 PA
        # Configuration de l'environnement
        Soit la PA #pa1
        Et la PA #pa2
        Et l'entreprise #e1 enregistrée sur la PA #pa1
        Et l'entreprise #e2 enregistrée sur la PA #pa2
        Et la facture #f1 de #e1 à #e2

        # Action côté émetteur
        Soit un utilisateur de la PA #pa1
        Quand je dépose la facture #f1
        Alors j'obtiens le statut #accepted

        # Vérification côté destinataire
        Soit un utilisateur de la PA #pa2
        Quand je recherche la facture #f1
        Alors j'obtiens le statut #accepted
```

**Points clés :**
- Utilisation de références (`#pa1`, `#e1`, `#f1`) pour nommer les entités
- Changement de contexte utilisateur en cours de scénario
- Test de bout en bout couvrant émission et réception
- Commentaires pour structurer les phases du test

---

### Exemple avec cycle de vie

*Fichier : `docs/briques/09-gestion-cycle-vie/facture.feature`*

Un scénario testant le workflow asynchrone d'une facture.

```gherkin
# language: fr
Fonctionnalité: Rejet facture
    Rejet par défaut d'une facture

    Scénario: Facture rejetée
        Etant un utilisateur

        Quand je dépose une facture
        Alors j'obtiens un numéro de tâche

        Quand j'interroge la tâche
        Alors j'obtiens le statut #rejected
```

**Points clés :**
- Workflow en deux temps : dépôt puis interrogation
- Gestion des traitements asynchrones via "numéro de tâche"
- Statuts métier explicites (`#rejected`, `#accepted`)
