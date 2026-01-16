# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pytest_bdd import then, when, parsers

# le contexte où conserver les états/valeurs à vérifier
ctx = {'nb': 0}

# on décore la fonction pour lui dire qu'elle doit être appelée
# pour l'étape "Quand je fais quelque chose"
@when("je fais quelque chose")
# peu import le nom de la fonction
def _():
    # on place dans le contexte la valeur modifiée
    ctx["nb"] += 1

# même chose pour l'étape "Quand je fais autre chose"
# valable aussi pour "Et je fais autre chose"
@when("je fais autre chose")
def _():
    ctx["nb"] += 1


# même chose pour l'étape "Alors j'ai fait 4 choses"
# notez le paramêtre `nb`
# notez l'utilisation pratique des triple quotes (''')
@then(parsers.parse("""j'ai fait {nb} choses"""))
def _(nb):
    # si le nombre donnée `nb` ne corresponds pas au contexte, on échoue
    assert ctx['nb'] == int(nb)

