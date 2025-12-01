"""Unit tests for config command module.

Tests the CLI command layer for 'arda config' including:
- parse_config_value utility
"""

from unittest.mock import MagicMock, patch

import pytest

from arda_cli.commands.config.main import (
    ALLOWED_KEYS,
    parse_config_value,
)


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
@pytest.mark.without_core
class TestParseConfigValue:
    """Test parse_config_value function."""

    def test_parse_config_value_theme(self):
        """Test that theme values pass through as strings."""
        result = parse_config_value("default", "nord")
        assert result == "nord"
        assert isinstance(result, str)

        result = parse_config_value("default", "forest")
        assert result == "forest"

        result = parse_config_value("default", "dracula")
        assert result == "dracula"

    def test_parse_config_value_verbose_true_variants(self):
        """Test all true boolean variants for verbose."""
        true_variants = [
            "true", "True", "TRUE", "1", "yes", "Yes", "YES", "on", "On", "ON"
        ]

        for variant in true_variants:
            result = parse_config_value("verbose", variant)
            assert result is True, f"Failed for variant: {variant}"
            assert isinstance(result, bool)

    def test_parse_config_value_verbose_false_variants(self):
        """Test all false boolean variants for verbose."""
        false_variants = [
            "false", "False", "FALSE", "0", "no", "No", "NO", "off", "Off", "OFF"
        ]

        for variant in false_variants:
            result = parse_config_value("verbose", variant)
            assert result is False, f"Failed for variant: {variant}"
            assert isinstance(result, bool)

    def test_parse_config_value_timestamp_true_variants(self):
        """Test all true boolean variants for timestamp."""
        true_variants = ["true", "1", "yes", "on"]

        for variant in true_variants:
            result = parse_config_value("timestamp", variant)
            assert result is True, f"Failed for variant: {variant}"

    def test_parse_config_value_timestamp_false_variants(self):
        """Test all false boolean variants for timestamp."""
        false_variants = ["false", "0", "no", "off"]

        for variant in false_variants:
            result = parse_config_value("timestamp", variant)
            assert result is False, f"Failed for variant: {variant}"

    def test_parse_config_value_invalid_boolean(self):
        """Test that invalid boolean values raise ValueError."""
        invalid_values = ["maybe", "2", "yep", "nope", "t", "f", "", "TRUE "]

        for invalid in invalid_values:
            with pytest.raises(ValueError) as exc_info:
                parse_config_value("verbose", invalid)
            assert "Invalid boolean value" in str(exc_info.value)
            assert invalid in str(exc_info.value)

    def test_parse_config_value_unknown_setting(self):
        """Test that unknown settings raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_config_value("unknown_setting", "value")
        assert "Unknown setting: unknown_setting" in str(exc_info.value)

    def test_parse_config_value_case_insensitive_booleans(self):
        """Test that boolean parsing is case-insensitive."""
        result = parse_config_value("verbose", "TrUe")
        assert result is True

        result = parse_config_value("verbose", "FaLsE")
        assert result is False

        result = parse_config_value("timestamp", "YeS")
        assert result is True

        result = parse_config_value("timestamp", "oFf")
        assert result is False


# NOTE: Click command tests (config view/set/init) have been moved to integration tests
# where they can be properly tested using CliRunner. See:
# - arda_cli/tests/integration/commands/test_config_commands.py
#
# The unit tests for parse_config_value above provide comprehensive coverage of the
# core parsing logic without the complexity of Click command testing.
