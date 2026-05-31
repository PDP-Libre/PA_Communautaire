#!/usr/bin/env bash
# init.sh — démarrage du staging Factur-E autoporté (PA_Communautaire).
# sprint-07 T-CL-FORGEJO-PUBLISH-PDP-LIBRE.
#
# Idempotent — safe re-run :
#   1. Décompresse les archives → runtime/ (skip si déjà extrait ; --force réextrait).
#   2. Crée .env.staging.local depuis .env.example si absent + génère les clés
#      locales (JWT/ENCRYPTION) ; s'arrête si les secrets SuperPDP manquent.
#   3. docker compose build (api + ocr depuis runtime/src).
#   4. docker compose up -d + attente postgres/api healthy.
#   5. Seed : SIREN sandbox + 2 comptes de test (Burger Queen / Tricatel).
#   6. Affiche les URLs + la marche à suivre (login, OAuth SuperPDP, emails).
#
# Usage :
#   ./init.sh            # démarrage normal
#   ./init.sh --force    # réextrait les archives runtime/ (après refresh PR)
#
# Arrêt   : docker compose -f docker-compose.yml down        (préserve les données)
# Reset   : docker compose -f docker-compose.yml down -v     (perd BDD + MinIO)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE="$SCRIPT_DIR/.env.staging.local"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml")
WAIT_POSTGRES_S="${WAIT_POSTGRES_S:-45}"
WAIT_API_S="${WAIT_API_S:-90}"
LOG="/tmp/factur-e-init-$$.log"
FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

log() { printf '[init] %s\n' "$*"; }
err() { printf '[init][KO] %s\n' "$*" >&2; }

cleanup_on_error() {
  local rc=$?
  if [ $rc -ne 0 ]; then
    err "init.sh a échoué (code $rc) — voir $LOG"
    err "  diagnostics : ${COMPOSE[*]} ps   |   ${COMPOSE[*]} logs --tail=50"
  fi
}
trap cleanup_on_error EXIT

# ---- 0. Prérequis ---------------------------------------------------------
log "0/6 vérification des prérequis (Docker + Compose)..."
if ! command -v docker >/dev/null 2>&1; then
  err "Docker introuvable. Installer Docker Desktop ou Docker Engine. Cf. README §2."
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  err "Docker Compose v2 introuvable (commande 'docker compose'). Cf. README §2."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  err "Le démon Docker ne répond pas — démarrer Docker puis relancer ./init.sh."
  exit 1
fi

# ---- 1. Décompression des archives → runtime/ -----------------------------
log "1/6 décompression des archives (runtime/)..."
extract() {
  local archive="$1" dest="$2" marker="$3"
  if [ ! -f "$archive" ]; then
    err "archive manquante : $archive (relancer package.sh côté Factur-E ?)"
    exit 1
  fi
  if [ "$FORCE" = "1" ] || [ ! -e "$marker" ]; then
    rm -rf "$dest"
    mkdir -p "$dest"
    tar -xzf "$archive" -C "$dest"
    log "  extrait $(basename "$archive") → $dest"
  else
    log "  $(basename "$archive") déjà extrait (skip — ./init.sh --force pour réextraire)"
  fi
}
extract "$SCRIPT_DIR/web-dist.tar.gz" "$SCRIPT_DIR/runtime" "$SCRIPT_DIR/runtime/web/dist"
extract "$SCRIPT_DIR/sources.tar.gz" "$SCRIPT_DIR/runtime/src" "$SCRIPT_DIR/runtime/src/package.json"

# ---- 2. .env.staging.local + clés locales ---------------------------------
set_env_var() {
  # set_env_var KEY VALUE — remplace `KEY=...` dans $ENV_FILE (ou l'ajoute).
  local key="$1" value="$2"
  if grep -qE "^${key}=" "$ENV_FILE"; then
    # Délimiteur | (les valeurs hex/URL ne contiennent pas de |).
    sed -i.bak -E "s|^${key}=.*|${key}=${value}|" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
  else
    printf '%s=%s\n' "$key" "$value" >>"$ENV_FILE"
  fi
}
env_value() {
  # Valeur de KEY dans $ENV_FILE, commentaire inline (` # ...`) et espaces
  # de bord retirés (Docker Compose les strippe aussi côté env-file).
  grep -E "^$1=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2- \
    | sed -E 's/[[:space:]]+#.*$//; s/^[[:space:]]+//; s/[[:space:]]+$//'
}

if [ ! -f "$ENV_FILE" ]; then
  log "2/6 création de .env.staging.local depuis .env.example..."
  cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"
  log "  génération des clés locales (JWT_SIGNING_KEY + ENCRYPTION_KEY_HEX)..."
  set_env_var JWT_SIGNING_KEY "$(openssl rand -hex 32)"
  set_env_var ENCRYPTION_KEY_HEX "$(openssl rand -hex 32)"
  err "Renseigne SUPERPDP_CLIENT_ID et SUPERPDP_CLIENT_SECRET dans :"
  err "    $ENV_FILE"
  err "  (credentials sandbox SuperPDP — cf. README §3.2), puis relance ./init.sh."
  trap - EXIT
  exit 0
fi
log "2/6 .env.staging.local présent."
# Garantit la présence des clés locales même si le fichier vient d'une vieille copie.
[ -z "$(env_value JWT_SIGNING_KEY)" ] && set_env_var JWT_SIGNING_KEY "$(openssl rand -hex 32)"
[ -z "$(env_value ENCRYPTION_KEY_HEX)" ] && set_env_var ENCRYPTION_KEY_HEX "$(openssl rand -hex 32)"
if [ -z "$(env_value SUPERPDP_CLIENT_ID)" ] || [ -z "$(env_value SUPERPDP_CLIENT_SECRET)" ]; then
  err "SUPERPDP_CLIENT_ID / SUPERPDP_CLIENT_SECRET vides dans $ENV_FILE."
  err "  Renseigne-les (cf. README §3.2) puis relance ./init.sh."
  trap - EXIT
  exit 0
fi

# ---- 2.bis Garde anti-divergence clé JWT ----------------------------------
# Si l'api tourne déjà avec une JWT_SIGNING_KEY différente de celle du fichier
# (ex. après régénération de .env.staging.local), le `up -d` ci-dessous recrée
# le container → les cookies de session existants deviennent invalides (401 en
# boucle). On prévient pour que l'utilisateur se reconnecte proprement.
if docker inspect factur-e-pdplibre-api >/dev/null 2>&1; then
  running_jwt="$(docker exec factur-e-pdplibre-api printenv JWT_SIGNING_KEY 2>/dev/null || true)"
  if [ -n "$running_jwt" ] && [ "$running_jwt" != "$(env_value JWT_SIGNING_KEY)" ]; then
    log "  (info) clé JWT modifiée → l'api va être recréée ; reconnecte-toi"
    log "         ensuite (vide les cookies du site ou ouvre une fenêtre privée)."
  fi
fi

# ---- 3. Build api + ocr ---------------------------------------------------
log "3/6 docker compose build (api + ocr — première fois : plusieurs minutes)..."
"${COMPOSE[@]}" build 2>&1 | tee -a "$LOG"

# ---- 4. Up + attente healthy ----------------------------------------------
log "4/6 docker compose up -d..."
"${COMPOSE[@]}" up -d 2>&1 | tee -a "$LOG"

wait_healthy() {
  local cname="$1" timeout="$2" i state
  log "  attente $cname healthy (timeout ${timeout}s)..."
  for i in $(seq 1 "$timeout"); do
    state="$(docker inspect --format '{{.State.Health.Status}}' "$cname" 2>/dev/null || echo starting)"
    [ "$state" = "healthy" ] && { log "  $cname healthy (${i}s)"; return 0; }
    sleep 1
  done
  err "$cname n'est pas devenu healthy en ${timeout}s"
  "${COMPOSE[@]}" logs --tail=30 "${cname#factur-e-pdplibre-}" >&2 || true
  exit 1
}
wait_healthy factur-e-pdplibre-postgres "$WAIT_POSTGRES_S"
wait_healthy factur-e-pdplibre-api "$WAIT_API_S"

# ---- 5. Seed SIREN sandbox + 2 comptes de test ----------------------------
# Best-effort : un échec de seed ne casse pas le démarrage (warn seulement).
log "5/6 seed des SIREN sandbox + comptes de test (Burger Queen / Tricatel)..."
API_PORT="$(env_value STAGING_API_PORT)"; API_PORT="${API_PORT:-47281}"
PGUSER="$(env_value POSTGRES_USER)"; PGUSER="${PGUSER:-factur_e_staging}"
PGDB="$(env_value POSTGRES_DB)"; PGDB="${PGDB:-factur_e_staging}"
seed() (
  set +e
  # 5.a Caches INSEE + annuaire des 2 SIREN sandbox (identité émetteur + buyer).
  "${COMPOSE[@]}" exec -T api pnpm --filter @factur-e/api dev:seed-test-sirens \
    >>"$LOG" 2>&1 || log "  (warn) seed-test-sirens a échoué — voir $LOG"
  # 5.b Création idempotente des 2 comptes (with_pa=false → OAuth réel ensuite).
  #     Burger Queen (000000002, mode base) + Tricatel (000000001, mode avancé).
  for spec in "bq@dev.factur-e.local:000000002:basic" "tricatel@dev.factur-e.local:000000001:advanced"; do
    email="${spec%%:*}"; rest="${spec#*:}"; siren="${rest%%:*}"; mode="${rest##*:}"
    curl -fsS "http://localhost:${API_PORT}/__dev/quick-login?email=${email}&siren=${siren}&with_pa=false&ui_mode=${mode}" \
      -o /dev/null >>"$LOG" 2>&1 || log "  (warn) quick-login $email a échoué — voir $LOG"
  done
  # 5.c Polit l'identité émetteur (nom/NAF/adresse + TVA/IBAN/BIC fake valides
  #     et distincts par compte) sur les valeurs sandbox. TVA = clé FR calculée,
  #     IBAN = checksum mod-97 valide.
  psql_exec() { "${COMPOSE[@]}" exec -T postgres psql -U "$PGUSER" -d "$PGDB" -v ON_ERROR_STOP=1 -c "$1" >>"$LOG" 2>&1; }
  psql_exec "UPDATE customers SET legal_name='BURGER QUEEN', naf_code='56.10C', juridique_code='5710', vat_number='FR18000000002', vat_number_unverified=false, iban='FR4510278060410002054550137', bic='CMCIFR2AXXX', address='{\"line_one\":\"2 AVENUE DU FAST FOOD\",\"postcode\":\"69002\",\"city\":\"LYON\",\"country_code\":\"FR\"}' WHERE siren='000000002';" \
    || log "  (warn) update identité Burger Queen — voir $LOG"
  psql_exec "UPDATE customers SET legal_name='TRICATEL', naf_code='10.89Z', juridique_code='5710', vat_number='FR15000000001', vat_number_unverified=false, iban='FR2930003012340000567890125', bic='SOGEFRPPXXX', address='{\"line_one\":\"1 RUE DE LA GASTRONOMIE\",\"postcode\":\"75001\",\"city\":\"PARIS\",\"country_code\":\"FR\"}' WHERE siren='000000001';" \
    || log "  (warn) update identité Tricatel — voir $LOG"
)
seed

# ---- 6. URLs + marche à suivre --------------------------------------------
WEB_PORT="$(env_value STAGING_WEB_PORT)"; WEB_PORT="${WEB_PORT:-47280}"
MINIO_CONSOLE_PORT="$(env_value STAGING_MINIO_CONSOLE_PORT)"; MINIO_CONSOLE_PORT="${MINIO_CONSOLE_PORT:-47291}"
cat <<EOF

[init] 6/6 OK — stack Factur-E démarrée.

  URLs locales :
    - Application (SPA)   → http://localhost:${WEB_PORT}/
    - API santé           → http://localhost:${API_PORT}/health
    - MinIO console       → http://localhost:${MINIO_CONSOLE_PORT}/

  Comptes de test pré-seedés (se connecter dans le navigateur via quick-login
  same-origin — pose le cookie de session côté SPA) :
    - Burger Queen (émetteur) :
        http://localhost:${WEB_PORT}/__dev/quick-login?email=bq@dev.factur-e.local
    - Tricatel (acheteur/destinataire) :
        http://localhost:${WEB_PORT}/__dev/quick-login?email=tricatel@dev.factur-e.local

  Connecter chaque compte à SuperPDP (canal OAuth réel) :
    une fois connecté, ouvrir le menu PA dans l'UI → "Connecter ma plateforme"
    → redirection SuperPDP → consentement → retour same-origin. Nécessite
    SUPERPDP_CLIENT_ID/SECRET renseignés + le callback enregistré côté sandbox.

  Récupérer le dernier email (OTP de connexion, notifications) — EMAIL_ADAPTER=mock :
    curl -s 'http://localhost:${API_PORT}/__dev/last-email?to=bq@dev.factur-e.local'

  Logs    : ${COMPOSE[*]} logs -f api
  Statut  : ${COMPOSE[*]} ps
  Arrêt   : ${COMPOSE[*]} down          (préserve les données)
  Reset   : ${COMPOSE[*]} down -v       (perd BDD + MinIO)

  Guide complet : README.md
EOF

trap - EXIT
