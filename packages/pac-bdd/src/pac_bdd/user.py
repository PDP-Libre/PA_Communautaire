# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pytest_bdd import given, parsers, scenario, then, when


# Etant un utilisateur de la PA #pa1
@given(parsers.parse("un utilisateur de la PA #{pa}"))
def author_user_pa(pa): ...


# Etant un utilisateur
@given("un utilisateur")
def author_user(pac):
    assert pac.is_running is True
