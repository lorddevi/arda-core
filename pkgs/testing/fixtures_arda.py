"""Arda-specific test fixtures.

Mirrors clan-core's fixtures_flakes.py but for arda-core infrastructure.
This enables the with-core/without-core testing pattern.
"""

import logging
import os
import tempfile
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

import pytest

log = logging.getLogger(__name__)


# Environment variable for arda-core path
ARDA_CORE = Path(os.environ.get("ARDA_CORE_PATH", "/home/ld/src/arda-core"))


# allows defining nested dictionary in a single line
def def_value() -> defaultdict:
    return defaultdict(def_value)


def nested_dict() -> defaultdict:
    """Creates a defaultdict that allows for arbitrary levels of nesting.

    For example: d['a']['b']['c'] = value
    """
    return defaultdict(def_value)


class FlakeForTest(NamedTuple):
    """Represents a test flake with its path."""

    path: Path


def create_test_flake(
    temporary_home: Path, monkeypatch: pytest.MonkeyPatch
) -> FlakeForTest:
    """Create a basic test flake without arda-core.

    This is for tests that don't need arda-core infrastructure.
    Like clan-core's test_flake fixture.

    Args:
        temporary_home: Temporary directory for the test
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        FlakeForTest with the path to the created flake
    """
    flake_dir = temporary_home / "test-flake"
    flake_dir.mkdir(parents=True, exist_ok=True)

    # Create a minimal flake.nix
    flake_nix = flake_dir / "flake.nix"
    flake_nix.write_text("""
{
  description = "Test flake without arda-core";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs, ... }: {
    # Minimal devShell for testing
    devShells.x86_64-linux.default = nixpkgs.mkShell {
      packages = [
        nixpkgs.bashInteractive
      ];
    };
  };
}
""")

    # Create a minimal arda.toml config
    arda_toml = flake_dir / "arda.toml"
    arda_toml.write_text("""
[theme]
name = "default"

[output]
verbose = false
timestamp = true
""")

    return FlakeForTest(path=flake_dir)


def create_test_flake_with_core(
    temporary_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> FlakeForTest:
    """Create a test flake WITH arda-core.

    This is for tests that need arda-core infrastructure.
    Like clan-core's test_flake_with_core fixture.

    Args:
        temporary_home: Temporary directory for the test
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        FlakeForTest with the path to the created flake
    """
    if not (ARDA_CORE / "flake.nix").exists():
        pytest.skip(
            "arda-core flake not found. This test requires arda-core to be present"
        )

    flake_dir = temporary_home / "test-flake-with-core"
    flake_dir.mkdir(parents=True, exist_ok=True)

    # Create a flake.nix that imports arda-core
    flake_nix = flake_dir / "flake.nix"
    flake_nix.write_text(f"""
{{
  description = "Test flake with arda-core";

  inputs = {{
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    arda-core = path:{ARDA_CORE};
  }};

  outputs = {{ self, nixpkgs, arda-core }}: {{
    # DevShell with arda-cli and arda-core
    devShells.x86_64-linux.default = nixpkgs.mkShell {{
      packages = [
        arda-core.packages.x86_64-linux.arda-cli
        nixpkgs.bashInteractive
        nixpkgs.git
      ];
    }};

    # This would include any arda-core modules/templates when available
    nixosConfigurations.test-vm.x86_64-linux = nixpkgs.nixosSystem {{
      system = "x86_64-linux";
      modules = [
        {{}}
      ];
    }};
  }};
}}
""")

    # Create a minimal arda.toml config
    arda_toml = flake_dir / "arda.toml"
    arda_toml.write_text("""
[theme]
name = "default"

[output]
verbose = false
timestamp = true
""")

    return FlakeForTest(path=flake_dir)


@pytest.fixture
def test_flake(
    temporary_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[FlakeForTest]:
    """Create a basic test flake WITHOUT arda-core.

    This fixture is for tests that don't need arda-core infrastructure.
    Like clan-core's test_flake fixture.

    The tests using this fixture will run in the 'without-core' phase.
    """
    yield from create_test_flake(temporary_home, monkeypatch)


@pytest.fixture
def test_flake_with_core(
    request: pytest.FixtureRequest,
    temporary_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[FlakeForTest]:
    """Create a test flake WITH arda-core.

    This fixture is for tests that need arda-core infrastructure.
    Like clan-core's test_flake_with_core fixture.

    The tests using this fixture will run in the 'with-core' phase
    and must be marked with @pytest.mark.with_core.

    Args:
        request: Pytest fixture request
        temporary_home: Temporary directory for the test
        monkeypatch: Pytest monkeypatch fixture

    Yields:
        FlakeForTest with the path to the created flake
    """
    # Skip if arda-core not available
    if not (ARDA_CORE / "flake.nix").exists():
        pytest.skip(
            "arda-core flake not found. This test requires arda-core to be present"
        )

    yield from create_test_flake_with_core(temporary_home, monkeypatch)


# Additional utility fixtures for testing


@pytest.fixture
def minimal_arda_config() -> dict:
    """Provide a minimal arda configuration for testing.

    Returns:
        Dictionary representing minimal arda.toml configuration
    """
    return {
        "theme": {"name": "default"},
        "output": {"verbose": False, "timestamp": True},
    }


@pytest.fixture
def temp_arda_config_file(minimal_arda_config: dict) -> Iterator[Path]:
    """Create a temporary arda config file for testing.

    Args:
        minimal_arda_config: Minimal config dictionary

    Yields:
        Path to temporary config file
    """
    import tomli_w

    temp_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False)

    toml_bytes = tomli_w.dumps(minimal_arda_config)
    temp_file.write(toml_bytes)
    temp_file.close()

    yield Path(temp_file.name)

    # Cleanup
    Path(temp_file.name).unlink(missing_ok=True)
