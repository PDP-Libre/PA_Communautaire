# SPDX-FileCopyrightText: 2026 PA Communautaire
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Validateur de conformité Swagger/OpenAPI selon XP Z12-013.

Compare un swagger distant avec les références AFNOR :
- Flow Service (Annexe A)
- Directory Service (Annexe B)
"""

import json
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import urllib.request
import urllib.error


class ServiceType(str, Enum):
    FLOW = "flow"
    DIRECTORY = "directory"


@dataclass
class TestResult:
    """Résultat d'un test individuel."""
    passed: bool
    name: str
    message: str

    def __str__(self) -> str:
        icon = "✅" if self.passed else "❌"
        return f"{icon} {self.name}: {self.message}"


@dataclass
class ValidationReport:
    """Rapport de validation complet."""
    service_type: ServiceType
    target_url: str
    results: list[TestResult]

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def total_count(self) -> int:
        return len(self.results)

    @property
    def success(self) -> bool:
        return all(r.passed for r in self.results)

    def __str__(self) -> str:
        lines = [f"Validation {self.service_type.value.upper()} Service"]
        lines.append(f"URL: {self.target_url}")
        lines.append("-" * 50)
        for result in self.results:
            lines.append(str(result))
        lines.append("-" * 50)
        lines.append(f"Résultat: {self.passed_count}/{self.total_count} tests passés")
        return "\n".join(lines)


class SwaggerValidator:
    """Validateur de conformité Swagger XP Z12-013."""

    # Chemins relatifs depuis la racine du projet
    REFERENCE_FILES = {
        ServiceType.FLOW: "docs/norme/XP_Z12-013_SWAGGER_Annexes_A_et_B_V1.2/ANNEXE A - PR XP Z12-013 - AFNOR-Flow_Service-1.1.0-swagger.json",
        ServiceType.DIRECTORY: "docs/norme/XP_Z12-013_SWAGGER_Annexes_A_et_B_V1.2/ANNEXE B - PR XP Z12-013 - AFNOR-Directory_Service-1.1.0-swagger.json",
    }

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialise le validateur.

        Args:
            project_root: Racine du projet PA Communautaire.
                         Si None, tente de la détecter automatiquement.
        """
        if project_root is None:
            # Remonter depuis ce fichier jusqu'à trouver la racine
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / "docs" / "norme").exists():
                    project_root = parent
                    break
            if project_root is None:
                raise ValueError("Impossible de trouver la racine du projet")

        self.project_root = Path(project_root)
        self._reference_cache: dict[ServiceType, dict] = {}

    def _load_reference(self, service_type: ServiceType) -> dict:
        """Charge le fichier swagger de référence."""
        if service_type not in self._reference_cache:
            ref_path = self.project_root / self.REFERENCE_FILES[service_type]
            if not ref_path.exists():
                raise FileNotFoundError(f"Fichier de référence introuvable: {ref_path}")
            with open(ref_path, encoding="utf-8") as f:
                self._reference_cache[service_type] = json.load(f)
        return self._reference_cache[service_type]

    def _fetch_swagger(self, url: str) -> dict:
        """Télécharge un swagger depuis une URL."""
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise ConnectionError(f"Impossible de se connecter à {url}: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Réponse JSON invalide: {e}")

    def _extract_endpoints(self, swagger: dict) -> set[tuple[str, str]]:
        """Extrait les endpoints (méthode, chemin) d'un swagger."""
        endpoints = set()
        for path, methods in swagger.get("paths", {}).items():
            for method in methods.keys():
                if method.lower() not in ("parameters", "servers", "summary", "description"):
                    endpoints.add((method.upper(), path))
        return endpoints

    def _normalize_path(self, path: str) -> str:
        """Normalise un chemin pour la comparaison (ignore le préfixe de version)."""
        # Enlève le préfixe /v1 ou /api/v1 pour comparaison
        import re
        return re.sub(r"^/(?:api/)?v\d+", "", path)

    def _check_endpoint_presence(
        self,
        reference: dict,
        target: dict
    ) -> list[TestResult]:
        """Vérifie que les endpoints de référence sont présents."""
        results = []
        ref_endpoints = self._extract_endpoints(reference)
        target_endpoints = self._extract_endpoints(target)

        # Normaliser les chemins pour comparaison
        target_normalized = {
            (method, self._normalize_path(path))
            for method, path in target_endpoints
        }

        for method, path in sorted(ref_endpoints):
            norm_path = self._normalize_path(path)
            present = (method, norm_path) in target_normalized

            # Chercher aussi sans normalisation exacte (paramètres différents)
            if not present:
                # Vérifier si le chemin de base existe avec la même méthode
                base_path = norm_path.split("{")[0].rstrip("/")
                for t_method, t_path in target_normalized:
                    if t_method == method and t_path.startswith(base_path):
                        present = True
                        break

            results.append(TestResult(
                passed=present,
                name=f"{method} {path}",
                message="présent" if present else "MANQUANT"
            ))

        return results

    def _check_healthcheck(self, target: dict) -> TestResult:
        """Vérifie la présence du healthcheck."""
        for path in target.get("paths", {}).keys():
            if "healthcheck" in path.lower():
                return TestResult(True, "Healthcheck", f"présent ({path})")
        return TestResult(False, "Healthcheck", "MANQUANT - route /healthcheck requise")

    def _check_openapi_version(self, target: dict) -> TestResult:
        """Vérifie la version OpenAPI."""
        version = target.get("openapi", target.get("swagger", ""))
        if version.startswith("3."):
            return TestResult(True, "Version OpenAPI", f"{version}")
        elif version.startswith("2."):
            return TestResult(True, "Version Swagger", f"{version} (migration OpenAPI 3.x recommandée)")
        return TestResult(False, "Version OpenAPI", "version non détectée")

    def _check_info_section(self, target: dict) -> list[TestResult]:
        """Vérifie la section info du swagger."""
        results = []
        info = target.get("info", {})

        # Titre
        title = info.get("title", "")
        results.append(TestResult(
            passed=bool(title),
            name="Info.title",
            message=title if title else "MANQUANT"
        ))

        # Version
        version = info.get("version", "")
        results.append(TestResult(
            passed=bool(version),
            name="Info.version",
            message=version if version else "MANQUANT"
        ))

        return results

    def _check_security_definitions(self, target: dict) -> TestResult:
        """Vérifie les définitions de sécurité (Bearer token)."""
        # OpenAPI 3.x
        components = target.get("components", {})
        security_schemes = components.get("securitySchemes", {})

        # Swagger 2.x
        if not security_schemes:
            security_schemes = target.get("securityDefinitions", {})

        has_bearer = False
        for scheme in security_schemes.values():
            scheme_type = scheme.get("type", "")
            bearer_format = scheme.get("bearerFormat", scheme.get("scheme", ""))
            if "bearer" in scheme_type.lower() or "bearer" in bearer_format.lower():
                has_bearer = True
                break
            if scheme_type == "apiKey" and scheme.get("in") == "header":
                has_bearer = True
                break

        return TestResult(
            passed=has_bearer,
            name="Sécurité Bearer",
            message="défini" if has_bearer else "MANQUANT - authentification Bearer requise (XP Z12-013 §5)"
        )

    def validate(self, url: str, service_type: ServiceType) -> ValidationReport:
        """
        Valide un swagger distant contre la référence XP Z12-013.

        Args:
            url: URL du swagger à valider (ex: http://localhost:8000/openapi.json)
            service_type: Type de service (flow ou directory)

        Returns:
            ValidationReport avec tous les résultats de tests
        """
        results = []

        # Charger les données
        try:
            reference = self._load_reference(service_type)
        except FileNotFoundError as e:
            return ValidationReport(
                service_type=service_type,
                target_url=url,
                results=[TestResult(False, "Référence", str(e))]
            )

        try:
            target = self._fetch_swagger(url)
        except (ConnectionError, ValueError) as e:
            return ValidationReport(
                service_type=service_type,
                target_url=url,
                results=[TestResult(False, "Connexion", str(e))]
            )

        # Tests généraux
        results.append(self._check_openapi_version(target))
        results.extend(self._check_info_section(target))
        results.append(self._check_security_definitions(target))
        results.append(self._check_healthcheck(target))

        # Tests des endpoints
        results.extend(self._check_endpoint_presence(reference, target))

        return ValidationReport(
            service_type=service_type,
            target_url=url,
            results=results
        )


def validate_swagger(
    url: str,
    service_type: str = "flow",
    project_root: Optional[Path] = None
) -> ValidationReport:
    """
    Fonction utilitaire pour valider un swagger.

    Args:
        url: URL du swagger à valider
        service_type: "flow" ou "directory"
        project_root: Racine du projet (optionnel)

    Returns:
        ValidationReport
    """
    validator = SwaggerValidator(project_root)
    return validator.validate(url, ServiceType(service_type))


if __name__ == "__main__":
    import sys

    usage = "Usage: python -m pac0.cli.lib.swagger_validator <URL> [flow|directory]"

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(usage)
        print()
        print("Valide la conformité d'un swagger avec XP Z12-013.")
        print()
        print("Arguments:")
        print("  URL                  URL du swagger (ex: http://localhost:8000/openapi.json)")
        print("  flow|directory       Type de service (défaut: flow)")
        sys.exit(0)

    url = sys.argv[1]
    service = sys.argv[2] if len(sys.argv) > 2 else "flow"

    if service not in ("flow", "directory"):
        print(f"Erreur: service doit être 'flow' ou 'directory', pas '{service}'")
        sys.exit(1)

    report = validate_swagger(url, service)
    print(report)
    sys.exit(0 if report.success else 1)
