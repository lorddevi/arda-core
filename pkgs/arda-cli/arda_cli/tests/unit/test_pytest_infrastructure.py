"""Test to verify pytest infrastructure is working correctly."""

import pytest


@pytest.mark.fast
@pytest.mark.unit
def test_infrastructure_setup():
    """Verify pytest infrastructure is configured correctly."""
    assert True


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_config_marker():
    """Verify config marker works."""
    assert True


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.theme
def test_theme_marker():
    """Verify theme marker works."""
    assert True


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.cli
def test_cli_marker():
    """Verify CLI marker works."""
    assert True
