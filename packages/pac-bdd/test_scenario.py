# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac_bdd.steps import *
from pytest_bdd import scenarios
import glob
import logging

logging.getLogger().setLevel(logging.DEBUG)


# loop over all *.feature files
for feature_file in glob.glob("../../**/*.feature", recursive=True):
    # scenarios("../../docs/briques/04-validation-metier/compliance.feature")
    scenarios(feature_file)
