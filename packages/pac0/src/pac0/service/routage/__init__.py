"""
Service de routage PEPPOL.

Ce package implémente le routage des factures vers les PA distantes
via le réseau PEPPOL ou vers le PPF en fallback.
"""

from .lib import (
    SUBJECT_IN,
    SUBJECT_OUT,
    SUBJECT_ERR,
    router,
    route_invoice,
    get_peppol_service,
    set_peppol_service,
)
from .models import (
    InvoiceMessage,
    RoutingResult,
    RoutingStatus,
)
from .peppol import (
    PeppolLookupService,
    PeppolEnvironment,
    PeppolScheme,
    PeppolEndpoint,
    PeppolLookupResult,
    PEPPOL_DOCUMENT_TYPES,
)

__all__ = [
    # Sujets NATS
    "SUBJECT_IN",
    "SUBJECT_OUT",
    "SUBJECT_ERR",
    # Router
    "router",
    # Fonctions
    "route_invoice",
    "get_peppol_service",
    "set_peppol_service",
    # Modèles
    "InvoiceMessage",
    "RoutingResult",
    "RoutingStatus",
    # PEPPOL
    "PeppolLookupService",
    "PeppolEnvironment",
    "PeppolScheme",
    "PeppolEndpoint",
    "PeppolLookupResult",
    "PEPPOL_DOCUMENT_TYPES",
]
