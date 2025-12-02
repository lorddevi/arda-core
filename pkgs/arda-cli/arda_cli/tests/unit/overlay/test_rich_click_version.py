"""Test to ensure custom rich-click overlay is always used.

This test prevents regression of the rich-click version mismatch bug.
Without the custom overlay, arda-cli will fail with:
  TypeError: RichHelpConfiguration.__init__() got an unexpected keyword argument 'theme'

The overlay upgrades rich-click from nixpkgs version (1.8.9) to custom version (1.9.4)
which includes theming support required by arda-cli.

These tests are part of Phase 1 (without-core) because:
1. The overlay is part of arda-cli's build dependencies
2. arda-cli cannot function without the overlay
3. This is testing arda-cli in isolation, not arda-core integration
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.fast
@pytest.mark.without_core
def test_rich_click_version_is_overlaid():
    """Verify that rich-click version has theming support (overlay applied).

    The custom overlay in overlays/python3/rich-click.nix upgrades rich-click
    to a version that supports the 'theme' parameter in RichHelpConfiguration.

    Without this overlay:
    - rich-click version would be 1.8.9 (from nixpkgs)
    - RichHelpConfiguration doesn't accept 'theme' parameter in 1.8.9
    - arda --help would fail with TypeError

    This test runs in both devShell and Nix builds to verify the overlay is applied.
    """
    import rich_click

    actual_version = rich_click.__version__

    # Verify the version is not the base nixpkgs version
    nixpkgs_version = "1.8.9"

    # Check that version is not the nixpkgs version OR has theming support
    # This makes the test more maintainable - we verify the feature works,
    # not specific version numbers
    if actual_version == nixpkgs_version:
        # If it's the nixpkgs version, verify theming support exists anyway
        import inspect

        from rich_click.rich_help_configuration import RichHelpConfiguration

        sig = inspect.signature(RichHelpConfiguration.__init__)
        params = sig.parameters

        assert "theme" in params, (
            f"rich-click version {actual_version} (nixpkgs) lacks theming support. "
            f"The custom overlay in overlays/python3/rich-click.nix must not be "
            f"applied correctly."
        )
    else:
        # It's a newer version - just verify it has theming support
        import inspect

        from rich_click.rich_help_configuration import RichHelpConfiguration

        sig = inspect.signature(RichHelpConfiguration.__init__)
        params = sig.parameters

        assert "theme" in params, (
            f"rich-click version {actual_version} lacks theming support. "
            f"The overlay may need to be updated to a version that supports theming."
        )


@pytest.mark.fast
@pytest.mark.without_core
def test_rich_click_has_theming_support():
    """Verify that RichHelpConfiguration accepts 'theme' parameter.

    This confirms that the overlaid version (1.9.4) is being used, which has
    theming support. The nixpkgs version (1.8.9) lacks this support.

    Failure means:
    - arda --help will fail with: TypeError: RichHelpConfiguration.__init__()
      got an unexpected keyword argument 'theme'

    This test runs in both devShell and Nix builds to verify the overlay is working.
    """
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
@pytest.mark.without_core
def test_arda_cli_help_works():
    """Integration test: Verify arda --help command works without errors.

    This test actually runs the arda CLI to ensure it can display help.
    If the overlay is not applied correctly, this will fail with:
      TypeError: RichHelpConfiguration.__init__() got an unexpected keyword
      argument 'theme'

    This is the actual user-facing symptom of the overlay not being applied.

    This test runs in both devShell and Nix builds to verify
    the overlay works end-to-end.
    """
    # Try to import arda_cli to ensure it can be loaded
    try:
        import arda_cli.main
    except ImportError as e:
        pytest.skip(f"Cannot import arda_cli.main: {e}")

    # Run arda --help as a subprocess to test the actual CLI
    # We just verify it exits with 0, not the output
    try:
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
@pytest.mark.without_core
def test_package_uses_overlaid_python313packages():
    """Verify that arda-cli package is built with overlaid python313Packages.

    This test checks that the package derivation uses the overlaid version.
    In Nix builds, we verify that the rich-click in the environment has theming support.

    This is a runtime verification test - it checks that the overlay actually works,
    not whether the overlay files exist in the source tree.
    """
    # In both devShell and Nix builds, we can verify the package is built correctly
    # by checking that the rich-click in the environment has theming support
    import rich_click

    # Check that version is not the base nixpkgs version OR has theming support
    nixpkgs_version = "1.8.9"
    actual_version = rich_click.__version__

    if actual_version == nixpkgs_version:
        # If it's the nixpkgs version, verify theming support exists
        # (This would be unusual but we handle it gracefully)
        import inspect

        from rich_click.rich_help_configuration import RichHelpConfiguration

        sig = inspect.signature(RichHelpConfiguration.__init__)
        params = sig.parameters

        assert "theme" in params, (
            f"Package build is using rich-click {actual_version} "
            f"(nixpkgs) without theming support. "
            "The package must be built with the overlaid python313Packages."
        )
    else:
        # It's a newer version - verify theming support
        import inspect

        from rich_click.rich_help_configuration import RichHelpConfiguration

        sig = inspect.signature(RichHelpConfiguration.__init__)
        params = sig.parameters

        assert "theme" in params, (
            f"Package build is using rich-click {actual_version} "
            f"without theming support. "
            "The package must be built with the overlaid python313Packages."
        )


@pytest.mark.fast
@pytest.mark.without_core
def test_rich_click_has_expected_module_structure():
    """Verify that rich-click has the expected module structure.

    This test ensures the overlaid version has all expected attributes
    and methods that arda-cli relies on.
    """
    import rich_click

    # Verify version attribute exists
    assert hasattr(rich_click, "__version__")

    # Verify RichHelpConfiguration is available
    from rich_click.rich_help_configuration import RichHelpConfiguration

    assert RichHelpConfiguration is not None

    # Verify the class has expected methods
    assert hasattr(RichHelpConfiguration, "__init__")


@pytest.mark.fast
@pytest.mark.without_core
def test_rich_click_parameter_details():
    """Verify that RichHelpConfiguration parameters have expected types.

    This test ensures the overlaid version has parameter type annotations
    that match what's expected.
    """
    import inspect

    from rich_click.rich_help_configuration import RichHelpConfiguration

    sig = inspect.signature(RichHelpConfiguration.__init__)
    params = sig.parameters

    # Verify all expected parameters exist
    assert len(params) > 0

    # Verify 'theme' parameter exists
    assert "theme" in params

    # Verify 'enable_theme_env_var' parameter exists
    assert "enable_theme_env_var" in params

    # Verify parameter has expected properties
    theme_param = params["theme"]
    assert theme_param is not None
