# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
lib to find files in docs
for examplem in BDD test you can use
"~doc/UC1_F202500003_00-INV_20250701.pdf"
it will resolves to
"docs/norme/XP_Z12-012_Annexes_A_V1.2_et_B_EXEMPLES_V1.2/XP_Z12-012_Annexe_B_EXEMPLES_V1.2/Factures/F202500003/UC1_F202500003_00-INV_20250701.pdf"

will tell or fail in case of duplicates
"""


prefix = "~doc"
folder = "docs"

def resolve(
        source: str,
) -> str:
    return source


def duplicate():
    ...