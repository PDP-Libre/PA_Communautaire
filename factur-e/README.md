# Factur-E — instance de démonstration et de test pour développeurs de PA

> Stack Docker Compose autoportée de **Factur-E**, publiée pour la communauté
> **PA_Communautaire**. Elle monte en local une instance Factur-E qui **émet** et
> **reçoit** des factures électroniques conformes, afin de **tester une Plateforme
> Agréée (PA) en cours de développement** contre un émetteur/récepteur réaliste.

---

## 1. Présentation

**Factur-E** est un SaaS de facturation électronique conforme à la réforme
française (généralisation sept. 2026 / sept. 2027). Il génère des factures
**Factur-X / EN 16931** au profil **EXTENDED-CTC-FR**, les transmet via une
Plateforme Agréée et suit leur cycle de vie (statuts CDAR AFNOR XP Z12-013).

Cette instance fournit un **partenaire d'échange** produisant des flux corrects
(factures bien formées CII XML + PDF/A-3, dépôts, accusés, changements de statut).
Un PA en développement peut lui faire **émettre une facture vers le PA** et lui
faire **recevoir une facture émise par le PA**, puis vérifier que son
implémentation se comporte correctement.

**Statut & évolution :**
- Version à **usage de démonstration**.
- Le connecteur Plateforme Agréée intègre aujourd'hui **SuperPDP** (sandbox) ;
  Factur-E doit évoluer pour intégrer **EsaLink**. Le développement du connecteur
  EsaLink prendra en compte la modélisation décrite dans le module `pdpconnectfr`
  de Dolibarr. La cible est de connecter Factur-E sur l'**API PA_Communautaire**
  dès sa définition.
- L'instance permet en outre de réaliser un **test BDD prototype** déclenchant
  l'émission d'une facture via le backend Factur-E (API directe en Bearer, cf. §4.5).

**Repères :**
- **Code source amont** : dépôt **GitLab interne** (BD2DB) — non public.
- **Plateforme Agréée de test** : SuperPDP (sandbox).
- **Périmètre** : émission B2B, réception, cycle de vie en polling (pas de webhook).

### Transparence sur ce qui est livré

| Composant | Forme livrée | Remarque |
|---|---|---|
| **web** (SPA React) | **dist Vite pré-buildé** (minifié) | bundle compilé, pas de source web |
| **api** (Fastify) | **source** (build local par Docker, runtime `tsx`) | l'API tourne sur ses sources TS ; pas d'artefact compilé en V1 |
| **ocr** (Python) | **source** (build local par Docker) | microservice Python |

Le source api/ocr est **publié ici sous licence GPL-3.0-or-later** (cf. §8), au
même titre que le reste du répertoire. Un durcissement (bundle compilé de l'API,
réduisant l'empreinte source) est envisagé pour une version ultérieure.

---

## 2. Prérequis

- **Docker** (Docker Desktop ou Docker Engine) — démon démarré.
- **Docker Compose v2** (commande `docker compose`).
- **`openssl`**, **`curl`**, **`tar`**, **`bash`** (présents par défaut sur
  macOS et la plupart des Linux).
- **Accès Internet au premier lancement** : le build api/ocr télécharge les
  images de base (`node:22`, `python:3.12`, `postgres:16`, `nginx`, `minio`) et
  les dépendances (npm / PyPI).
- **Pas besoin de Node.js / pnpm** côté poste : le web est déjà buildé, l'api/ocr
  sont buildés à l'intérieur de Docker.
- **Ports hôte libres** (bloc `472xx`, modifiables — cf. §5) :
  `47280` (web), `47281` (api), `47282` (ocr), `47254` (postgres),
  `47290`/`47291` (MinIO).
- **Un compte sandbox SuperPDP** avec un `client_id` / `client_secret` (cf. §3.2).

---

## 3. Installation

### 3.1 Récupérer le répertoire

```bash
git clone https://git.pdplibre.org/Construction_PA/PA_Communautaire.git
cd PA_Communautaire/factur-e
```

### 3.2 Configuration SuperPDP (à faire AVANT de renseigner les credentials)

Pour que l'instance puisse émettre/recevoir via la sandbox SuperPDP, créer
d'abord un compte **et** une application :

1. **Créer un compte** sur le **sandbox SuperPDP**.
   > ⚠️ L'inscription/connexion SuperPDP peut exiger une **vraie adresse email**
   > (réception d'un OTP SuperPDP) — une adresse `*.local` fictive ne suffit pas
   > de ce côté.
2. **Créer une application** dans l'espace SuperPDP :
   - **générer le secret** → on obtient un `client_id` + un `client_secret`
     (= `SUPERPDP_CLIENT_ID` / `SUPERPDP_CLIENT_SECRET`) ;
   - **renseigner l'URL de redirection** dans la zone *« URLs de redirection »* :
     ```
     http://localhost:47280/oauth/superpdp/callback
     ```
     (port web `47280` ; à adapter si `STAGING_WEB_PORT` est modifié). Sans cela,
     le retour OAuth est rejeté.
3. **Ensuite seulement**, reporter ces valeurs dans `.env.staging.local` (§3.3).

### 3.3 Renseigner les secrets sensibles

Le premier `./init.sh` crée `.env.staging.local` (gitignored) depuis
`.env.example` et **génère automatiquement** les clés locales `JWT_SIGNING_KEY`
et `ENCRYPTION_KEY_HEX`. Il s'arrête ensuite pour laisser renseigner les **deux
seuls secrets externes obligatoires** :

```bash
./init.sh
# → crée .env.staging.local, génère les clés, puis demande les secrets SuperPDP
$EDITOR .env.staging.local
```

À renseigner :

| Variable | Obligatoire | Comment l'obtenir |
|---|---|---|
| `SUPERPDP_CLIENT_ID` | **oui** | Enregistrement de l'application sur le **sandbox SuperPDP** |
| `SUPERPDP_CLIENT_SECRET` | **oui** | idem |
| `JWT_SIGNING_KEY` | non (auto-généré) | laisser vide → généré par `init.sh` |
| `ENCRYPTION_KEY_HEX` | non (auto-généré) | laisser vide → généré par `init.sh` |
| `INSEE_API_KEY` | non | inutile : les SIREN sandbox sont pré-seedés en cache |

> **Callback OAuth** : déjà couvert au §3.2 — l'URI
> `http://localhost:47280/oauth/superpdp/callback` doit être enregistrée côté
> application SuperPDP sandbox, identique à `SUPERPDP_REDIRECT_URI`.

> **Secrets** : ne jamais committer `.env.staging.local`. Il est déjà ignoré par
> le `.gitignore` de ce répertoire.

### 3.4 Démarrer

```bash
./init.sh
```

`init.sh` est **idempotent** :
1. décompresse `web-dist.tar.gz` et `sources.tar.gz` dans `runtime/` (gitignored) ;
2. construit les images api + ocr (`docker compose build`) — **plusieurs minutes
   au premier lancement** ;
3. démarre les 5 services et attend que `postgres` et `api` soient *healthy* ;
4. **seed** les SIREN sandbox + **2 comptes de test** ;
5. affiche les URLs et la marche à suivre.

Re-lancer `./init.sh` ne casse rien (no-op si la stack tourne). Après un refresh
des archives, utiliser `./init.sh --force` pour réextraire `runtime/`.

---

## 4. Usage

### 4.1 URLs

| Service | URL |
|---|---|
| Application (SPA) | <http://localhost:47280/> |
| API — santé | <http://localhost:47281/health> |
| API — dernier email | `http://localhost:47281/__dev/last-email?to=<email>` |
| MinIO console | <http://localhost:47291/> (user/pass : `factur_e_staging`) |

> Le SPA appelle l'API en **same-origin** via le proxy nginx (`/api`, `/oauth`,
> `/__dev`). Le port API direct (`47281`) est exposé pour les `curl` de debug et
> les tests automatisés (cf. §4.5).

### 4.2 Comptes de test pré-seedés

Deux comptes sont créés automatiquement, reliés aux SIREN sandbox SuperPDP :

| Compte | Email | SIREN | Rôle typique |
|---|---|---|---|
| **Burger Queen** | `bq@dev.factur-e.local` | `000000002` | émetteur |
| **Tricatel** | `tricatel@dev.factur-e.local` | `000000001` | acheteur / destinataire |

**Se connecter** (pose le cookie de session côté SPA — utiliser le port web
same-origin), en ouvrant dans le navigateur :

```
http://localhost:47280/__dev/quick-login?email=bq@dev.factur-e.local
http://localhost:47280/__dev/quick-login?email=tricatel@dev.factur-e.local
```

La connexion est alors établie, avec redirection vers le tableau de bord.

> **Login par formulaire** (alternative au quick-login) : les deux comptes ont le
> mot de passe `TestPassword12!`. La connexion déclenche un **OTP MFA par email**,
> récupérable via `/__dev/last-email` (cf. §4.3). Inutile de passer par « mot de
> passe oublié » : le mot de passe est connu.

**Connecter le compte à SuperPDP (canal OAuth réel)** : une fois connecté, aller
dans **Paramètres → Connexion Plateforme Agréée** → redirection vers SuperPDP →
consentement → retour vers Factur-E. Ce canal OAuth permet ensuite l'émission /
réception réelle via la sandbox. *(Nécessite les secrets SuperPDP du §3.2-3.3 +
le callback enregistré.)*

### 4.3 Récupérer les emails (OTP, notifications)

`EMAIL_ADAPTER=mock` : aucun email réel n'est envoyé, tout est capturé en mémoire
et relisible via `/__dev/last-email` — pratique pour récupérer un code OTP de
connexion ou vérifier une notification :

```bash
curl -s 'http://localhost:47281/__dev/last-email?to=bq@dev.factur-e.local'
```

### 4.4 Scénarios de test PA

1. **Émettre depuis Factur-E vers le PA** : connecté en Burger Queen, créer une
   facture (menu Émission) avec Tricatel comme acheteur (recherche annuaire →
   SIREN `000000001`), puis l'émettre. Observer le dépôt côté PA en développement.
2. **Recevoir sur Factur-E une facture émise par le PA** : faire émettre, depuis
   le PA, une facture à destination de Burger Queen / Tricatel ; vérifier sa
   réception et son rendu dans Factur-E.
3. **Vérifier les statuts CDAR** : suivre le cycle de vie (Déposée → Reçue →
   Disponible → Payée…) et le comparer aux statuts AFNOR XP Z12-013 renvoyés par
   le PA.
4. **Cas limites EN 16931 / EXTENDED-CTC-FR** : formats de facture, codes statut,
   métadonnées — pour valider la robustesse du parsing / de la validation du PA.

> **Réception & statuts = polling, pas temps réel.** Les factures reçues et les
> statuts CDAR sont récupérés par un job de polling **côté serveur** (indépendant
> de la session navigateur). Cadence par défaut de cet outil : **1 min**
> (`RECV_POLLING_CRON` / `CDAR_POLLING_CRON` dans `.env.staging.local` ; à passer
> à `*/15 * * * *` pour un comportement type prod). Une facture émise apparaît
> donc côté destinataire en ≤ 1 min, pas instantanément.

### 4.5 Piloter l'API directement (tests automatisés / BDD)

Pour intégrer l'instance dans des tests automatisés **sans passer par le front**,
l'API est joignable en direct sur `http://localhost:47281` (mêmes chemins que via
le proxy). Auth = **JWT Bearer**. Cela permet notamment d'écrire un **scénario BDD
prototype** déclenchant l'émission d'une facture via le backend Factur-E.

**1. Obtenir un token** (raccourci dev, comptes seedés) :

```bash
TOKEN=$(curl -s "http://localhost:47281/__dev/quick-login?email=bq@dev.factur-e.local" \
        | jq -r .access_token)
```

**2. Appeler l'API en Bearer** :

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:47281/api/invoices | jq
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:47281/api/received-invoices | jq
```

| Action | Méthode + route |
|---|---|
| Émettre une facture | `POST /api/invoices` |
| Prévisualiser (PDF/XML) | `POST /api/invoices/preview` |
| Vérifier l'unicité du numéro | `POST /api/invoices/check-number-unique` |
| Lister / détail facture | `GET /api/invoices` · `GET /api/invoices/:id` |
| Cycle de vie CDAR | `GET /api/invoices/:id/events` |
| PDF Factur-X / XML CII | `GET /api/invoices/:id/pdf` · `/xml` |
| Avoir / marquer payée | `POST /api/invoices/:id/credit-note` · `/mark-paid` |
| Factures reçues | `GET /api/received-invoices` · `/:id` |
| Statut connexion PA | `GET /pa/status` |
| Dernier email capturé | `GET /__dev/last-email?to=...` |

Notes :
- **Token court** : l'`access_token` expire ; rappeler `/__dev/quick-login` pour
  en regénérer un (idempotent).
- **Corps de `POST /api/invoices`** : le plus simple est de le capturer depuis
  l'onglet réseau du navigateur (émettre une facture via l'UI, copier le body),
  ou de se référer au contrat Zod `InvoiceFormSchema` (`packages/shared-schemas/`,
  décompressé dans `runtime/src/`).
- Les routes `/__dev/*` ne sont actives que parce que `NODE_ENV=development`.

**Spécification OpenAPI** : `factur-e/openapi.yaml` (OpenAPI 3.1) décrit les
endpoints + l'auth + les schémas. Pour la visualiser :
- coller dans <https://editor.swagger.io>, **ou**
- Swagger UI local :
  ```bash
  docker run --rm -p 8088:8080 -e SWAGGER_JSON=/spec/openapi.yaml \
    -v "$PWD:/spec" swaggerapi/swagger-ui   # → http://localhost:8088
  ```
- ou import direct dans Postman / Insomnia (génération de client incluse).

---

## 5. Troubleshooting

**Un port est déjà utilisé** (`bind: address already in use`)
Modifier les variables `STAGING_*_PORT` dans `.env.staging.local`, puis
`./init.sh`. (Si le port web change, mettre à jour `SUPERPDP_REDIRECT_URI` et le
callback enregistré côté SuperPDP.)

**`init.sh` s'arrête en demandant les secrets SuperPDP**
Normal au premier run : renseigner `SUPERPDP_CLIENT_ID` / `SUPERPDP_CLIENT_SECRET`
dans `.env.staging.local` (§3.2) puis relancer.

**Le build api échoue (npm / réseau)**
Le build a besoin d'Internet (npm, apt). Vérifier la connexion et relancer
`./init.sh`. Logs détaillés dans `/tmp/factur-e-init-*.log`.

**`api` ne devient pas healthy**
Augmenter le délai : `WAIT_API_S=180 ./init.sh`. Inspecter les logs :
`docker compose -f docker-compose.yml logs -f api`. (L'api applique les migrations
Postgres au boot — quelques secondes.)

**Le retour OAuth SuperPDP est rejeté**
Vérifier que `SUPERPDP_REDIRECT_URI` (`.env.staging.local`) est **identique** à
l'URI de callback enregistrée dans l'application sandbox SuperPDP.

**`/__dev/last-email` renvoie 404 "adapter is not Mock"**
`EMAIL_ADAPTER` doit valoir `mock` (défaut). Ne pas le passer à `tem`.

**`503 — Votre Plateforme Agréée est momentanément indisponible` alors que tout
est connecté**
Souvent un **numéro de facture déjà soumis** au sandbox SuperPDP (qui est
**partagé** entre toutes les instances) → le sandbox rejette le doublon. Utiliser
un **numéro de facture unique** (série haute) et ré-émettre. Le motif exact est en
base : `SELECT metadata->>'error' FROM auth_audit WHERE success=false ORDER BY id
DESC LIMIT 1;`.

**401 en boucle sur `/auth/me` + `/auth/refresh` (impossible de rester connecté)**
Les cookies ont été signés avec une clé `JWT_SIGNING_KEY` qui ne correspond plus à
celle de l'api (peut arriver après une régénération de `.env.staging.local`).
Solution : **vider les cookies du site** (ou ouvrir une **fenêtre privée**) puis
refaire le quick-login. (Un seul `401` sur `/auth/me` immédiatement suivi d'un
`/auth/refresh` 200 est, lui, normal — c'est le renouvellement d'access token.)

**Repartir de zéro**
```bash
docker compose -f docker-compose.yml down -v   # perd BDD + MinIO + uploads
./init.sh
```

---

## 6. Reset complet

```bash
docker compose -f docker-compose.yml down -v && ./init.sh
```

Supprime les volumes (BDD Postgres + stockage MinIO) et reconstruit un état neuf,
comptes de test re-seedés.

---

## 7. Contribution / maintenance

Ce répertoire `factur-e/` est **synchronisé depuis le dépôt Factur-E** (GitLab
interne BD2DB, non public) au fil des évolutions, via une mise à jour des archives
`web-dist.tar.gz` / `sources.tar.gz`.

- **Bug / amélioration de Factur-E** : remonter aux mainteneurs Factur-E (BD2DB).
- **Adaptation spécifique `PA_Communautaire`** : ouvrir une PR ici — review par les
  mainteneurs Factur-E.
- **Ne jamais committer** le contenu de `runtime/` (source décompressé) ni
  `.env.staging.local` — déjà couverts par le `.gitignore`.

---

## 8. Licence

Le contenu de ce répertoire `factur-e/` (configs, scripts, documentation, bundle
web et archives source) est distribué sous **GPL-3.0-or-later**, licence accordée
par **BD2DB**, titulaire de Factur-E. Le produit Factur-E **amont reste
propriétaire** ; seule la présente publication de démonstration est sous GPL.

Conformité **REUSE** : licence déclarée dans `REUSE.toml` (racine du dépôt) +
`LICENSES/GPL-3.0-or-later.txt`.

---

*Instance de démonstration et de test communautaire — pas une instance de
production.*
