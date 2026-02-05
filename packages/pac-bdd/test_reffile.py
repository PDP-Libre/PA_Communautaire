# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pytest.mark import skip
from pac_bdd.lib import reffile



"""
@parametize???
( "source",  "resolved")
(
    "~doc/UC1_F202500003_00-INV_20250701.pdf",
    "docs/norme/XP_Z12-012_Annexes_A_V1.2_et_B_EXEMPLES_V1.2/XP_Z12-012_Annexe_B_EXEMPLES_V1.2/Factures/F202500003/UC1_F202500003_00-INV_20250701.pdf",
),(
    "~doc/UC4b_F202500010_00-INVCORR_20250702.pdf",
    "docs/norme/XP_Z12-012_Annexes_A_V1.2_et_B_EXEMPLES_V1.2/XP_Z12-012_Annexe_B_EXEMPLES_V1.2/Factures/Facture et Facture Rectificative/UC4b_F202500010_00-INVCORR_20250702.pdf",
)
"""


# @skip("not yet implemented")
def test_pdf_files(source: str, resolved: str):
    '''test pdf files'''
    assert False


"""

@parametize???
( "source",  "resolved")
(
    "~doc/UC4_F202500006_00-INV_20250701_CII.xml",
    "docs/norme/XP_Z12-012_Annexes_A_V1.2_et_B_EXEMPLES_V1.2/XP_Z12-012_Annexe_B_EXEMPLES_V1.2/Factures/Facture et Facture Rectificative/UC4_F202500006_00-INV_20250701_CII.xml",
),(
    "~doc/F202500001_INV_20250201_UBL.xml",
    "docs/docs/norme/XP_Z12-012_Annexes_A_V1.2_et_B_EXEMPLES_V1.2/XP_Z12-012_Annexe_B_EXEMPLES_V1.2/Factures/F202500001/F202500001_INV_20250201_UBL.xml",
)
"""


# @skip("not yet implemented")
def test_xml_files(source: str, resolved: str):
    '''test pdf files'''
    assert False
