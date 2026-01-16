# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from enum import Enum
import hashlib


class PeppolEnvironment(Enum):
    """Environnements PEPPOL disponibles."""

    PRODUCTION = "edelivery.tech.ec.europa.eu"
    TEST = "acc.edelivery.tech.ec.europa.eu"


class PeppolScheme(Enum):
    """Schemes d'identification PEPPOL pour la France."""

    SIREN = "0009"  # 9 chiffres
    SIRET = "0002"  # 14 chiffres
    TVA_FR = "9957"  # FR + 11 caractères


def compute_participant_hash(scheme_id: str, participant_id: str) -> str:
    """
    Calcule le hash MD5 de l'identifiant participant PEPPOL.

    Args:
        scheme_id: Scheme ID (ex: "0009" pour SIREN)
        participant_id: Identifiant (ex: "123456789")

    Returns:
        Hash MD5 en hexadécimal
    """
    full_id = f"{scheme_id}::{participant_id}".lower()
    return hashlib.md5(full_id.encode("utf-8")).hexdigest()


def compute_sml_hostname(
    sml_zone: str,
    scheme_id: str,
    participant_id: str,
) -> str:
    """
    Génère le hostname SML pour un participant PEPPOL.

    Algorithme:
    1. Construire l'identifiant: "{scheme_id}::{participant_id}"
    2. Convertir en minuscules
    3. Calculer le hash MD5
    4. Construire: "B-{hash}.iso6523-actorid-upis.{sml_zone}"

    Args:
        scheme_id: Scheme ID (ex: "0009")
        participant_id: Identifiant (ex: "123456789")

    Returns:
        Hostname SML complet
    """
    hash_value = compute_participant_hash(scheme_id, participant_id)
    return f"B-{hash_value}.iso6523-actorid-upis.{sml_zone}"
