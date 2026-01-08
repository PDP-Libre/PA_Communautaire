"""
Service de découverte PEPPOL via SML/SMP.

Ce module implémente le lookup PEPPOL pour déterminer quelle PA
a autorité pour une entreprise donnée.
"""

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from urllib.parse import quote

import httpx


class PeppolEnvironment(Enum):
    """Environnements PEPPOL disponibles."""

    PRODUCTION = "edelivery.tech.ec.europa.eu"
    TEST = "acc.edelivery.tech.ec.europa.eu"


class PeppolScheme(Enum):
    """Schemes d'identification PEPPOL pour la France."""

    SIREN = "0009"  # 9 chiffres
    SIRET = "0002"  # 14 chiffres
    TVA_FR = "9957"  # FR + 11 caractères


@dataclass
class PeppolEndpoint:
    """Représente un endpoint PEPPOL découvert."""

    address: str
    certificate: str
    transport_profile: str
    service_description: Optional[str] = None
    technical_contact_url: Optional[str] = None


@dataclass
class PeppolLookupResult:
    """Résultat d'un lookup PEPPOL."""

    success: bool
    endpoint: Optional[PeppolEndpoint] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    smp_url: Optional[str] = None


# Document types PEPPOL courants
PEPPOL_DOCUMENT_TYPES = {
    "invoice_ubl": (
        "busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:"
        "Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#"
        "urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1"
    ),
    "invoice_cii": (
        "busdox-docid-qns::urn:un:unece:uncefact:data:standard:"
        "CrossIndustryInvoice:100::CrossIndustryInvoice##"
        "urn:cen.eu:en16931:2017#compliant#"
        "urn:fdc:peppol.eu:2017:poacc:billing:3.0::D16B"
    ),
    "credit_note": (
        "busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:"
        "CreditNote-2::CreditNote##urn:cen.eu:en16931:2017#compliant#"
        "urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1"
    ),
}


class PeppolLookupService:
    """
    Service de découverte PEPPOL via SML/SMP.

    Permet de déterminer quelle PA a autorité pour une entreprise donnée
    en interrogeant le réseau PEPPOL.
    """

    def __init__(
        self,
        environment: PeppolEnvironment = PeppolEnvironment.PRODUCTION,
        timeout: float = 30.0,
        dns_resolver: Optional[object] = None,
    ):
        """
        Initialise le service de lookup PEPPOL.

        Args:
            environment: Environnement PEPPOL (production ou test)
            timeout: Timeout en secondes pour les requêtes HTTP
            dns_resolver: Résolveur DNS optionnel (pour les tests)
        """
        self.sml_zone = environment.value
        self.environment = environment
        self.timeout = timeout
        self._dns_resolver = dns_resolver
        self._mock_smp_responses: dict = {}

    def _compute_participant_hash(self, scheme_id: str, participant_id: str) -> str:
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

    def compute_sml_hostname(self, scheme_id: str, participant_id: str) -> str:
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
        hash_value = self._compute_participant_hash(scheme_id, participant_id)
        return f"B-{hash_value}.iso6523-actorid-upis.{self.sml_zone}"

    def _resolve_smp_url_sync(self, hostname: str) -> Optional[str]:
        """
        Résout l'URL du SMP via DNS (synchrone).

        Tente d'abord NAPTR, puis fallback vers CNAME.

        Args:
            hostname: Hostname SML généré

        Returns:
            URL du SMP ou None si non trouvé
        """
        # Si un mock est configuré, l'utiliser
        if self._dns_resolver is not None:
            return self._dns_resolver(hostname)

        # Implémentation réelle avec dnspython
        try:
            import dns.resolver

            # Essayer NAPTR d'abord (nouvelle méthode)
            try:
                answers = dns.resolver.resolve(hostname, "NAPTR")
                for rdata in answers:
                    regexp = str(rdata.regexp)
                    if regexp.startswith("!^.*$!") and regexp.endswith("!"):
                        return regexp[6:-1]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                pass
            except Exception:
                pass

            # Fallback vers CNAME
            try:
                answers = dns.resolver.resolve(hostname, "CNAME")
                cname = str(answers[0].target).rstrip(".")
                return f"https://{cname}"
            except dns.resolver.NXDOMAIN:
                return None
            except Exception:
                return None

        except ImportError:
            # dnspython non disponible - mode dégradé
            return None

    def set_mock_smp_response(
        self,
        scheme_id: str,
        participant_id: str,
        smp_url: Optional[str],
        endpoint: Optional[PeppolEndpoint] = None,
        error_code: Optional[str] = None,
    ):
        """
        Configure une réponse SMP mockée pour les tests.

        Args:
            scheme_id: Scheme ID
            participant_id: Identifiant participant
            smp_url: URL du SMP
            endpoint: Endpoint à retourner (ou None pour simuler non trouvé)
            error_code: Code d'erreur à retourner (pour simuler des erreurs)
        """
        key = f"{scheme_id}::{participant_id}".lower()
        self._mock_smp_responses[key] = {
            "smp_url": smp_url,
            "endpoint": endpoint,
            "error_code": error_code,
        }

    def clear_mock_responses(self):
        """Supprime toutes les réponses mockées."""
        self._mock_smp_responses.clear()

    async def lookup(
        self,
        scheme_id: str,
        participant_id: str,
        document_type: str = "invoice_ubl",
    ) -> PeppolLookupResult:
        """
        Recherche l'endpoint PEPPOL pour un participant.

        Args:
            scheme_id: Scheme ID ("0009" pour SIREN, "0002" pour SIRET)
            participant_id: Identifiant (SIREN ou SIRET)
            document_type: Type de document (clé ou identifiant complet)

        Returns:
            PeppolLookupResult avec l'endpoint ou l'erreur
        """
        # Résoudre le document type si c'est une clé
        doc_type_id = PEPPOL_DOCUMENT_TYPES.get(document_type, document_type)

        # Vérifier si une réponse mockée existe
        key = f"{scheme_id}::{participant_id}".lower()
        if key in self._mock_smp_responses:
            mock = self._mock_smp_responses[key]
            # Vérifier si une erreur est configurée
            if mock.get("error_code"):
                error_messages = {
                    "SMP_UNAVAILABLE": "SMP temporairement indisponible",
                    "SMP_TIMEOUT": "Timeout lors de la requête SMP",
                    "PARTICIPANT_NOT_FOUND": f"Participant non trouvé dans le SML",
                }
                return PeppolLookupResult(
                    success=False,
                    error_code=mock["error_code"],
                    error_message=error_messages.get(
                        mock["error_code"], f"Erreur: {mock['error_code']}"
                    ),
                    smp_url=mock.get("smp_url"),
                )
            if mock["endpoint"]:
                return PeppolLookupResult(
                    success=True,
                    endpoint=mock["endpoint"],
                    smp_url=mock["smp_url"],
                )
            else:
                return PeppolLookupResult(
                    success=False,
                    error_code="DOCUMENT_TYPE_NOT_SUPPORTED",
                    error_message=f"Le participant ne supporte pas le document type {document_type}",
                    smp_url=mock["smp_url"],
                )

        # Étape 1: Générer le hostname SML
        hostname = self.compute_sml_hostname(scheme_id, participant_id)

        # Étape 2: Résoudre l'URL du SMP via DNS
        smp_url = self._resolve_smp_url_sync(hostname)

        if not smp_url:
            return PeppolLookupResult(
                success=False,
                error_code="PARTICIPANT_NOT_FOUND",
                error_message=f"Participant {scheme_id}::{participant_id} non trouvé dans le SML",
            )

        # Étape 3: Requête HTTP vers le SMP
        try:
            endpoint = await self._fetch_smp_metadata(
                smp_url, scheme_id, participant_id, doc_type_id
            )

            if endpoint:
                return PeppolLookupResult(
                    success=True,
                    endpoint=endpoint,
                    smp_url=smp_url,
                )
            else:
                return PeppolLookupResult(
                    success=False,
                    error_code="DOCUMENT_TYPE_NOT_SUPPORTED",
                    error_message=f"Le participant ne supporte pas le document type {document_type}",
                    smp_url=smp_url,
                )

        except httpx.TimeoutException:
            return PeppolLookupResult(
                success=False,
                error_code="SMP_TIMEOUT",
                error_message="Timeout lors de la requête SMP",
                smp_url=smp_url,
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                return PeppolLookupResult(
                    success=False,
                    error_code="SMP_UNAVAILABLE",
                    error_message="SMP temporairement indisponible",
                    smp_url=smp_url,
                )
            return PeppolLookupResult(
                success=False,
                error_code="SMP_ERROR",
                error_message=f"Erreur SMP: {e.response.status_code}",
                smp_url=smp_url,
            )
        except Exception as e:
            return PeppolLookupResult(
                success=False,
                error_code="SMP_ERROR",
                error_message=str(e),
                smp_url=smp_url,
            )

    async def _fetch_smp_metadata(
        self,
        smp_url: str,
        scheme_id: str,
        participant_id: str,
        document_type_id: str,
    ) -> Optional[PeppolEndpoint]:
        """
        Récupère les métadonnées depuis le SMP.

        Args:
            smp_url: URL de base du SMP
            scheme_id: Scheme ID
            participant_id: Identifiant participant
            document_type_id: Type de document PEPPOL

        Returns:
            PeppolEndpoint ou None si non trouvé
        """
        participant_identifier = f"iso6523-actorid-upis::{scheme_id}::{participant_id}"
        encoded_doc_type = quote(document_type_id, safe="")

        url = f"{smp_url}/{participant_identifier}/services/{encoded_doc_type}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers={"Accept": "application/xml"})

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return self._parse_smp_response(response.text)

    def _parse_smp_response(self, xml_content: str) -> Optional[PeppolEndpoint]:
        """
        Parse la réponse XML du SMP.

        Args:
            xml_content: Contenu XML de la réponse SMP

        Returns:
            PeppolEndpoint extrait ou None
        """
        import xml.etree.ElementTree as ET

        namespaces = {
            "smp": "http://busdox.org/serviceMetadata/publishing/1.0/",
            "wsa": "http://www.w3.org/2005/08/addressing",
        }

        try:
            root = ET.fromstring(xml_content)

            # Chercher l'endpoint AS4
            endpoint = root.find(
                './/smp:Endpoint[@transportProfile="peppol-transport-as4-v2_0"]',
                namespaces,
            )

            if endpoint is None:
                # Essayer sans namespace
                for elem in root.iter():
                    if "Endpoint" in elem.tag:
                        if elem.get("transportProfile") == "peppol-transport-as4-v2_0":
                            endpoint = elem
                            break

            if endpoint is None:
                return None

            # Extraire l'adresse
            address = None
            for child in endpoint.iter():
                if "Address" in child.tag:
                    address = child.text
                    break

            # Extraire le certificat
            certificate = None
            for child in endpoint.iter():
                if "Certificate" in child.tag:
                    certificate = child.text
                    break

            # Extraire la description
            description = None
            for child in endpoint.iter():
                if "ServiceDescription" in child.tag:
                    description = child.text
                    break

            if address is None or certificate is None:
                return None

            return PeppolEndpoint(
                address=address,
                certificate=certificate,
                transport_profile="peppol-transport-as4-v2_0",
                service_description=description,
            )

        except ET.ParseError:
            return None

    async def lookup_by_siren(
        self, siren: str, document_type: str = "invoice_ubl"
    ) -> PeppolLookupResult:
        """
        Raccourci pour lookup par SIREN.

        Args:
            siren: Numéro SIREN (9 chiffres)
            document_type: Type de document

        Returns:
            PeppolLookupResult
        """
        return await self.lookup(PeppolScheme.SIREN.value, siren, document_type)

    async def lookup_by_siret(
        self, siret: str, document_type: str = "invoice_ubl"
    ) -> PeppolLookupResult:
        """
        Raccourci pour lookup par SIRET.

        Args:
            siret: Numéro SIRET (14 chiffres)
            document_type: Type de document

        Returns:
            PeppolLookupResult
        """
        return await self.lookup(PeppolScheme.SIRET.value, siret, document_type)
