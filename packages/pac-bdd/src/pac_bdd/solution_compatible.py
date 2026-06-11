# SPDX-FileCopyrightText: 2026 PDP Libre
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Steps du cas nominal d'échange de facture piloté par un Logiciel Solution Compatible.

Référence : XP Z12-014 v1.3, section 4.2 « Description du cas nominal d'échange de factures ».

Ces steps sont volontairement **déclaratifs et agnostiques du canal** : ils décrivent le
comportement métier sans préjuger de l'implémentation (Playwright sur l'IHM du Logiciel Solution
Compatible, ou appels API sur son backend). Tant que la Plateforme Agréée et un Logiciel Solution
Compatible réel ne sont pas disponibles, ils sont en attente d'implémentation et appellent
``pytest.skip`` : les scénarios sont donc collectés et marqués *skipped* (et non en erreur).

Le premier step exécuté (un `Soit` du Contexte) court-circuite le scénario via ``pytest.skip`` ;
les autres steps sont néanmoins définis pour documenter la spécification complète et éviter tout
``StepDefNotFound`` si l'ordre d'exécution venait à changer.
"""

import pytest
from pytest_bdd import given, parsers, then, when

_EN_ATTENTE = (
    "En attente de la Plateforme Agréée et d'un Logiciel Solution Compatible réel "
    "(spécification exécutable, voir docs/developpement/BDD_Guide_SolutionCompatible.md)"
)


# --- Contexte -------------------------------------------------------------------------------

@given("un VENDEUR équipé d'un Logiciel Solution Compatible raccordé à sa PA-E")
def vendeur_equipe():
    pytest.skip(_EN_ATTENTE)


@given("un ACHETEUR équipé d'un Logiciel Solution Compatible raccordé à sa PA-R")
def acheteur_equipe():
    pytest.skip(_EN_ATTENTE)


# --- Émission côté VENDEUR / PA-E ------------------------------------------------------------

@when(
    parsers.parse(
        '''le VENDEUR envoie la facture "{invoice}" à son ACHETEUR depuis son Logiciel Solution Compatible'''
    )
)
def vendeur_envoie_facture(invoice: str):
    pytest.skip(_EN_ATTENTE)


@then(parsers.parse('''le VENDEUR obtient le statut "{status}" pour la facture "{invoice}"'''))
def vendeur_obtient_statut_facture(status: str, invoice: str):
    pytest.skip(_EN_ATTENTE)


@when(parsers.parse('''le VENDEUR demande l'actualisation du statut de la facture "{invoice}"'''))
def vendeur_actualise_statut(invoice: str):
    pytest.skip(_EN_ATTENTE)


@then(parsers.parse('''le VENDEUR obtient le statut "{status}"'''))
def vendeur_obtient_statut(status: str):
    pytest.skip(_EN_ATTENTE)


# --- Réception côté ACHETEUR / PA-R ----------------------------------------------------------

@when("l'ACHETEUR consulte ses factures reçues depuis son Logiciel Solution Compatible")
def acheteur_consulte_factures():
    pytest.skip(_EN_ATTENTE)


@then(parsers.parse('''l'ACHETEUR voit la facture "{invoice}" avec le statut "{status}"'''))
def acheteur_voit_facture(invoice: str, status: str):
    pytest.skip(_EN_ATTENTE)
