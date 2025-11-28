"""Pytest configuration for arda-cli tests.

This file is automatically loaded by pytest and adds the testing helpers
directory to the Python path so tests can import pytest_helpers.
"""

import sys
from pathlib import Path

# Add testing helpers to path - compute relative to project root
# Path: pkgs/arda-cli/arda_cli/conftest.py
# __file__ is /home/ld/src/arda-core/pkgs/arda-cli/arda_cli/conftest.py
# Need to go up: conftest.py -> arda_cli/ -> arda-cli/ -> pkgs/ -> arda-core/
project_root = Path(__file__).parent.parent.parent.parent
helpers_path = project_root / "pkgs" / "testing" / "helpers"

if str(helpers_path) not in sys.path:
    sys.path.insert(0, str(helpers_path))
