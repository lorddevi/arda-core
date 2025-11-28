"""Test Nix operations with real file system and mock subprocess.

This test file verifies the Nix integration system works correctly with real
file system operations, subprocess mocking, and error handling.
"""

import subprocess
import sys
from pathlib import Path as PathLib
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path to import arda_cli
sys.path.insert(0, str(PathLib(__file__).parent.parent.parent.parent.parent))

# Import nix functions and errors
# Import pytest helpers for subprocess mocking
from pytest_helpers import (
    create_mock_nix_eval_success,
)

from arda_lib.nix.nix import (
    BuildError,
    NixError,
    nix_build,
    nix_command,
    nix_eval,
)


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_eval_json_success():
    """Test successful nix eval with JSON output."""
    # Mock subprocess.run to return successful result
    mock_result = create_mock_nix_eval_success('{"key": "value"}')

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        result = nix_eval("nixpkgs", "packages")

        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]

        # Check that it includes nix eval command (as a list)
        assert args[0] == "nix"
        assert "eval" in args
        assert any("nixpkgs" in str(arg) for arg in args)

        # Verify result
        assert result == {"key": "value"}


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_eval_with_attribute():
    """Test nix eval with specific attribute path."""
    mock_result = create_mock_nix_eval_success('{"version": "1.0.0"}')

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        result = nix_eval("nixpkgs#hello", "meta.version")

        args = mock_run.call_args[0][0]
        assert args[0] == "nix"
        assert "eval" in args
        assert any("meta.version" in str(arg) for arg in args)
        assert result == {"version": "1.0.0"}


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_eval_raw_output():
    """Test nix eval with raw (non-JSON) output."""
    # Mock result with plain text output (as bytes since text=True will decode)
    mock_result = MagicMock()
    mock_result.stdout = "2.0.0\n"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result):
        result = nix_eval("nixpkgs", "packages", json_output=False)

        # Verify result is the raw string (text=True already decoded it)
        assert result.strip() == "2.0.0"


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_eval_error_handling():
    """Test nix eval error handling."""
    # Create an exception for nix error
    mock_exception = subprocess.CalledProcessError(
        1, ["nix", "eval"], stderr="error: attribute 'nonexistent' does not exist"
    )

    with patch("subprocess.run", side_effect=mock_exception):
        with pytest.raises(NixError) as exc_info:
            nix_eval("nixpkgs", "nonexistent")

        assert "nonexistent" in str(exc_info.value)


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_build_success():
    """Test successful nix build operation."""
    mock_result = MagicMock()
    mock_result.stdout = "/nix/store/abc123-hello-2.0.0\n"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result):
        result = nix_build("nixpkgs#hello")

        assert result == ["/nix/store/abc123-hello-2.0.0"]


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_build_with_out_link():
    """Test nix build with output link."""
    mock_result = MagicMock()
    mock_result.stdout = "/nix/store/abc123-hello-2.0.0\n"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        result = nix_build("nixpkgs#hello", out_link="result")

        args = mock_run.call_args[0][0]
        assert "--out-link" in args
        assert "result" in args
        assert result == ["/nix/store/abc123-hello-2.0.0"]


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_build_error_handling():
    """Test nix build error handling."""
    # Create an exception for build error
    mock_exception = subprocess.CalledProcessError(
        1,
        ["nix", "build"],
        stderr="error: Package 'nonexistent' in nixpkgs has an unfree license",
    )

    with patch("subprocess.run", side_effect=mock_exception):
        with pytest.raises(BuildError) as exc_info:
            nix_build("nixpkgs#nonexistent")

        assert "unfree license" in str(exc_info.value)


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_command_construction():
    """Test nix command construction with various options."""
    # Test nix_command directly (it doesn't call subprocess.run)
    cmd = nix_command(
        ["eval", "nixpkgs#version"], nix_options=["--accept-flake-config"]
    )

    # Verify nix command structure
    assert cmd[0] == "nix"
    assert "eval" in cmd
    assert "nixpkgs#version" in cmd
    assert "--accept-flake-config" in cmd


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_eval_flake_lock():
    """Test nix eval with flake.lock updates."""
    # Create an exception for flake error
    mock_exception = subprocess.CalledProcessError(
        1,
        ["nix", "eval"],
        stderr="error: flake.lock is not writable (override with --no-write-lock)",
    )

    with patch("subprocess.run", side_effect=mock_exception):
        with pytest.raises(NixError) as exc_info:
            nix_eval("nixpkgs", "version")

        assert "flake.lock" in str(exc_info.value)
        assert "--no-write-lock" in str(exc_info.value)


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_build_multiple_outputs():
    """Test nix build with multiple outputs."""
    mock_result = MagicMock()
    mock_result.stdout = (
        "/nix/store/abc123-hello-2.0.0\n/nix/store/def456-hello-2.0.0-doc\n"
    )
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result):
        result = nix_build("nixpkgs#hello")

        # Verify multiple outputs are split correctly
        assert len(result) == 2
        assert "/nix/store/abc123-hello-2.0.0" in result
        assert "/nix/store/def456-hello-2.0.0-doc" in result


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_command_with_extra_options():
    """Test nix command with extra keyword options."""
    mock_result = MagicMock()
    mock_result.stdout = "ok\n"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result):
        # nix_command doesn't call subprocess, it just builds the command
        # Let's just test that it builds the command correctly
        cmd = nix_command(["eval", "nixpkgs#version"], nix_options=["--verbose"])

        # Verify command structure
        assert cmd[0] == "nix"
        assert "eval" in cmd
        assert "--verbose" in cmd
        assert any("--option" in str(arg) for arg in cmd)


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.nix
def test_nix_eval_with_extra_args():
    """Test nix eval with extra arguments passed via kwargs."""
    mock_result = create_mock_nix_eval_success('{"system": "x86_64-linux"}')

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        # Test nix_eval with a custom option passed through kwargs
        result = nix_eval("nixpkgs", "system", verbose=True)

        args = mock_run.call_args[0][0]

        # Verify nix command was built with kwargs
        assert args[0] == "nix"
        assert "eval" in args
        assert result == {"system": "x86_64-linux"}
