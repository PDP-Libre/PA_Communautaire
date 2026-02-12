# Test de conformité API Swagger (XP Z12-013)

Outil de validation de la conformité d'une API Swagger/OpenAPI avec la norme AFNOR XP Z12-013.

## Principe

Compare le swagger exposé par une PA avec les fichiers de référence AFNOR :

| Service | Référence AFNOR | Routes |
|---------|-----------------|--------|
| Flow Service | Annexe A - `AFNOR-Flow_Service-1.1.0-swagger.json` | `/flows`, `/flows/search`, `/flows/{flowId}`, `/healthcheck` |
| Directory Service | Annexe B - `AFNOR-Directory_Service-1.1.0-swagger.json` | `/siren`, `/siret`, `/routing-code`, `/directory-line`, `/healthcheck` |

## Points de contrôle

- Version OpenAPI (2.x / 3.x)
- Section info (title, version)
- Authentification Bearer (XP Z12-013 §5)
- Présence du healthcheck (XP Z12-013 §4.4)
- Présence de chaque endpoint de la norme

## Lancement

### Via pac-cli

```bash
cd packages/pac0-cli

# Flow Service (défaut)
uv run pac test swagger http://localhost:8000/openapi.json

# Directory Service
uv run pac test swagger http://localhost:8000/openapi.json --service directory

# Aide
uv run pac test swagger --help
```

### Mode standalone

```bash
cd packages/pac0-cli

# Flow Service (défaut)
uv run python -m pac0.cli.lib.swagger_validator http://localhost:8000/openapi.json

# Directory Service
uv run python -m pac0.cli.lib.swagger_validator http://localhost:8000/openapi.json directory

# Aide
uv run python -m pac0.cli.lib.swagger_validator --help
```

## Exemple de sortie

```
Validation swagger FLOW Service...
URL: http://localhost:8000/openapi.json
--------------------------------------------------
✅ Version OpenAPI: 3.1.0
✅ Info.title: FastAPI
✅ Info.version: 0.1.0
❌ Sécurité Bearer: MANQUANT - authentification Bearer requise (XP Z12-013 §5)
✅ Healthcheck: présent (/healthcheck)
✅ GET /v1/flows/{flowId}: présent
✅ GET /v1/healthcheck: présent
✅ POST /v1/flows: présent
❌ POST /v1/flows/search: MANQUANT
--------------------------------------------------
❌ 7/9 tests passés - NON CONFORME
```

## Code de retour

| Code | Signification |
|------|---------------|
| `0` | Conforme |
| `1` | Non conforme |

## Fichiers source

| Fichier | Description |
|---------|-------------|
| `packages/pac0-cli/src/pac0/cli/command/test.py` | Commande CLI |
| `packages/pac0-cli/src/pac0/cli/lib/swagger_validator.py` | Module de validation |
