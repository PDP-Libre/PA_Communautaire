# Intégration PEPPOL pour le Routage

## 1. Introduction à PEPPOL

### 1.1 Qu'est-ce que PEPPOL ?

**PEPPOL** (Pan-European Public Procurement OnLine) est un réseau international standardisé pour l'échange de documents commerciaux électroniques. Il permet l'interopérabilité entre les plateformes de facturation électronique à travers l'Europe et au-delà.

Caractéristiques principales :
- **Architecture 4-Corner Model** : Émetteur → Access Point Émetteur → Access Point Récepteur → Destinataire
- **Protocole AS4** : Transport sécurisé des messages
- **Découverte dynamique** : Localisation automatique des participants via SML/SMP
- **Formats standardisés** : UBL, CII, Factur-X conformes à la norme EN16931

### 1.2 PEPPOL dans le contexte français

La **DGFiP** (Direction Générale des Finances Publiques) est devenue **Peppol Authority France** le 8 juillet 2025.

#### Calendrier de déploiement B2B

| Date | Obligation |
|------|------------|
| **1er septembre 2026** | - Toutes les entreprises doivent pouvoir **recevoir** des factures électroniques<br>- Les **grandes entreprises** doivent **émettre** des factures électroniques et transmettre les données e-reporting |
| **1er septembre 2027** | - Les **PME** doivent émettre des factures électroniques et transmettre les données e-reporting |

#### Acteurs clés

- **PPF** (Portail Public de Facturation) : Plateforme publique gérée par l'État
- **PDP** (Plateforme de Dématérialisation Partenaire) : Plateformes privées agréées
- **OD** (Opérateur de Dématérialisation) : Prestataires non agréés
- **Chorus Pro** : Portail B2G existant, intégré à PEPPOL via Pagero

#### Formats supportés en France

- Factur-X (PDF A/3)
- UBL EN16931 France CIUS
- UBL EN16931 France EXTENDED-CTC-FR
- UN/CEFACT EN16931 France CIUS
- UN/CEFACT EN16931 France EXTENDED-CTC-FR
- Peppol BIS 3.0

---

## 2. Architecture de découverte PEPPOL

### 2.1 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SML (Service Metadata Locator)              │
│                                                                     │
│  Fonction : Résolution DNS pour localiser le SMP d'un participant   │
│  Production : edelivery.tech.ec.europa.eu                           │
│  Test : acc.edelivery.tech.ec.europa.eu                             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Requête DNS (NAPTR/CNAME)
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SMP (Service Metadata Publisher)            │
│                                                                     │
│  Fonction : Fournit les métadonnées d'un participant                │
│  Contenu : Endpoint AS4, Certificat, Document Types supportés       │
│  Format : XML signé                                                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Requête HTTPS
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Peppol Directory (Optionnel)                │
│                                                                     │
│  Fonction : Annuaire public consultable                             │
│  URL : https://directory.peppol.eu                                  │
│  Usage : Recherche manuelle, export de données                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Identifiants PEPPOL pour la France

Les entreprises françaises sont identifiées par leur numéro SIREN ou SIRET dans le réseau PEPPOL.

| Scheme ID | Type | Format | Exemple |
|-----------|------|--------|---------|
| `0009` | SIREN | 9 chiffres | `0009::123456789` |
| `0002` | SIRET | 14 chiffres | `0002::12345678900012` |
| `9957` | TVA FR | FR + 11 caractères | `9957::FR12345678901` |

**Construction de l'identifiant participant PEPPOL :**

```
{scheme_id}::{identifier}
```

Exemple pour le SIREN 123456789 :
```
0009::123456789
```

---

## 3. Processus de découverte - Étapes détaillées

### 3.1 Étape 1 : Construire l'identifiant PEPPOL

À partir des informations de la facture, extraire le SIREN/SIRET du destinataire.

```python
def build_peppol_participant_id(siren: str = None, siret: str = None) -> tuple[str, str]:
    """
    Construit l'identifiant participant PEPPOL.
    
    Args:
        siren: Numéro SIREN (9 chiffres)
        siret: Numéro SIRET (14 chiffres)
    
    Returns:
        Tuple (scheme_id, participant_id)
    """
    if siret and len(siret) == 14:
        return ("0002", siret)
    elif siren and len(siren) == 9:
        return ("0009", siren)
    else:
        raise ValueError("SIREN ou SIRET invalide")

# Exemple
scheme_id, participant_id = build_peppol_participant_id(siren="123456789")
# Résultat: ("0009", "123456789")
```

### 3.2 Étape 2 : Requête DNS vers le SML

Le SML utilise le DNS pour mapper un identifiant participant vers l'URL de son SMP.

#### Algorithme de génération du hostname SML

```python
import hashlib

def compute_sml_hostname(scheme_id: str, participant_id: str, sml_zone: str) -> str:
    """
    Génère le hostname SML pour un participant PEPPOL.
    
    Algorithme:
    1. Construire l'identifiant complet: "{scheme_id}::{participant_id}"
    2. Convertir en minuscules
    3. Calculer le hash MD5
    4. Construire le hostname: "B-{hash}.iso6523-actorid-upis.{sml_zone}"
    
    Args:
        scheme_id: Scheme ID (ex: "0009")
        participant_id: Identifiant (ex: "123456789")
        sml_zone: Zone SML (ex: "edelivery.tech.ec.europa.eu")
    
    Returns:
        Hostname SML complet
    """
    # 1. Construire l'identifiant complet en minuscules
    full_id = f"{scheme_id}::{participant_id}".lower()
    
    # 2. Calculer le hash MD5
    md5_hash = hashlib.md5(full_id.encode('utf-8')).hexdigest()
    
    # 3. Construire le hostname
    hostname = f"B-{md5_hash}.iso6523-actorid-upis.{sml_zone}"
    
    return hostname


# Exemple d'utilisation
hostname = compute_sml_hostname(
    scheme_id="0009",
    participant_id="123456789",
    sml_zone="edelivery.tech.ec.europa.eu"
)
print(hostname)
# Résultat: "B-7f9b8c7e6d5a4b3c2d1e0f9a8b7c6d5e.iso6523-actorid-upis.edelivery.tech.ec.europa.eu"
```

#### Requête DNS

**Méthode NAPTR (obligatoire à partir de novembre 2025) :**

```bash
# Requête NAPTR
dig NAPTR B-{hash}.iso6523-actorid-upis.edelivery.tech.ec.europa.eu

# Exemple de réponse NAPTR
;; ANSWER SECTION:
B-{hash}.iso6523-actorid-upis.edelivery.tech.ec.europa.eu. 300 IN NAPTR 100 10 "U" "Meta:SMP" "!^.*$!https://smp.pdp-example.fr!" .
```

**Méthode CNAME (legacy, supportée jusqu'à migration complète) :**

```bash
# Requête CNAME
dig CNAME B-{hash}.iso6523-actorid-upis.edelivery.tech.ec.europa.eu

# Exemple de réponse CNAME
;; ANSWER SECTION:
B-{hash}.iso6523-actorid-upis.edelivery.tech.ec.europa.eu. 300 IN CNAME smp.pdp-example.fr.
```

#### Implémentation Python

```python
import dns.resolver
from typing import Optional

async def resolve_smp_url(hostname: str) -> Optional[str]:
    """
    Résout l'URL du SMP via DNS.
    
    Args:
        hostname: Hostname SML généré
    
    Returns:
        URL du SMP ou None si non trouvé
    """
    # Essayer d'abord NAPTR (nouvelle méthode)
    try:
        answers = dns.resolver.resolve(hostname, 'NAPTR')
        for rdata in answers:
            # Parser la réponse NAPTR pour extraire l'URL
            # Format: "!^.*$!https://smp.example.com!"
            regexp = str(rdata.regexp)
            if regexp.startswith("!^.*$!") and regexp.endswith("!"):
                url = regexp[6:-1]  # Extraire l'URL
                return url
    except dns.resolver.NXDOMAIN:
        return None
    except dns.resolver.NoAnswer:
        pass
    except Exception as e:
        print(f"Erreur NAPTR: {e}")
    
    # Fallback vers CNAME
    try:
        answers = dns.resolver.resolve(hostname, 'CNAME')
        cname = str(answers[0].target).rstrip('.')
        return f"https://{cname}"
    except dns.resolver.NXDOMAIN:
        return None
    except Exception as e:
        print(f"Erreur CNAME: {e}")
        return None
```

### 3.3 Étape 3 : Requête HTTP vers le SMP

Une fois l'URL du SMP obtenue, interroger le SMP pour récupérer les métadonnées du participant.

#### Construction de l'URL SMP

```
GET https://{smp_host}/{participant_identifier}/services/{document_type_id}
```

Où :
- `{smp_host}` : Hostname du SMP obtenu via DNS
- `{participant_identifier}` : `iso6523-actorid-upis::{scheme_id}::{participant_id}`
- `{document_type_id}` : Identifiant du type de document (URL-encoded)

#### Exemple de requête

```bash
# Document type pour une facture UBL
DOCUMENT_TYPE="busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1"

# Requête SMP
curl -X GET \
  "https://smp.pdp-example.fr/iso6523-actorid-upis::0009::123456789/services/${DOCUMENT_TYPE}" \
  -H "Accept: application/xml"
```

#### Réponse SMP (XML signé)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<smp:SignedServiceMetadata xmlns:smp="http://busdox.org/serviceMetadata/publishing/1.0/">
  <smp:ServiceMetadata>
    <smp:ServiceInformation>
      <smp:ParticipantIdentifier scheme="iso6523-actorid-upis">0009::123456789</smp:ParticipantIdentifier>
      <smp:DocumentIdentifier scheme="busdox-docid-qns">
        urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1
      </smp:DocumentIdentifier>
      <smp:ProcessList>
        <smp:Process>
          <smp:ProcessIdentifier scheme="cenbii-procid-ubl">
            urn:fdc:peppol.eu:2017:poacc:billing:01:1.0
          </smp:ProcessIdentifier>
          <smp:ServiceEndpointList>
            <smp:Endpoint transportProfile="peppol-transport-as4-v2_0">
              <wsa:EndpointReference xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsa:Address>https://ap.pdp-destinataire.fr/as4</wsa:Address>
              </wsa:EndpointReference>
              <smp:RequireBusinessLevelSignature>false</smp:RequireBusinessLevelSignature>
              <smp:Certificate>MIIFxTCCA62gAwIBAgIQT...base64...</smp:Certificate>
              <smp:ServiceDescription>PDP Destinataire - Access Point PEPPOL</smp:ServiceDescription>
              <smp:TechnicalContactUrl>https://pdp-destinataire.fr/support</smp:TechnicalContactUrl>
            </smp:Endpoint>
          </smp:ServiceEndpointList>
        </smp:Process>
      </smp:ProcessList>
    </smp:ServiceInformation>
  </smp:ServiceMetadata>
  <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
    <!-- Signature XML du SMP -->
  </ds:Signature>
</smp:SignedServiceMetadata>
```

#### Implémentation Python

```python
import httpx
from dataclasses import dataclass
from typing import Optional
import xml.etree.ElementTree as ET

@dataclass
class PeppolEndpoint:
    """Représente un endpoint PEPPOL découvert."""
    address: str
    certificate: str
    transport_profile: str
    service_description: Optional[str] = None
    technical_contact_url: Optional[str] = None


async def fetch_smp_metadata(
    smp_url: str,
    scheme_id: str,
    participant_id: str,
    document_type_id: str
) -> Optional[PeppolEndpoint]:
    """
    Récupère les métadonnées SMP pour un participant.
    
    Args:
        smp_url: URL de base du SMP
        scheme_id: Scheme ID (ex: "0009")
        participant_id: Identifiant participant (ex: "123456789")
        document_type_id: Type de document PEPPOL
    
    Returns:
        PeppolEndpoint ou None si non trouvé
    """
    # Construire l'URL complète
    participant_identifier = f"iso6523-actorid-upis::{scheme_id}::{participant_id}"
    
    # URL-encode le document type
    from urllib.parse import quote
    encoded_doc_type = quote(document_type_id, safe='')
    
    url = f"{smp_url}/{participant_identifier}/services/{encoded_doc_type}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers={"Accept": "application/xml"})
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            
            return parse_smp_response(response.text)
            
        except httpx.HTTPStatusError as e:
            print(f"Erreur HTTP SMP: {e.response.status_code}")
            return None
        except Exception as e:
            print(f"Erreur SMP: {e}")
            return None


def parse_smp_response(xml_content: str) -> Optional[PeppolEndpoint]:
    """
    Parse la réponse XML du SMP.
    
    Args:
        xml_content: Contenu XML de la réponse SMP
    
    Returns:
        PeppolEndpoint extrait ou None
    """
    namespaces = {
        'smp': 'http://busdox.org/serviceMetadata/publishing/1.0/',
        'wsa': 'http://www.w3.org/2005/08/addressing'
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        # Trouver l'endpoint AS4
        endpoint = root.find('.//smp:Endpoint[@transportProfile="peppol-transport-as4-v2_0"]', namespaces)
        
        if endpoint is None:
            return None
        
        address = endpoint.find('wsa:EndpointReference/wsa:Address', namespaces)
        certificate = endpoint.find('smp:Certificate', namespaces)
        description = endpoint.find('smp:ServiceDescription', namespaces)
        contact = endpoint.find('smp:TechnicalContactUrl', namespaces)
        
        if address is None or certificate is None:
            return None
        
        return PeppolEndpoint(
            address=address.text,
            certificate=certificate.text,
            transport_profile="peppol-transport-as4-v2_0",
            service_description=description.text if description is not None else None,
            technical_contact_url=contact.text if contact is not None else None
        )
        
    except ET.ParseError as e:
        print(f"Erreur parsing XML: {e}")
        return None
```

### 3.4 Étape 4 : Extraire les informations de la PA

Les informations clés extraites de la réponse SMP :

| Champ | XPath | Usage |
|-------|-------|-------|
| **Endpoint URL** | `//Endpoint/EndpointReference/Address` | URL de l'Access Point AS4 de la PA destinataire |
| **Certificat** | `//Endpoint/Certificate` | Certificat X.509 pour chiffrement et vérification |
| **Transport Profile** | `//Endpoint/@transportProfile` | Doit être `peppol-transport-as4-v2_0` |
| **Process ID** | `//Process/ProcessIdentifier` | Identifiant du processus métier |

---

## 4. Service complet de lookup PEPPOL

### 4.1 Implémentation complète

```python
import hashlib
import httpx
import dns.resolver
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class PeppolEnvironment(Enum):
    PRODUCTION = "edelivery.tech.ec.europa.eu"
    TEST = "acc.edelivery.tech.ec.europa.eu"


@dataclass
class PeppolEndpoint:
    """Endpoint PEPPOL découvert."""
    address: str
    certificate: str
    transport_profile: str
    service_description: Optional[str] = None


@dataclass
class PeppolLookupResult:
    """Résultat d'un lookup PEPPOL."""
    success: bool
    endpoint: Optional[PeppolEndpoint] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class PeppolLookupService:
    """
    Service de découverte PEPPOL via SML/SMP.
    
    Permet de déterminer quelle PA a autorité pour une entreprise donnée.
    """
    
    # Document types courants
    DOCUMENT_TYPES = {
        "invoice_ubl": "busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1",
        "invoice_cii": "busdox-docid-qns::urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100::CrossIndustryInvoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::D16B",
        "credit_note": "busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2::CreditNote##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1",
    }
    
    def __init__(self, environment: PeppolEnvironment = PeppolEnvironment.PRODUCTION):
        self.sml_zone = environment.value
        self.timeout = 30.0
    
    def _compute_sml_hostname(self, scheme_id: str, participant_id: str) -> str:
        """Calcule le hostname SML pour un participant."""
        full_id = f"{scheme_id}::{participant_id}".lower()
        md5_hash = hashlib.md5(full_id.encode('utf-8')).hexdigest()
        return f"B-{md5_hash}.iso6523-actorid-upis.{self.sml_zone}"
    
    def _resolve_smp_url_sync(self, hostname: str) -> Optional[str]:
        """Résout l'URL du SMP via DNS (synchrone)."""
        # Essayer NAPTR d'abord
        try:
            answers = dns.resolver.resolve(hostname, 'NAPTR')
            for rdata in answers:
                regexp = str(rdata.regexp)
                if regexp.startswith("!^.*$!") and regexp.endswith("!"):
                    return regexp[6:-1]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            pass
        except Exception:
            pass
        
        # Fallback CNAME
        try:
            answers = dns.resolver.resolve(hostname, 'CNAME')
            cname = str(answers[0].target).rstrip('.')
            return f"https://{cname}"
        except dns.resolver.NXDOMAIN:
            return None
        except Exception:
            return None
    
    async def lookup(
        self,
        scheme_id: str,
        participant_id: str,
        document_type: str = "invoice_ubl"
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
        doc_type_id = self.DOCUMENT_TYPES.get(document_type, document_type)
        
        # Étape 1: Générer le hostname SML
        hostname = self._compute_sml_hostname(scheme_id, participant_id)
        
        # Étape 2: Résoudre l'URL du SMP via DNS
        smp_url = self._resolve_smp_url_sync(hostname)
        
        if not smp_url:
            return PeppolLookupResult(
                success=False,
                error_code="PARTICIPANT_NOT_FOUND",
                error_message=f"Participant {scheme_id}::{participant_id} non trouvé dans le SML"
            )
        
        # Étape 3: Requête HTTP vers le SMP
        try:
            endpoint = await self._fetch_smp_metadata(
                smp_url, scheme_id, participant_id, doc_type_id
            )
            
            if endpoint:
                return PeppolLookupResult(success=True, endpoint=endpoint)
            else:
                return PeppolLookupResult(
                    success=False,
                    error_code="DOCUMENT_TYPE_NOT_SUPPORTED",
                    error_message=f"Le participant ne supporte pas le document type {document_type}"
                )
                
        except httpx.TimeoutException:
            return PeppolLookupResult(
                success=False,
                error_code="SMP_TIMEOUT",
                error_message="Timeout lors de la requête SMP"
            )
        except Exception as e:
            return PeppolLookupResult(
                success=False,
                error_code="SMP_ERROR",
                error_message=str(e)
            )
    
    async def _fetch_smp_metadata(
        self,
        smp_url: str,
        scheme_id: str,
        participant_id: str,
        document_type_id: str
    ) -> Optional[PeppolEndpoint]:
        """Récupère les métadonnées depuis le SMP."""
        from urllib.parse import quote
        
        participant_identifier = f"iso6523-actorid-upis::{scheme_id}::{participant_id}"
        encoded_doc_type = quote(document_type_id, safe='')
        
        url = f"{smp_url}/{participant_identifier}/services/{encoded_doc_type}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers={"Accept": "application/xml"})
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            return self._parse_smp_response(response.text)
    
    def _parse_smp_response(self, xml_content: str) -> Optional[PeppolEndpoint]:
        """Parse la réponse XML du SMP."""
        import xml.etree.ElementTree as ET
        
        namespaces = {
            'smp': 'http://busdox.org/serviceMetadata/publishing/1.0/',
            'wsa': 'http://www.w3.org/2005/08/addressing'
        }
        
        try:
            root = ET.fromstring(xml_content)
            endpoint = root.find('.//smp:Endpoint[@transportProfile="peppol-transport-as4-v2_0"]', namespaces)
            
            if endpoint is None:
                return None
            
            address = endpoint.find('wsa:EndpointReference/wsa:Address', namespaces)
            certificate = endpoint.find('smp:Certificate', namespaces)
            description = endpoint.find('smp:ServiceDescription', namespaces)
            
            if address is None or certificate is None:
                return None
            
            return PeppolEndpoint(
                address=address.text,
                certificate=certificate.text,
                transport_profile="peppol-transport-as4-v2_0",
                service_description=description.text if description is not None else None
            )
        except ET.ParseError:
            return None
    
    async def lookup_by_siren(self, siren: str, document_type: str = "invoice_ubl") -> PeppolLookupResult:
        """Raccourci pour lookup par SIREN."""
        return await self.lookup("0009", siren, document_type)
    
    async def lookup_by_siret(self, siret: str, document_type: str = "invoice_ubl") -> PeppolLookupResult:
        """Raccourci pour lookup par SIRET."""
        return await self.lookup("0002", siret, document_type)
```

### 4.2 Exemple d'utilisation

```python
import asyncio

async def main():
    # Créer le service de lookup
    lookup_service = PeppolLookupService(environment=PeppolEnvironment.PRODUCTION)
    
    # Rechercher un participant par SIREN
    result = await lookup_service.lookup_by_siren("123456789")
    
    if result.success:
        print(f"Participant trouvé!")
        print(f"  Endpoint: {result.endpoint.address}")
        print(f"  Transport: {result.endpoint.transport_profile}")
        print(f"  Description: {result.endpoint.service_description}")
    else:
        print(f"Participant non trouvé: {result.error_code}")
        print(f"  Message: {result.error_message}")

asyncio.run(main())
```

---

## 5. Interactions avec le service 07-routage

### 5.1 Flux de décision complet

```
                         ┌─────────────────────────┐
                         │   Facture validée       │
                         │   (06-annuaire-local)   │
                         └───────────┬─────────────┘
                                     │
                                     ▼
                         ┌─────────────────────────┐
                         │ Extraire SIREN/SIRET    │
                         │ du destinataire         │
                         └───────────┬─────────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────────┐
         ┌──────────│  Destinataire dans annuaire local? │──────────┐
         │ OUI      └────────────────────────────────────┘   NON    │
         │                                                          │
         ▼                                                          ▼
┌─────────────────────┐                              ┌──────────────────────────┐
│ Livraison locale    │                              │ 07-routage-IN            │
│ (08-transmission-   │                              │ Lookup PEPPOL            │
│  fiscale-IN)        │                              └───────────┬──────────────┘
└─────────────────────┘                                          │
                                                                 ▼
                                              ┌────────────────────────────────────┐
                                   ┌──────────│  Participant trouvé dans PEPPOL?   │──────────┐
                                   │ OUI      └────────────────────────────────────┘   NON    │
                                   │                                                          │
                                   ▼                                                          ▼
                    ┌──────────────────────────┐                          ┌──────────────────────────┐
                    │ Transmission AS4         │                          │ Routage vers PPF         │
                    │ vers PA distante         │                          │ (Portail Public de       │
                    │                          │                          │  Facturation)            │
                    │ - Endpoint: SMP.address  │                          │                          │
                    │ - Cert: SMP.certificate  │                          │ - API PPF                │
                    └───────────┬──────────────┘                          └───────────┬──────────────┘
                                │                                                      │
                                ▼                                                      ▼
                    ┌──────────────────────────┐                          ┌──────────────────────────┐
                    │ routage-OUT              │                          │ routage-OUT              │
                    │ status: "routed"         │                          │ status: "routed_to_ppf"  │
                    └──────────────────────────┘                          └──────────────────────────┘
```

### 5.2 Intégration dans le service de routage

```python
from pac0.shared.esb import init_esb_app, QUEUE
from pydantic import BaseModel
from typing import Optional


SUBJECT_IN = "routage-IN"
SUBJECT_OUT = "routage-OUT"
SUBJECT_ERR = "routage-ERR"

broker, app = init_esb_app()
publisher_out = broker.publisher(SUBJECT_OUT)
publisher_err = broker.publisher(SUBJECT_ERR)


class InvoiceMessage(BaseModel):
    invoice_id: str
    sender_siren: str
    recipient_siren: str
    recipient_siret: Optional[str] = None
    document_type: str
    payload: str


class RoutingResult(BaseModel):
    invoice_id: str
    status: str  # "routed", "routed_to_ppf", "error"
    destination: Optional[str] = None
    error_message: Optional[str] = None


# Service de lookup PEPPOL
peppol_lookup = PeppolLookupService(environment=PeppolEnvironment.PRODUCTION)


@broker.subscriber(SUBJECT_IN, QUEUE)
async def process(message: InvoiceMessage):
    """
    Traite une facture pour routage vers la PA appropriée.
    """
    # Lookup PEPPOL pour le destinataire
    if message.recipient_siret:
        result = await peppol_lookup.lookup_by_siret(
            message.recipient_siret,
            document_type=message.document_type
        )
    else:
        result = await peppol_lookup.lookup_by_siren(
            message.recipient_siren,
            document_type=message.document_type
        )
    
    if result.success:
        # Participant trouvé - transmettre via AS4
        routing_result = RoutingResult(
            invoice_id=message.invoice_id,
            status="routed",
            destination=result.endpoint.address
        )
        
        # TODO: Implémenter la transmission AS4
        # await transmit_as4(message.payload, result.endpoint)
        
        await publisher_out.publish(routing_result, correlation_id=message.correlation_id)
    
    elif result.error_code == "PARTICIPANT_NOT_FOUND":
        # Fallback vers PPF
        routing_result = RoutingResult(
            invoice_id=message.invoice_id,
            status="routed_to_ppf",
            destination="https://api.ppf.gouv.fr"
        )
        
        # TODO: Implémenter la transmission vers PPF
        # await transmit_to_ppf(message.payload)
        
        await publisher_out.publish(routing_result, correlation_id=message.correlation_id)
    
    else:
        # Erreur de routage
        routing_result = RoutingResult(
            invoice_id=message.invoice_id,
            status="error",
            error_message=result.error_message
        )
        await publisher_err.publish(routing_result, correlation_id=message.correlation_id)
```

### 5.3 Canaux NATS

| Canal | Direction | Format message | Description |
|-------|-----------|----------------|-------------|
| `routage-IN` | Entrée | `InvoiceMessage` | Facture à router |
| `routage-OUT` | Sortie | `RoutingResult` | Confirmation de routage |
| `routage-ERR` | Erreur | `RoutingResult` | Échec de routage |

---

## 6. Liens utiles

### Documentation technique PEPPOL (priorité haute)

| Ressource | URL | Description |
|-----------|-----|-------------|
| Spécifications eDelivery | https://docs.peppol.eu/edelivery/ | Index des spécifications SML, SMP, AS4 |
| SML Specification v1.3 | https://docs.peppol.eu/edelivery/sml/ | Service Metadata Locator |
| SMP Specification v1.4 | https://docs.peppol.eu/edelivery/smp/ | Service Metadata Publisher |
| Policy for Identifiers v4.4 | https://docs.peppol.eu/edelivery/policies/ | Règles d'utilisation des identifiants |
| AS4 Profile v2.0.3 | https://docs.peppol.eu/edelivery/as4/specification/ | Profil de transport AS4 |

### Contexte France (priorité haute)

| Ressource | URL | Description |
|-----------|-----|-------------|
| France Country Profile | https://peppol.org/learn-more/country-profiles/france/ | Contexte PEPPOL France |
| Documentation France PA | https://openpeppol.atlassian.net/wiki/spaces/FP/overview | Wiki PEPPOL France |
| Immatriculation PDP | https://www.impots.gouv.fr | Guide d'immatriculation PDP |
| Contact Peppol France | peppolfrance@dgfip.finances.gouv.fr | Support DGFiP |

### Outils et ressources (priorité moyenne)

| Ressource | URL | Description |
|-----------|-----|-------------|
| Peppol Directory | https://directory.peppol.eu | Annuaire public des participants |
| Peppol Testbed | https://peppol.org/tools-support/testbed/ | Environnement de test |
| Service Desk | https://openpeppol.atlassian.net/servicedesk/customer/portal/1 | Support technique |

### Normes et spécifications françaises

| Ressource | Emplacement | Description |
|-----------|-------------|-------------|
| AFNOR Directory Service API | `docs/norme/XP_Z12-013_SWAGGER_Annexes_A_et_B_V1.2/` | API de l'annuaire AFNOR |
| XP Z12-012 | `docs/norme/` | Spécification des échanges |
| XP Z12-013 | `docs/norme/` | Spécification de l'annuaire |
| XP Z12-014 | `docs/norme/` | Cas d'usage |

---

## 7. Glossaire

| Terme | Définition |
|-------|------------|
| **Access Point (AP)** | Point d'accès au réseau PEPPOL pour l'envoi et la réception de documents |
| **AS4** | Protocole de messagerie utilisé pour le transport sécurisé dans PEPPOL |
| **DGFiP** | Direction Générale des Finances Publiques |
| **PDP** | Plateforme de Dématérialisation Partenaire (plateforme privée agréée) |
| **PPF** | Portail Public de Facturation (plateforme publique) |
| **SBDH** | Standard Business Document Header (enveloppe des messages PEPPOL) |
| **Scheme ID** | Identifiant du schéma d'identification (ex: 0009 pour SIREN) |
| **SIREN** | Système d'Identification du Répertoire des Entreprises (9 chiffres) |
| **SIRET** | Système d'Identification du Répertoire des Établissements (14 chiffres) |
| **SML** | Service Metadata Locator (service DNS de localisation) |
| **SMP** | Service Metadata Publisher (service HTTP de métadonnées) |
