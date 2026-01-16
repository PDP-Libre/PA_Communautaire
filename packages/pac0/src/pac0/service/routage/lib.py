# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Service de routage - Logique métier et handlers NATS.

Ce module implémente le routage des factures vers les PA distantes
via PEPPOL ou vers le PPF en fallback.
"""

from typing import Optional


from pac0.shared.esb import QUEUE

from .models import InvoiceMessage, RoutingResult, RoutingStatus
from .peppol import PeppolEndpoint, PeppolEnvironment, PeppolLookupService


# URL du PPF pour le fallback
PPF_API_URL = "https://api.ppf.gouv.fr"


# Service PEPPOL (singleton)
_peppol_service: Optional[PeppolLookupService] = None


def get_peppol_service() -> PeppolLookupService:
    """Retourne le service PEPPOL (singleton)."""
    global _peppol_service
    if _peppol_service is None:
        _peppol_service = PeppolLookupService(environment=PeppolEnvironment.PRODUCTION)
    return _peppol_service


def set_peppol_service(service: PeppolLookupService):
    """Configure le service PEPPOL (pour les tests)."""
    global _peppol_service
    _peppol_service = service


async def route_invoice(message: InvoiceMessage) -> RoutingResult:
    """
    Route une facture vers la destination appropriée.

    Logique de routage:
    1. Si le destinataire est local, ne pas router (erreur)
    2. Sinon, lookup PEPPOL pour trouver la PA du destinataire
    3. Si trouvé, transmettre via AS4
    4. Sinon, fallback vers le PPF

    Args:
        message: Message de facture à router

    Returns:
        RoutingResult avec le statut et la destination
    """
    peppol_service = get_peppol_service()

    # Lookup PEPPOL pour le destinataire
    if message.recipient_siret:
        result = await peppol_service.lookup_by_siret(
            message.recipient_siret, document_type=message.document_type
        )
    else:
        result = await peppol_service.lookup_by_siren(
            message.recipient_siren, document_type=message.document_type
        )

    if result.success and result.endpoint:
        # Participant trouvé sur PEPPOL - transmettre via AS4
        # TODO: Implémenter la transmission AS4 réelle
        return RoutingResult(
            invoice_id=message.invoice_id,
            status=RoutingStatus.ROUTED,
            destination=result.endpoint.address,
            peppol_lookup_success=True,
        )

    elif result.error_code == "PARTICIPANT_NOT_FOUND":
        # Fallback vers PPF
        # TODO: Implémenter la transmission vers PPF
        return RoutingResult(
            invoice_id=message.invoice_id,
            status=RoutingStatus.ROUTED_TO_PPF,
            destination=PPF_API_URL,
            peppol_lookup_success=False,
        )

    else:
        # Erreur de routage (timeout, SMP indisponible, etc.)
        return RoutingResult(
            invoice_id=message.invoice_id,
            status=RoutingStatus.ERROR,
            error_code=result.error_code,
            error_message=result.error_message,
            peppol_lookup_success=False,
        )


@router.subscriber(SUBJECT_IN, QUEUE)
async def process(message):
    """
    Handler principal du service de routage.

    Reçoit les factures depuis routage-IN et les route vers
    la destination appropriée.
    """
    try:
        # Parser le message si c'est un dict
        if isinstance(message, dict):
            invoice_message = InvoiceMessage(**message)
        elif isinstance(message, InvoiceMessage):
            invoice_message = message
        else:
            # Message simple (legacy) - créer un message minimal
            invoice_message = InvoiceMessage(
                invoice_id="unknown",
                sender_siren="000000000",
                recipient_siren="000000000",
                payload=str(message),
            )

        # Router la facture
        routing_result = await route_invoice(invoice_message)

        # Publier le résultat
        if routing_result.status == RoutingStatus.ERROR:
            await publisher_err.publish(
                routing_result.model_dump(), correlation_id=message.correlation_id
            )
        else:
            await publisher_out.publish(
                routing_result.model_dump(), correlation_id=message.correlation_id
            )

    except Exception as e:
        # Erreur inattendue
        error_result = RoutingResult(
            invoice_id=getattr(message, "invoice_id", "unknown"),
            status=RoutingStatus.ERROR,
            error_code="INTERNAL_ERROR",
            error_message=str(e),
        )
        await publisher_err.publish(
            error_result.model_dump(), correlation_id=message.correlation_id
        )
