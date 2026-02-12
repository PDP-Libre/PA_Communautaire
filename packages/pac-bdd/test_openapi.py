# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from pathlib import Path

from pac0.shared.test.world import world1  # noqa: F401 (pytest fixture)

# Chemin vers le package pac0-cli (relatif depuis pac-bdd)
PAC0_CLI_DIR = Path(__file__).resolve().parent.parent / "pac0-cli"


def _test_swagger(url: str, service_type: str):
    """
    Vérifier si une API respecte une definition Swagger/OpenAPI
    en appelant le validateur de pac0-cli en mode standalone.

    Cette API doit respecter le versioning indiqué dans l'URL de la route API du Swagger. Dans un objectif de
    simplification le versioning des routes n'est pas affiché dans le présent document;
    Dans cette API publiée par le Fournisseur API ce dernier peut :
    •Avoir une URL spécifique en amont du versioning
    •Ajouter des propriétés aux objets dans les requêtes.
    •Ajouter des paramètres aux routes dans les requêtes.
    •Ajouter des propriétés aux objets dans les réponses.
    •Ajouter des codes erreurs dans les réponses.
    """
    result = subprocess.run(
        ["uv", "run", "python", "-m", "pac0.cli.lib.swagger_validator", url, service_type],
        cwd=PAC0_CLI_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"{service_type.upper()} Service non conforme:\n{result.stdout}{result.stderr}"
    )


def test_swagger_flow_service(world1):
    url = f"{world1.pa1.api_gateway.url}/openapi.json"
    _test_swagger(url, "flow")


def test_swagger_directory_service(world1):
    url = f"{world1.pa1.api_gateway.url}/openapi.json"
    _test_swagger(url, "directory")
