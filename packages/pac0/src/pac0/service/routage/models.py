"""
Modèles de données pour le service de routage.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RoutingStatus(str, Enum):
    """Statuts de routage possibles."""

    ROUTED = "routed"  # Transmis via AS4 à une PA distante
    ROUTED_TO_PPF = "routed_to_ppf"  # Transmis au PPF (fallback)
    DELIVERED = "delivered"  # Livré localement
    ERROR = "error"  # Erreur de routage
    PENDING = "pending"  # En attente de retry


class InvoiceMessage(BaseModel):
    """Message de facture entrant pour le routage."""

    invoice_id: str = Field(..., description="Identifiant unique de la facture")
    sender_siren: str = Field(..., description="SIREN de l'émetteur")
    sender_siret: Optional[str] = Field(None, description="SIRET de l'émetteur")
    recipient_siren: str = Field(..., description="SIREN du destinataire")
    recipient_siret: Optional[str] = Field(None, description="SIRET du destinataire")
    document_type: str = Field(
        default="invoice_ubl", description="Type de document PEPPOL"
    )
    payload: str = Field(..., description="Contenu de la facture (XML)")
    local_recipient: bool = Field(
        default=False, description="True si le destinataire est local"
    )


class RoutingResult(BaseModel):
    """Résultat du routage d'une facture."""

    invoice_id: str = Field(..., description="Identifiant de la facture")
    status: RoutingStatus = Field(..., description="Statut du routage")
    destination: Optional[str] = Field(
        None, description="URL de destination (endpoint AS4 ou PPF)"
    )
    error_code: Optional[str] = Field(None, description="Code erreur si échec")
    error_message: Optional[str] = Field(None, description="Message d'erreur si échec")
    peppol_lookup_success: Optional[bool] = Field(
        None, description="True si le lookup PEPPOL a réussi"
    )


class AS4TransmissionResult(BaseModel):
    """Résultat d'une transmission AS4."""

    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
