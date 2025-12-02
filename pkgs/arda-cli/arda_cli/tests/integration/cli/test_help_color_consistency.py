"""Integration tests for help output color consistency.

This module tests that 'arda' and 'arda --help' produce identical colored output,
preventing regressions where different code paths might use different themes.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from arda_cli.main import main

# ANSI color code regex pattern
# Matches escape sequences like \x1b[38;5;36m or \x1b[0m
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[mKHF]")


class TestHelpColorConsistency:
    """Test that help output colors are consistent.

    Verifies that 'arda' and 'arda --help' produce identical colored output,
    preventing regressions where different code paths might use different themes.
    """

    @pytest.mark.integration
    @pytest.mark.cli
    @pytest.mark.with_core
    def test_arda_vs_arda_help_color_consistency(self):
        """Test that 'arda' and 'arda --help' produce identical color codes.

        This test ensures that both invocation methods use the same theme from
        the config file, producing identical colored output. This is a regression
        test for the bug where 'arda --help' used a hardcoded 'dracula' default
        while 'arda' read from the config file.
        """
        runner = CliRunner()

        # Run 'arda' (without --help flag) - should show help by default
        result_arda = runner.invoke(main, [], catch_exceptions=False)

        # Run 'arda --help' explicitly
        result_help = runner.invoke(main, ["--help"], catch_exceptions=False)

        # Both should succeed
        assert result_arda.exit_code == 0, f"'arda' failed: {result_arda.output}"
        assert result_help.exit_code == 0, f"'arda --help' failed: {result_help.output}"

        # Extract ANSI escape codes from both outputs
        colors_arda = set(ANSI_ESCAPE_PATTERN.findall(result_arda.output))
        colors_help = set(ANSI_ESCAPE_PATTERN.findall(result_help.output))

        # The color codes should be identical
        # Note: We compare the SET of color codes to ensure same colors are used
        # The order might differ slightly but the presence should be the same

        if colors_arda != colors_help:
            # Helpful error message showing differences
            only_in_arda = colors_arda - colors_help
            only_in_help = colors_help - colors_arda

            error_msg = "Color codes differ between 'arda' and 'arda --help':\n"
            if only_in_arda:
                error_msg += f"  Only in 'arda': {only_in_arda}\n"
            if only_in_help:
                error_msg += f"  Only in 'arda --help': {only_in_help}\n"

            pytest.fail(error_msg)

        # Additional check: compare normalized outputs (remove all ANSI codes)
        normalized_arda = ANSI_ESCAPE_PATTERN.sub("", result_arda.output)
        normalized_help = ANSI_ESCAPE_PATTERN.sub("", result_help.output)

        # The normalized text should be identical (ignoring colors)
        assert normalized_arda == normalized_help, (
            "Text content differs between 'arda' and 'arda --help'"
        )

    @pytest.mark.integration
    @pytest.mark.cli
    @pytest.mark.with_core
    @pytest.mark.parametrize("theme", ["dracula", "nord", "forest", "solarized"])
    def test_color_consistency_with_different_themes(self, theme):
        """Test color consistency with different themes.

        Ensures that the fix works correctly across multiple themes.
        """
        runner = CliRunner()

        # Run with --theme option
        result_arda = runner.invoke(main, ["--theme", theme], catch_exceptions=False)

        result_help = runner.invoke(
            main, ["--theme", theme, "--help"], catch_exceptions=False
        )

        # Both should succeed
        assert result_arda.exit_code == 0, f"'arda --theme {theme}' failed"
        assert result_help.exit_code == 0, f"'arda --theme {theme} --help' failed"

        # Extract ANSI escape codes
        colors_arda = set(ANSI_ESCAPE_PATTERN.findall(result_arda.output))
        colors_help = set(ANSI_ESCAPE_PATTERN.findall(result_help.output))

        # Colors should be identical
        assert colors_arda == colors_help, f"Color codes differ with theme '{theme}'"

        # Normalized text should be identical
        normalized_arda = ANSI_ESCAPE_PATTERN.sub("", result_arda.output)
        normalized_help = ANSI_ESCAPE_PATTERN.sub("", result_help.output)

        assert normalized_arda == normalized_help, (
            f"Text content differs with theme '{theme}'"
        )

    @pytest.mark.integration
    @pytest.mark.cli
    @pytest.mark.with_core
    def test_active_configuration_line_colors(self):
        """Test that the 'Active configuration:' line has consistent colors.

        This is a specific test for the bug where the Active configuration
        line had different colors between 'arda' and 'arda --help'.
        """
        runner = CliRunner()

        # Run both commands
        result_arda = runner.invoke(main, [])
        result_help = runner.invoke(main, ["--help"])

        assert result_arda.exit_code == 0
        assert result_help.exit_code == 0

        # Extract the "Active configuration:" line from both outputs
        import re

        # Pattern to match the active configuration line
        pattern = r"Active configuration:.*"

        match_arda = re.search(pattern, result_arda.output)
        match_help = re.search(pattern, result_help.output)

        assert match_arda, (
            "Could not find 'Active configuration:' line in 'arda' output"
        )
        assert match_help, (
            "Could not find 'Active configuration:' line in 'arda --help' output"
        )

        line_arda = match_arda.group(0)
        line_help = match_help.group(0)

        # Extract colors from both lines
        colors_arda = set(ANSI_ESCAPE_PATTERN.findall(line_arda))
        colors_help = set(ANSI_ESCAPE_PATTERN.findall(line_help))

        # Colors should be identical
        assert colors_arda == colors_help, (
            "Colors in 'Active configuration:' line differ between "
            "'arda' and 'arda --help'"
        )

        # Text should be identical
        normalized_arda = ANSI_ESCAPE_PATTERN.sub("", line_arda)
        normalized_help = ANSI_ESCAPE_PATTERN.sub("", line_help)

        assert normalized_arda == normalized_help, (
            "Text in 'Active configuration:' line differs"
        )

    @pytest.mark.integration
    @pytest.mark.cli
    @pytest.mark.with_core
    def test_help_output_with_subcommands(self):
        """Test that help for subcommands is also consistent.

        Verifies that the fix doesn't break subcommand help output.
        """
        runner = CliRunner()

        # Test config subcommand
        result_arda = runner.invoke(main, ["config"])
        result_help = runner.invoke(main, ["config", "--help"])

        assert result_arda.exit_code == 0
        assert result_help.exit_code == 0

        # Both should show help
        assert "Usage:" in result_arda.output
        assert "Usage:" in result_help.output

        # Extract colors
        colors_arda = set(ANSI_ESCAPE_PATTERN.findall(result_arda.output))
        colors_help = set(ANSI_ESCAPE_PATTERN.findall(result_help.output))

        # Colors should be identical for subcommands too
        assert colors_arda == colors_help, (
            "Color codes differ for 'arda config' vs 'arda config --help'"
        )
