# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Importez ici toutes les définitions d'étapes BDD
# L'ordre de définition des étapes est important:
# La première règle qui matche *masque* les autres

from .api import *
from .demo import *
from .esb import *
from .facture import *
from .peppol import *
from .service import *
from .tobeimplemented import *
from .user import *
