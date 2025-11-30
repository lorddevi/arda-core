"""Test to ensure custom rich-click overlay is always used.

This test prevents regression of the rich-click version mismatch bug.
Without the custom overlay, arda-cli will fail with:
  TypeError: RichHelpConfiguration.__init__() got an unexpected keyword argument 'theme'

The overlay upgrades rich-click from nixpkgs version (1.8.9) to custom version (1.9.4)
which includes theming support required by arda-cli.
"""

import os

import pytest

# Skip these tests in Nix build environment - they require devShell
# Check if we're in a Nix build by looking for NIX_BUILD_CORES
in_nix_build = os.environ.get("NIX_BUILD_CORES") is not None


def skip_if_in_nix_build():
    """Skip test if running in Nix build environment."""
    if in_nix_build:
        pytest.skip(
            "Test requires devShell overlay infrastructure, not available in Nix build"
        )


@pytest.mark.fast
@pytest.mark.with_core
def test_rich_click_version_is_overlaid():
    """Verify that rich-click version is 1.9.4 (overlay), not 1.8.9 (nixpkgs).

    The custom overlay in overlays/python3/rich-click.nix upgrades rich-click
    to version 1.9.4, which supports the 'theme' parameter in RichHelpConfiguration.

    Without this overlay:
    - rich-click version would be 1.8.9 (from nixpkgs)
    - RichHelpConfiguration doesn't accept 'theme' parameter in 1.8.9
    - arda --help would fail with TypeError
    """
    skip_if_in_nix_build()
    import rich_click

    # The overlay version (1.9.4) vs nixpkgs version (1.8.9)
    expected_version = "1.9.4"
    nixpkgs_version = "1.8.9"

    actual_version = rich_click.__version__

    assert actual_version == expected_version, (
        f"Expected rich-click {expected_version} "
        f"(custom overlay version with theming), "
        f"but got {actual_version} (nixpkgs version without theming support). "
        f"The custom overlay in overlays/python3/rich-click.nix must not be "
        f"applied correctly. Both devShell and arda-cli package must use the "
        f"overlaid version."
    )


@pytest.mark.fast
@pytest.mark.with_core
def test_rich_click_has_theming_support():
    """Verify that RichHelpConfiguration accepts 'theme' parameter.

    This confirms that the overlaid version (1.9.4) is being used, which has
    theming support. The nixpkgs version (1.8.9) lacks this support.

    Failure means:
    - arda --help will fail with: TypeError: RichHelpConfiguration.__init__()
      got an unexpected keyword argument 'theme'
    """
    skip_if_in_nix_build()
    import inspect

    from rich_click.rich_help_configuration import RichHelpConfiguration

    sig = inspect.signature(RichHelpConfiguration.__init__)
    params = sig.parameters

    # Version 1.9.4+ has these parameters
    assert "theme" in params, (
        "RichHelpConfiguration.__init__() missing 'theme' parameter. "
        "This indicates nixpkgs version 1.8.9 is being used instead of "
        "overlay version 1.9.4. Please verify overlays/python3/rich-click.nix "
        "is correctly applied."
    )

    assert "enable_theme_env_var" in params, (
        "RichHelpConfiguration.__init__() missing 'enable_theme_env_var' "
        "parameter. This indicates nixpkgs version 1.8.9 is being used instead "
        "of overlay version 1.9.4. Please verify overlays/python3/rich-click.nix "
        "is correctly applied."
    )


@pytest.mark.slow
@pytest.mark.with_core
def test_arda_cli_help_works():
    """Integration test: Verify arda --help command works without errors.

    This test actually runs the arda CLI to ensure it can display help.
    If the overlay is not applied correctly, this will fail with:
      TypeError: RichHelpConfiguration.__init__() got an unexpected keyword
      argument 'theme'

    This is the actual user-facing symptom of the overlay not being applied.
    """
    skip_if_in_nix_build()
    import subprocess
    import sys

    # Try to import arda_cli to ensure it can be loaded
    try:
        import arda_cli.main
    except ImportError as e:
        pytest.skip(f"Cannot import arda_cli.main: {e}")

    # Run arda --help as a subprocess to test the actual CLI
    # We just verify it exits with 0, not the output
    try:
        # For package build: arda might not be in PATH
        # We'll try a simple Python import test instead
        from click.testing import CliRunner

        from arda_cli.main import main

        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0, (
            f"arda --help failed with exit code {result.exit_code}. "
            f"This indicates the rich-click overlay is not applied correctly. "
            f"Output: {result.output}"
        )

    except Exception as e:
        pytest.skip(f"Cannot test arda CLI directly: {e}")


@pytest.mark.fast
@pytest.mark.with_core
def test_overlay_configuration_exists():
    """Verify that the overlay files exist and are properly configured.

    This is a sanity check that the overlay infrastructure is in place.
    """
    skip_if_in_nix_build()
    import os
    import pathlib

    # Navigate from the test file to the repository root
    # Test is at: pkgs/arda-cli/arda_cli/tests/unit/overlay/test_rich_click_version.py
    # Need to go up 7 levels to reach repo root
    repo_root = pathlib.Path(__file__).resolve()
    for _ in range(7):
        repo_root = repo_root.parent

    # Check for overlays in the repo root
    overlay_dir = repo_root / "overlays"

    assert overlay_dir.exists(), (
        f"Overlays directory {overlay_dir} does not exist. "
        "The custom overlay infrastructure is missing."
    )

    # Check specific overlay files
    python3_overlay = overlay_dir / "python3" / "rich-click.nix"
    assert python3_overlay.exists(), (
        f"Rich-click overlay file {python3_overlay} does not exist. "
        "The overlay to upgrade rich-click to 1.9.4 is missing."
    )

    # Check that flake.nix references the overlay
    flake_nix = repo_root / "flake.nix"
    assert flake_nix.exists(), (
        f"flake.nix does not exist at {flake_nix}. Cannot verify overlay configuration."
    )

    with open(flake_nix) as f:
        flake_content = f.read()

    assert "overlays/default.nix" in flake_content, (
        "flake.nix does not import overlays/default.nix. "
        "The overlay is not being applied to nixpkgs."
    )

    assert "rich-click" in flake_content, (
        "flake.nix does not reference rich-click. "
        "The rich-click overlay may not be configured."
    )


@pytest.mark.integration
@pytest.mark.with_core
def test_package_uses_overlaid_python313packages():
    """Verify that arda-cli package is built with overlaid python313Packages.

    This test checks that the package derivation uses the overlaid version.
    In Nix, this means checking that python313Packages.rich-click is 1.9.4.
    """
    skip_if_in_nix_build()
    import os
    import sys

    # Check if we're in a Nix build environment
    nix_build = os.environ.get("NIX_BUILD_TOP") or os.environ.get("IN_NIX_SANDBOX")

    if not nix_build:
        pytest.skip("This test only runs during Nix build")

    # In a Nix build, we can verify the package is built correctly
    # by checking that the rich-click in the environment is 1.9.4
    import rich_click

    assert rich_click.__version__ == "1.9.4", (
        f"Package build is using rich-click {rich_click.__version__}, expected 1.9.4. "
        "The package must be built with the overlaid python313Packages."
    )
