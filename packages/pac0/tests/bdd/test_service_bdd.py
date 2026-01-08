"""
BDD test runner for service lifecycle scenarios.

This module loads feature files and runs them as pytest-bdd tests.
All step definitions are imported from service_steps.py.

References:
- pytest-bdd scenarios: https://pytest-bdd.readthedocs.io/en/latest/
- Feature files location: docs/briques/00-tests/
"""

import os

from pytest_bdd import scenarios

# Import all step definitions
from .service_steps import *  # noqa: F401, F403


# Get the path to the feature file
# Relative path from this file to the feature file
FEATURE_FILE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "..",
    "..",  # packages/pac0/tests/bdd -> root
    "docs",
    "briques",
    "00-tests",
    "service_lifecycle.feature",
)

# Load all scenarios from the feature file
scenarios(FEATURE_FILE)
