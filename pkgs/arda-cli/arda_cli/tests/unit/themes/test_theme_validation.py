"""Test that theme configurations are validated correctly.

This test file verifies the theme system functionality using pytest helpers.
Tests focus on theme configuration structure and validation logic.
"""

import pytest

# Import helpers
from arda_cli.testing.helpers.pytest_helpers import (
    TempDirectory,
    assert_theme_config,
    create_test_theme_config,
)


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.theme
def test_marker_system_works():
    """Verify that test markers are working correctly."""
    # This is a basic test to verify the test infrastructure
    assert True


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.theme
def test_create_test_theme_config():
    """Test that we can create test theme configurations."""
    # Create a default theme config
    config = create_test_theme_config()

    # Verify structure
    assert "theme" in config
    assert "name" in config["theme"]
    assert config["theme"]["name"] == "dracula"
    assert "primary_color" in config["theme"]
    assert "secondary_color" in config["theme"]
    assert config["theme"]["primary_color"] == "#282936"

    # Verify other config fields
    assert "verbose" in config
    assert config["verbose"] is False
    assert "timestamp" in config
    assert config["timestamp"] is True


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.theme
def test_create_custom_theme_config():
    """Test creating theme configs with custom theme names."""
    # Create config with custom theme
    config = create_test_theme_config("solarized")

    # Verify theme name is updated
    assert config["theme"]["name"] == "solarized"

    # Verify structure is still correct
    assert "primary_color" in config["theme"]
    assert "secondary_color" in config["theme"]


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.theme
def test_assert_theme_config():
    """Test that we can assert theme configs correctly."""
    # Create a valid theme config
    config = {
        "theme": {
            "name": "dracula",
            "primary_color": "#282936",
        },
        "verbose": False,
    }

    # Should pass with matching theme
    assert_theme_config(config, "dracula")

    # Should fail with wrong theme
    with pytest.raises(AssertionError):
        assert_theme_config(config, "monokai")


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.theme
def test_theme_config_persistence():
    """Test that theme configs persist correctly across operations."""
    with TempDirectory() as temp_dir:
        # Create theme config
        original_config = create_test_theme_config("forest")

        # Write to file
        config_file = temp_dir / "theme.toml"

        try:
            import tomli_w
        except ImportError:
            import toml

            with open(config_file, "w", encoding="utf-8") as f:
                f.write(toml.dumps(original_config))
        else:
            toml_data = tomli_w.dumps(original_config)
            if isinstance(toml_data, str):
                toml_data = toml_data.encode("utf-8")
            with open(config_file, "wb") as f:
                f.write(toml_data)

        # Verify file exists
        assert config_file.exists()

        # Read back and verify
        import tomllib

        with open(config_file, "rb") as f:
            loaded_config = tomllib.load(f)

        assert loaded_config["theme"]["name"] == "forest"
        assert_theme_config(loaded_config, "forest")


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.theme
def test_multiple_theme_configs():
    """Test creating and validating multiple theme configs."""
    themes = ["dracula", "monokai", "solarized", "forest", "ocean"]

    for theme_name in themes:
        config = create_test_theme_config(theme_name)
        assert_theme_config(config, theme_name)
        assert config["theme"]["name"] == theme_name
