# language: fr
Fonctionnalité: Découverte PEPPOL et routage inter-PA
    En tant que service de routage
    Je veux interroger le réseau PEPPOL
    Afin de déterminer quelle PA a autorité pour une entreprise donnée
    Et router les factures vers la bonne destination

    Contexte:
        Soit le service PEPPOL configuré en mode "test"
        Et le SML de test "acc.edelivery.tech.ec.europa.eu"

    # ==========================================================================
    # Lookup SML - Résolution DNS
    # ==========================================================================

    Scénario: Résolution SML réussie pour un participant enregistré
        Soit l'entreprise #e1 avec le SIREN "123456789"
        Et l'entreprise #e1 enregistrée sur PEPPOL
        Quand je calcule le hostname SML pour le SIREN "123456789"
        Alors le hostname SML est "B-{hash}.iso6523-actorid-upis.acc.edelivery.tech.ec.europa.eu"
        Quand j'interroge le SML via DNS
        Alors j'obtiens une réponse DNS valide
        Et j'obtiens l'URL du SMP "https://smp.pa-distante.fr"

    Scénario: Résolution SML échouée - participant non enregistré
        Soit l'entreprise #e2 avec le SIREN "999999999"
        Et l'entreprise #e2 non enregistrée sur PEPPOL
        Quand je calcule le hostname SML pour le SIREN "999999999"
        Et j'interroge le SML via DNS
        Alors j'obtiens une erreur DNS "NXDOMAIN"
        Et le code erreur est "PARTICIPANT_NOT_FOUND"

    # ==========================================================================
    # Lookup SMP - Récupération des métadonnées
    # ==========================================================================

    Scénario: Récupération métadonnées SMP réussie
        Soit l'entreprise #e1 avec le SIREN "123456789"
        Et l'entreprise #e1 enregistrée sur PEPPOL
        Et le SMP de #e1 accessible à "https://smp.pa-distante.fr"
        Quand je recherche les métadonnées SMP pour #e1
        Et le document type est "invoice_ubl"
        Alors j'obtiens une réponse SMP valide
        Et l'endpoint AS4 est "https://ap.pa-distante.fr/as4"
        Et le transport profile est "peppol-transport-as4-v2_0"
        Et le certificat est présent et valide

    Scénario: SMP ne supporte pas le document type demandé
        Soit l'entreprise #e1 avec le SIREN "123456789"
        Et l'entreprise #e1 enregistrée sur PEPPOL
        Et #e1 ne supporte que les factures UBL
        Quand je recherche les métadonnées SMP pour #e1
        Et le document type est "order_ubl"
        Alors j'obtiens une erreur HTTP 404
        Et le code erreur est "DOCUMENT_TYPE_NOT_SUPPORTED"

    # ==========================================================================
    # Lookup PEPPOL complet (SML + SMP)
    # ==========================================================================

    Scénario: Lookup PEPPOL complet réussi par SIREN
        Soit l'entreprise #e1 avec le SIREN "123456789"
        Et l'entreprise #e1 enregistrée sur PEPPOL
        Quand je recherche le participant PEPPOL pour le SIREN "123456789"
        Alors le lookup PEPPOL réussit
        Et j'obtiens l'endpoint de la PA responsable
        Et l'adresse de l'endpoint est "https://ap.pa-distante.fr/as4"

    Scénario: Lookup PEPPOL complet réussi par SIRET
        Soit l'entreprise #e1 avec le SIRET "12345678900012"
        Et l'entreprise #e1 enregistrée sur PEPPOL avec scheme "0002"
        Quand je recherche le participant PEPPOL pour le SIRET "12345678900012"
        Alors le lookup PEPPOL réussit
        Et j'obtiens l'endpoint de la PA responsable

    Scénario: Lookup PEPPOL échoué - participant introuvable
        Soit l'entreprise #e2 avec le SIREN "999999999"
        Et l'entreprise #e2 non enregistrée sur PEPPOL
        Quand je recherche le participant PEPPOL pour le SIREN "999999999"
        Alors le lookup PEPPOL échoue
        Et le code erreur est "PARTICIPANT_NOT_FOUND"
        Et le message erreur contient "non trouvé dans le SML"

    # ==========================================================================
    # Intégration avec le service de routage
    # ==========================================================================

    Scénario: Routage facture vers PA distante via PEPPOL
        Soit la PA #pa1
        Et la PA #pa2
        Et l'entreprise #e1 avec le SIREN "111111111"
        Et l'entreprise #e2 avec le SIREN "222222222"
        Et l'entreprise #e1 enregistrée sur la PA #pa1
        Et l'entreprise #e2 enregistrée sur la PA #pa2 via PEPPOL
        Et la facture #f1 de #e1 à #e2

        Soit un utilisateur de la PA #pa1
        Quand je dépose la facture #f1
        Alors la facture passe par le service de validation
        Et la facture passe par l'annuaire local
        Et le destinataire #e2 n'est pas trouvé localement
        Et la facture est transmise au service de routage
        Et le service de routage consulte PEPPOL pour #e2
        Et PEPPOL retourne l'endpoint de #pa2
        Et la facture est transmise à #pa2 via AS4
        Et j'obtiens le statut "routed"
        Et la destination est "https://ap.pa2.fr/as4"

    Scénario: Routage facture - destinataire local (pas de lookup PEPPOL)
        Soit la PA #pa1
        Et l'entreprise #e1 avec le SIREN "111111111"
        Et l'entreprise #e2 avec le SIREN "222222222"
        Et l'entreprise #e1 enregistrée sur la PA #pa1
        Et l'entreprise #e2 enregistrée sur la PA #pa1
        Et la facture #f1 de #e1 à #e2

        Soit un utilisateur de la PA #pa1
        Quand je dépose la facture #f1
        Alors la facture passe par l'annuaire local
        Et le destinataire #e2 est trouvé localement
        Et la facture n'est PAS transmise au service de routage
        Et le service de routage ne consulte PAS PEPPOL
        Et la facture est livrée localement à #e2
        Et j'obtiens le statut "delivered"

    Scénario: Routage facture - fallback vers PPF
        Soit la PA #pa1
        Et l'entreprise #e1 avec le SIREN "111111111"
        Et l'entreprise #e1 enregistrée sur la PA #pa1
        Et l'entreprise #e2 avec le SIREN "999999999"
        Et l'entreprise #e2 non enregistrée sur PEPPOL
        Et la facture #f1 de #e1 à #e2

        Soit un utilisateur de la PA #pa1
        Quand je dépose la facture #f1
        Alors la facture passe par l'annuaire local
        Et le destinataire #e2 n'est pas trouvé localement
        Et la facture est transmise au service de routage
        Et le service de routage consulte PEPPOL pour #e2
        Et PEPPOL retourne "PARTICIPANT_NOT_FOUND"
        Et la facture est transmise au PPF
        Et j'obtiens le statut "routed_to_ppf"
        Et la destination est "https://api.ppf.gouv.fr"

    # ==========================================================================
    # Validation des métadonnées SMP
    # ==========================================================================

    Scénario: Validation du certificat PEPPOL
        Soit l'entreprise #e1 avec le SIREN "123456789"
        Et l'entreprise #e1 enregistrée sur PEPPOL
        Quand je récupère les métadonnées SMP pour #e1
        Alors le certificat est au format X.509
        Et le certificat est signé par une autorité PEPPOL valide
        Et le certificat n'est pas expiré
        Et le certificat n'est pas révoqué

    Scénario: Vérification de la signature SMP
        Soit l'entreprise #e1 avec le SIREN "123456789"
        Et l'entreprise #e1 enregistrée sur PEPPOL
        Quand je récupère les métadonnées SMP pour #e1
        Alors la réponse SMP est signée
        Et la signature est valide
        Et le signataire est le SMP enregistré

    Scénario: Vérification des document types supportés
        Soit l'entreprise #e1 avec le SIREN "123456789"
        Et l'entreprise #e1 enregistrée sur PEPPOL
        Quand je récupère la liste des document types pour #e1
        Alors les document types supportés incluent:
            | document_type                                                    |
            | urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice |
        Et le process identifier est "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"

    # ==========================================================================
    # Gestion des erreurs et résilience
    # ==========================================================================

    Scénario: Timeout lors du lookup SML
        Soit un SML de test lent
        Et un timeout configuré à 5 secondes
        Quand je recherche le participant PEPPOL pour le SIREN "123456789"
        Et la requête DNS prend plus de 5 secondes
        Alors j'obtiens une erreur "SML_TIMEOUT"
        Et la facture est mise en file d'attente pour retry

    Scénario: SMP temporairement indisponible
        Soit l'entreprise #e1 avec le SIREN "123456789"
        Et l'entreprise #e1 enregistrée sur PEPPOL
        Et le SMP de #e1 temporairement indisponible (HTTP 503)
        Quand je recherche le participant PEPPOL pour #e1
        Alors la résolution SML réussit
        Mais la requête SMP échoue avec HTTP 503
        Et j'obtiens une erreur "SMP_UNAVAILABLE"
        Et la facture est mise en file d'attente pour retry

    Scénario: Retry automatique après échec temporaire
        Soit l'entreprise #e1 avec le SIREN "123456789"
        Et l'entreprise #e1 enregistrée sur PEPPOL
        Et le SMP de #e1 indisponible la première fois
        Et le SMP de #e1 disponible après 30 secondes
        Quand je recherche le participant PEPPOL pour #e1
        Alors la première tentative échoue
        Et une seconde tentative est programmée après 30 secondes
        Et la seconde tentative réussit
        Et j'obtiens l'endpoint de la PA responsable

    Scénario: Échec définitif après plusieurs retries
        Soit l'entreprise #e1 avec le SIREN "123456789"
        Et l'entreprise #e1 enregistrée sur PEPPOL
        Et le SMP de #e1 définitivement indisponible
        Quand je recherche le participant PEPPOL pour #e1
        Et 3 tentatives échouent
        Alors le routage échoue définitivement
        Et j'obtiens une erreur "ROUTING_FAILED"
        Et un message d'erreur est publié sur "routage-ERR"

    # ==========================================================================
    # Scénarios de communication inter-PA
    # ==========================================================================

    Scénario: Communication bidirectionnelle entre 2 PA
        Soit la PA #pa1
        Et la PA #pa2
        Et l'entreprise #e1 avec le SIREN "111111111"
        Et l'entreprise #e2 avec le SIREN "222222222"
        Et l'entreprise #e1 enregistrée sur la PA #pa1
        Et l'entreprise #e2 enregistrée sur la PA #pa2
        Et #pa1 et #pa2 enregistrées mutuellement sur PEPPOL

        # Facture de PA1 vers PA2
        Soit la facture #f1 de #e1 à #e2
        Quand un utilisateur de #pa1 dépose la facture #f1
        Alors la facture #f1 est routée vers #pa2 via PEPPOL

        # Facture de PA2 vers PA1
        Soit la facture #f2 de #e2 à #e1
        Quand un utilisateur de #pa2 dépose la facture #f2
        Alors la facture #f2 est routée vers #pa1 via PEPPOL

    Scénario: Réception d'une facture via AS4 depuis une PA distante
        Soit la PA #pa1
        Et l'entreprise #e1 avec le SIREN "111111111"
        Et l'entreprise #e1 enregistrée sur la PA #pa1
        Et une facture #f1 reçue via AS4 depuis une PA distante
        Et le destinataire de #f1 est #e1

        Quand la PA #pa1 reçoit la facture #f1 via AS4
        Alors la facture est validée
        Et la facture est livrée à #e1
        Et un accusé de réception AS4 est envoyé

    # ==========================================================================
    # Scénarios avec Chorus Pro / B2G
    # ==========================================================================

    Scénario: Facture B2G via Chorus Pro PEPPOL
        Soit la PA #pa1
        Et l'entreprise #e1 avec le SIREN "111111111"
        Et l'entreprise #e1 enregistrée sur la PA #pa1
        Et l'entité publique #ep1 avec le SIRET "11111111100015"
        Et #ep1 accessible via Chorus Pro sur PEPPOL
        Et la facture #f1 de #e1 à #ep1

        Soit un utilisateur de la PA #pa1
        Quand je dépose la facture #f1
        Et le service de routage consulte PEPPOL pour #ep1
        Alors PEPPOL retourne l'endpoint Chorus Pro via Pagero
        Et la facture est transmise à Chorus Pro
        Et j'obtiens le statut "routed"
