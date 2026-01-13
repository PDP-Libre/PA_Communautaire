# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac0.shared.esb import init_esb_app
from pac0.service.gestion_cycle_vie.lib import router

broker, app = init_esb_app()
broker.include_router(router)
