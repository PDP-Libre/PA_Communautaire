# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import os

def test_openapi():
    url = os.environ.get("API_DOC_URL", "http://01-api-gateway:8000/openapi.json")

    # Vérifier si le fichier OpenApi est conforme à la spécification OpenAPI
    try:
        from openapi_spec_validator import validate_url

        validate_url(url)
    except ValueError as e:
        raise ValueError(
            f"Le fichier OpenApi {url} n'est pas conforme à la spécification OpenAPI: {e}"
        )
