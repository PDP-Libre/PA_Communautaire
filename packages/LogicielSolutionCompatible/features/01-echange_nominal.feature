# language: fr
# SPDX-FileCopyrightText: 2026 PDP Libre
# SPDX-License-Identifier: GPL-3.0-or-later
@solution-compatible @cas-nominal @wip
Fonctionnalité: Échange nominal d'une facture entre Logiciels Solution Compatible
    Cas nominal d'échange de factures — Section 4.2 de XP Z12-014 v1.3.

    Un VENDEUR émet une facture à destination de son ACHETEUR en pilotant son
    Logiciel Solution Compatible (par exemple Dolibarr ou Factur-e). La facture
    transite par la PA-E du VENDEUR puis par la PA-R de l'ACHETEUR. Ce scénario
    couvre la phase de transmission, de la création de la facture jusqu'à sa mise
    à disposition de l'ACHETEUR (« tout va bien » : pas de rejet, pas de litige).

    Périmètre : étapes 1 à 3 du cas nominal (statuts Déposée, Émise, Reçue,
    Mise à disposition). Les phases de traitement, paiement et encaissement font
    l'objet de scénarios ultérieurs (voir docs/developpement/BDD_Guide_SolutionCompatible.md).

    Contexte:
        Soit un VENDEUR équipé d'un Logiciel Solution Compatible raccordé à sa PA-E
        Et un ACHETEUR équipé d'un Logiciel Solution Compatible raccordé à sa PA-R

    Scénario: Le VENDEUR émet la facture, l'ACHETEUR la réceptionne
        # Étapes 1 et 2 : création puis dépôt de la facture, contrôles de la PA-E
        Quand le VENDEUR envoie la facture "15" à son ACHETEUR depuis son Logiciel Solution Compatible
        Alors le VENDEUR obtient le statut "Déposée" pour la facture "15"

        # Étape 2 : la PA-E émet la facture vers la PA-R
        Quand le VENDEUR demande l'actualisation du statut de la facture "15"
        Alors le VENDEUR obtient le statut "Émise"

        # Étape 3 : la PA-R reçoit et met la facture à disposition de l'ACHETEUR
        Quand le VENDEUR demande l'actualisation du statut de la facture "15"
        Alors le VENDEUR obtient le statut "Mise à disposition"

        # Vérification côté ACHETEUR : la facture est bien réceptionnée
        Quand l'ACHETEUR consulte ses factures reçues depuis son Logiciel Solution Compatible
        Alors l'ACHETEUR voit la facture "15" avec le statut "Reçue"
