# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later


from typing import Literal, get_args

# default repo to use on `pac0 run`
# DEFAULT_REPO = "https://github.com/paxpar-tech/PA_Communautaire"
DEFAULT_REPO = "https://git.pdplibre.org/Construction_PA/PA_Communautaire.git"

# default branch to use on `pac0 run`
DEFAULT_BRANCH = "main"

type Brique = Literal[
    "01-api-gateway",
    "02-esb-central",
    "03-controle-formats",
    "04-validation-metier",
    "05-conversion-formats",
    "06-annuaire-local",
    "07-routage",
    "08-transmission-fiscale",
    "09-gestion-cycle-vie",
    "10-stockage",
]

SERVICES = get_args(Brique)
Briques: tuple[Brique, ...] = get_args(Brique)
