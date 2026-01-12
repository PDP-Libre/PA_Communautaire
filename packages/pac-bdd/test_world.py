"""
BDD test runner for WorldContext scenarios.

This module runs the BDD scenarios defined in:
docs/briques/02-esb-central/world.feature

References:
- pytest-bdd: https://pytest-bdd.readthedocs.io/
"""

import pytest
from pytest_bdd import scenario, scenarios

# Import all step definitions
from pac_bdd.world_steps import *


# Load all scenarios from the feature file
scenarios("../../docs/briques/02-esb-central/world.feature")
