# SPDX-FileCopyrightText: 2026 PA Communautaire
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Step definitions BDD pour la conformité API Swagger XP Z12-013.

Vérifie que le swagger exposé par l'API Gateway est conforme
aux références AFNOR (Flow Service et Directory Service).

Valide directement contre les swaggers de référence AFNOR
sans dépendance à pac0-cli.
"""

import json
import re
from pathlib import Path

import httpx
import pytest
from pytest_bdd import parsers, then, when

from pac0.shared.test.world import WorldContext, world1


# Racine du projet (pour trouver les fichiers de référence AFNOR)
PROJECT_ROOT = Path(__file__).resolve().parents[4]

REFERENCE_FILES = {
    "flow": PROJECT_ROOT / "docs/norme/XP_Z12-013_SWAGGER_Annexes_A_et_B_V1.2/ANNEXE A - PR XP Z12-013 - AFNOR-Flow_Service-1.1.0-swagger.json",
    "directory": PROJECT_ROOT / "docs/norme/XP_Z12-013_SWAGGER_Annexes_A_et_B_V1.2/ANNEXE B - PR XP Z12-013 - AFNOR-Directory_Service-1.1.0-swagger.json",
}


def _normalize_path(path: str) -> str:
    """Normalise un chemin pour la comparaison (ignore le préfixe de version)."""
    return re.sub(r"^/(?:api/)?v\d+", "", path)


def _extract_endpoints(swagger: dict) -> set[tuple[str, str]]:
    """Extrait les endpoints (méthode, chemin normalisé) d'un swagger."""
    endpoints = set()
    for path, methods in swagger.get("paths", {}).items():
        for method in methods.keys():
            if method.lower() not in ("parameters", "servers", "summary", "description"):
                endpoints.add((method.upper(), _normalize_path(path)))
    return endpoints


def _validate_against_reference(target_url: str, service_type: str) -> dict:
    """Valide un swagger distant contre le fichier de référence AFNOR."""
    ref_path = REFERENCE_FILES.get(service_type)
    if ref_path is None:
        return {"success": False, "errors": [f"Pas de référence pour le service '{service_type}'"]}

    # Charger la référence AFNOR
    with open(ref_path, encoding="utf-8") as f:
        reference = json.load(f)

    # Récupérer le swagger de la PA
    response = httpx.get(target_url, timeout=10)
    target = response.json()

    errors = []
    ok = []

    # Vérifier la version OpenAPI
    version = target.get("openapi", target.get("swagger", ""))
    if version.startswith(("2.", "3.")):
        ok.append(f"Version OpenAPI: {version}")
    else:
        errors.append("Version OpenAPI non détectée")

    # Vérifier la sécurité Bearer
    components = target.get("components", {})
    security_schemes = components.get("securitySchemes", target.get("securityDefinitions", {}))
    has_bearer = any(
        "bearer" in s.get("type", "").lower()
        or "bearer" in s.get("scheme", "").lower()
        or (s.get("type") == "apiKey" and s.get("in") == "header")
        for s in security_schemes.values()
    ) if security_schemes else False
    if has_bearer:
        ok.append("Sécurité Bearer: défini")
    else:
        errors.append("Sécurité Bearer: MANQUANT (XP Z12-013 §5)")

    # Vérifier les endpoints de la référence AFNOR dans le target
    ref_endpoints = _extract_endpoints(reference)
    target_endpoints = _extract_endpoints(target)

    for method, norm_path in sorted(ref_endpoints):
        if (method, norm_path) in target_endpoints:
            ok.append(f"{method} {norm_path}: présent")
        else:
            errors.append(f"{method} {norm_path}: MANQUANT")

    total = len(ok) + len(errors)
    return {
        "success": len(errors) == 0,
        "ok": ok,
        "errors": errors,
        "summary": f"{len(ok)}/{total} tests passés",
    }


@pytest.fixture
def swagger_report():
    """Stocke le rapport de validation swagger."""
    return {}


@when(
    parsers.parse('je vérifie la conformité swagger "{service_type}"'),
    target_fixture="swagger_report",
)
def _(
    world1: WorldContext,
    service_type: str,
):
    api_url = f"{world1.pa1.api_gateway.url}/openapi.json"
    return _validate_against_reference(api_url, service_type)


@then("le swagger est conforme")
def _(
    swagger_report: dict,
):
    assert swagger_report["success"], (
        f"Swagger non conforme ({swagger_report['summary']}):\n"
        + "\n".join(f"  ❌ {e}" for e in swagger_report["errors"])
    )
