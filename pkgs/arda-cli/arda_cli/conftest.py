"""Pytest configuration for arda-cli tests.

This file is automatically loaded by pytest and adds the testing helpers
directory to the Python path so tests can import pytest_helpers.
"""

import sys
from pathlib import Path

# Add testing helpers to path
# Path: pkgs/arda-cli/arda_cli/conftest.py
# __file__ is /build/arda-cli-source/arda_cli/conftest.py (during build)
# Testing helpers are at /build/arda-cli-source/testing/helpers/pytest_helpers.py
# conftest.py -> parent = arda_cli/
# arda_cli/ -> parent = pkgs/arda-cli/ (repo root for arda-cli package)
# So go up 2 levels to reach /build/arda-cli-source/, then add testing/helpers
helpers_path = Path(__file__).parent.parent / "testing" / "helpers"

if str(helpers_path) not in sys.path:
    sys.path.insert(0, str(helpers_path))
