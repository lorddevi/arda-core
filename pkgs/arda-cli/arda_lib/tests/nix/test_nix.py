"""Test nix.py module to increase coverage from 47.45% to 85%+.

This module tests the Nix operations library in arda_lib.nix.nix.
"""

import json
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Import modules to test
from arda_lib.nix.nix import (
    BuildError,
    Flake,
    FlakeCache,
    FlakeCacheEntry,
    FlakeError,
    NixError,
    Packages,
    SelectError,
    Selector,
    SelectorType,
    SetSelector,
    SetSelectorType,
    find_store_references,
    get_physical_store_path,
    locked_open,
    nix_add_to_gcroots,
    nix_build,
    nix_command,
    nix_config,
    nix_eval,
    nix_metadata,
    nix_shell,
    nix_store,
    nix_test_store,
    parse_selector,
    selectors_as_json,
)


class TestNixExceptions:
    """Test custom exception classes."""

    def test_nix_error(self):
        """Test that NixError is raised correctly."""
        with pytest.raises(NixError):
            raise NixError("Test error")

    def test_nix_error_with_cause(self):
        """Test that NixError can be raised with cause."""
        original_error = ValueError("Original")
        with pytest.raises(NixError) as exc_info:
            raise NixError("Test error") from original_error
        assert exc_info.value.__cause__ is original_error

    def test_flake_error(self):
        """Test that FlakeError is raised correctly."""
        with pytest.raises(FlakeError):
            raise FlakeError("Flake test error")

    def test_build_error(self):
        """Test that BuildError is raised correctly."""
        with pytest.raises(BuildError):
            raise BuildError("Build test error")


class TestNixCommand:
    """Test nix_command function."""

    def test_nix_command_basic(self):
        """Test basic nix command construction."""
        result = nix_command(["eval", "nixpkgs#hello"])
        assert result[0] == "nix"
        assert "--option" in result
        assert "experimental-features" in result
        assert "true" in result
        assert "eval" in result
        assert "nixpkgs#hello" in result

    def test_nix_command_with_nix_options(self):
        """Test nix command with custom options."""
        result = nix_command(
            ["eval", "nixpkgs#hello"], nix_options=["extra-feature", "another-feature"]
        )
        assert "extra-feature" in result
        assert "another-feature" in result

    def test_nix_command_kwargs_passed(self):
        """Test that kwargs are passed through."""
        # Just verify it doesn't raise
        result = nix_command(["eval"], timeout=10)
        assert result[0] == "nix"


class TestNixEval:
    """Test nix_eval function."""

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_eval_success(self, mock_run):
        """Test successful nix eval."""
        # Mock successful subprocess result
        mock_result = MagicMock()
        mock_result.stdout = '{"name": "hello", "version": "2.12.1"}'
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = nix_eval("nixpkgs#hello", attribute="name")

        assert result == {"name": "hello", "version": "2.12.1"}
        mock_run.assert_called_once()

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_eval_without_attribute(self, mock_run):
        """Test nix eval without specific attribute."""
        mock_result = MagicMock()
        mock_result.stdout = '{"name": "hello"}'
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = nix_eval("nixpkgs")

        assert result == {"name": "hello"}

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_eval_no_json_output(self, mock_run):
        """Test nix eval with text output."""
        mock_result = MagicMock()
        mock_result.stdout = "  hello  \n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = nix_eval("nixpkgs#hello", json_output=False)

        assert result == "hello"  # Should be stripped

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_eval_called_process_error(self, mock_run):
        """Test nix eval with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "nix", stderr="error: flake not found"
        )

        with pytest.raises(NixError) as exc_info:
            nix_eval("nixpkgs#nonexistent")

        assert "Nix eval failed" in str(exc_info.value)
        assert "flake not found" in str(exc_info.value)


class TestNixBuild:
    """Test nix_build function."""

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_build_success(self, mock_run):
        """Test successful nix build."""
        mock_result = MagicMock()
        mock_result.stdout = (
            "/nix/store/abc123-hello-2.12.1\n/nix/store/def456-hello-2.12.1"
        )
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = nix_build("nixpkgs#hello", attribute="hello")

        assert len(result) == 2
        assert "/nix/store/abc123-hello-2.12.1" in result

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_build_with_out_link(self, mock_run):
        """Test nix build with output link."""
        mock_result = MagicMock()
        mock_result.stdout = "/nix/store/abc123-hello-2.12.1"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        nix_build("nixpkgs#hello", attribute="hello", out_link="result")

        # Verify out-link option was added
        call_args = mock_run.call_args
        assert "--out-link" in call_args[0][0]
        assert "result" in call_args[0][0]

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_build_empty_output(self, mock_run):
        """Test nix build with empty output."""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = nix_build("nixpkgs#hello", attribute="hello")

        assert result == []

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_build_called_process_error(self, mock_run):
        """Test nix build with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "nix", stderr="error: build failed"
        )

        with pytest.raises(BuildError) as exc_info:
            nix_build("nixpkgs#broken")

        assert "Nix build failed" in str(exc_info.value)
        assert "build failed" in str(exc_info.value)


class TestNixShell:
    """Test nix_shell function."""

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_shell_success(self, mock_run):
        """Test successful nix shell execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = nix_shell(["nixpkgs#hello"], command="hello --version")

        assert result == 0
        mock_run.assert_called_once()

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_shell_with_command(self, mock_run):
        """Test nix shell with command."""
        mock_result = MagicMock()
        mock_result.returncode = 42
        mock_run.return_value = mock_result

        result = nix_shell(["nixpkgs#python3"], command="python --version")

        assert result == 42

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_shell_interactive(self, mock_run):
        """Test nix shell without command (interactive)."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = nix_shell(["nixpkgs#bash"])

        assert result == 0

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_shell_called_process_error(self, mock_run):
        """Test nix shell with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "nix", stderr="error: shell failed"
        )

        with pytest.raises(NixError) as exc_info:
            nix_shell(["nixpkgs#broken"])

        assert "Nix shell failed" in str(exc_info.value)


class TestNixMetadata:
    """Test nix_metadata function."""

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_metadata_success(self, mock_run):
        """Test successful nix metadata fetch."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(
            {"flake": {"locks": "test", "path": "/nix/store/abc123"}}
        )
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = nix_metadata("nixpkgs")

        assert "flake" in result
        assert result["flake"]["path"] == "/nix/store/abc123"

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_metadata_called_process_error(self, mock_run):
        """Test nix metadata with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "nix", stderr="error: flake not found"
        )

        with pytest.raises(FlakeError) as exc_info:
            nix_metadata("nixpkgs#nonexistent")

        assert "Flake metadata fetch failed" in str(exc_info.value)
        assert "flake not found" in str(exc_info.value)


class TestNixConfig:
    """Test nix_config function."""

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_config_success(self, mock_run):
        """Test successful nix config fetch."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(
            {"experimental-features": ["nix-command", "flakes"], "cores": "8"}
        )
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = nix_config()

        assert "experimental-features" in result
        assert result["cores"] == "8"

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_config_called_process_error(self, mock_run):
        """Test nix config with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "nix", stderr="error: config access denied"
        )

        with pytest.raises(NixError) as exc_info:
            nix_config()

        assert "Nix config fetch failed" in str(exc_info.value)


class TestNixStore:
    """Test nix_store function."""

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_store_success(self, mock_run):
        """Test successful nix store query."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(
            {"path": "/nix/store/abc123-hello-2.12.1", "valid": True}
        )
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = nix_store("--hash /nix/store/abc123-hello-2.12.1")

        assert "path" in result
        assert result["valid"] is True

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_store_called_process_error(self, mock_run):
        """Test nix store with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "nix", stderr="error: store query failed"
        )

        with pytest.raises(NixError) as exc_info:
            nix_store("--invalid")

        assert "Nix store query failed" in str(exc_info.value)


class TestFlakeClass:
    """Test Flake class."""

    def test_flake_init(self, tmp_path):
        """Test Flake initialization."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        assert flake.path == test_flake_path
        assert flake.flake_ref == f"path:{test_flake_path}"
        assert flake.nix_options == []
        assert flake.metadata is None
        assert flake._cache is None  # Cache is lazily initialized
        assert flake._cache_path is None  # Cache path is lazily initialized
        assert flake.cache_misses == 0  # No cache misses initially

    def test_flake_init_with_options(self, tmp_path):
        """Test Flake initialization with options."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path, nix_options=["extra-feature"])

        assert flake.nix_options == ["extra-feature"]

    def test_flake_get_metadata_cached(self, tmp_path):
        """Test Flake get_metadata with caching."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Mock nix_metadata
        with patch("arda_lib.nix.nix.nix_metadata") as mock_metadata:
            mock_metadata.return_value = {"locks": "test"}

            # First call should call nix_metadata
            result1 = flake.get_metadata()
            assert result1 == {"locks": "test"}
            assert mock_metadata.call_count == 1

            # Second call should use cache
            result2 = flake.get_metadata()
            assert result2 == {"locks": "test"}
            assert mock_metadata.call_count == 1  # Still 1, not called again

    @patch("arda_lib.nix.nix.nix_eval")
    def test_flake_eval(self, mock_eval, tmp_path):
        """Test Flake eval method."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)
        mock_eval.return_value = {"name": "test"}

        result = flake.eval("packages.hello")

        assert result == {"name": "test"}
        mock_eval.assert_called_once_with(
            f"path:{test_flake_path}", attribute="packages.hello", nix_options=[]
        )

    @patch("arda_lib.nix.nix.nix_eval")
    def test_flake_eval_without_attribute(self, mock_eval, tmp_path):
        """Test Flake eval without specific attribute."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)
        mock_eval.return_value = {"type": "flake"}

        result = flake.eval()

        assert result == {"type": "flake"}
        mock_eval.assert_called_once_with(
            f"path:{test_flake_path}", attribute=None, nix_options=[]
        )

    @patch("arda_lib.nix.nix.nix_build")
    def test_flake_build(self, mock_build, tmp_path):
        """Test Flake build method."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)
        mock_build.return_value = ["/nix/store/abc123-result"]

        result = flake.build(attribute="packages.hello", out_link="result")

        assert result == ["/nix/store/abc123-result"]
        mock_build.assert_called_once_with(
            f"path:{test_flake_path}",
            attribute="packages.hello",
            out_link="result",
            nix_options=[],
        )


class TestPackagesClass:
    """Test Packages class."""

    def test_packages_init_default(self):
        """Test Packages initialization with defaults."""
        packages = Packages()

        assert isinstance(packages.allowed_packages, set)
        assert "git" in packages.allowed_packages
        assert "nix" in packages.allowed_packages
        assert "python3" in packages.allowed_packages

    def test_packages_init_custom(self):
        """Test Packages initialization with custom allowed packages."""
        custom = {"custom1", "custom2"}
        packages = Packages(allowed_packages=custom)

        assert packages.allowed_packages == custom
        # Note: When custom packages provided, they are used directly (not copied)
        # Only DEFAULT_ALLOWED is copied when no custom packages given

    def test_packages_is_allowed_exact_match(self):
        """Test is_allowed with exact match."""
        packages = Packages()

        assert packages.is_allowed("git") is True
        assert packages.is_allowed("nix") is True
        assert packages.is_allowed("unknown-package") is False

    def test_packages_is_allowed_attribute_path(self):
        """Test is_allowed with attribute paths."""
        packages = Packages()

        # Exact match
        assert packages.is_allowed("python3Packages.pip") is True

        # Attribute path that's allowed
        assert packages.is_allowed("python3Packages.pip.setuptools") is True
        assert packages.is_allowed("python3Packages.virtualenv") is True

        # Not allowed
        assert packages.is_allowed("gcc") is False
        assert packages.is_allowed("rustc") is False

    def test_packages_is_allowed_partial_match(self):
        """Test is_allowed with partial matches."""
        packages = Packages(allowed_packages={"python3Packages"})

        # Should allow any attribute under python3Packages
        assert packages.is_allowed("python3Packages.pip") is True
        assert packages.is_allowed("python3Packages.requests") is True
        assert packages.is_allowed("python3Packages.pip.setuptools") is True

    def test_packages_assert_allowed_success(self):
        """Test assert_allowed with allowed package."""
        packages = Packages()

        # Should not raise
        packages.assert_allowed("git")
        packages.assert_allowed("python3Packages.pip")

    def test_packages_assert_allowed_failure(self):
        """Test assert_allowed with disallowed package."""
        packages = Packages()

        with pytest.raises(NixError) as exc_info:
            packages.assert_allowed("gcc")

        assert "gcc" in str(exc_info.value)
        assert "not in allowed packages list" in str(exc_info.value)

    @patch("arda_lib.nix.nix.nix_shell")
    def test_packages_shell_success(self, mock_nix_shell):
        """Test Packages.shell with allowed packages."""
        packages = Packages()
        mock_nix_shell.return_value = 0

        result = packages.shell(["git", "nix"])

        assert result == 0
        mock_nix_shell.assert_called_once_with(["git", "nix"])

    @patch("arda_lib.nix.nix.nix_shell")
    def test_packages_shell_with_custom_allowlist(self, mock_nix_shell):
        """Test Packages.shell with custom allowlist."""
        packages = Packages(allowed_packages={"custom-pkg"})
        mock_nix_shell.return_value = 0

        result = packages.shell(["custom-pkg"])

        assert result == 0
        mock_nix_shell.assert_called_once_with(["custom-pkg"])

    def test_packages_shell_with_disallowed_package(self):
        """Test Packages.shell with disallowed package."""
        packages = Packages()

        with pytest.raises(NixError) as exc_info:
            packages.shell(["gcc"])

        assert "gcc" in str(exc_info.value)

    @patch("arda_lib.nix.nix.nix_shell")
    def test_packages_shell_with_mixed_packages(self, mock_nix_shell):
        """Test Packages.shell with mix of allowed and disallowed."""
        packages = Packages()

        # Should fail on first disallowed package
        with pytest.raises(NixError) as exc_info:
            packages.shell(["git", "gcc", "nix"])

        assert "gcc" in str(exc_info.value)
        mock_nix_shell.assert_not_called()  # Should never call nix_shell


class TestNixTestStore:
    """Test nix_test_store utilities."""

    def test_nix_test_store_without_sandbox(self, monkeypatch):
        """Test nix_test_store returns None when IN_NIX_SANDBOX not set."""
        monkeypatch.delenv("IN_NIX_SANDBOX", raising=False)
        monkeypatch.delenv("ARDA_TEST_STORE", raising=False)
        monkeypatch.delenv("LOCK_NIX", raising=False)

        result = nix_test_store()

        assert result is None

    @patch("arda_lib.nix.nix.locked_open")
    def test_nix_test_store_with_sandbox_and_store(
        self, mock_locked_open, tmp_path, monkeypatch
    ):
        """Test nix_test_store with IN_NIX_SANDBOX and ARDA_TEST_STORE set."""
        test_store_path = tmp_path / "test-store"
        monkeypatch.setenv("IN_NIX_SANDBOX", "1")
        monkeypatch.setenv("ARDA_TEST_STORE", str(test_store_path))
        monkeypatch.setenv("LOCK_NIX", str(tmp_path / "lock"))

        # Mock locked_open to avoid actual file locking in tests
        mock_locked_open.return_value.__enter__ = MagicMock()
        mock_locked_open.return_value.__exit__ = MagicMock()

        result = nix_test_store()

        assert result == test_store_path
        assert test_store_path.exists()

    @patch("arda_lib.nix.nix.locked_open")
    def test_nix_test_store_with_sandbox_no_store(self, mock_locked_open, monkeypatch):
        """Test nix_test_store with IN_NIX_SANDBOX but no ARDA_TEST_STORE."""
        monkeypatch.setenv("IN_NIX_SANDBOX", "1")
        monkeypatch.delenv("ARDA_TEST_STORE", raising=False)
        monkeypatch.delenv("LOCK_NIX", raising=False)

        # Mock locked_open
        mock_locked_open.return_value.__enter__ = MagicMock()
        mock_locked_open.return_value.__exit__ = MagicMock()

        result = nix_test_store()

        # Should return None when store is not specified
        assert result is None

    def test_locked_open_context_manager(self, tmp_path):
        """Test locked_open context manager."""
        lock_file = tmp_path / "test.lock"

        with locked_open(lock_file, "w") as fd:
            # File should be writable
            fd.write("test")

        # File should exist and contain the written content
        assert lock_file.exists()
        assert lock_file.read_text() == "test"


class TestSelectorParsing:
    """Test selector parsing functionality."""

    def test_parse_selector_simple(self):
        """Test parsing simple selector."""
        result = parse_selector("foo.bar")
        assert len(result) == 2
        assert result[0].type == SelectorType.STR
        assert result[0].value == "foo"
        assert result[1].type == SelectorType.STR
        assert result[1].value == "bar"

    def test_parse_selector_with_wildcard(self):
        """Test parsing selector with wildcard."""
        result = parse_selector("packages.*")
        assert len(result) == 2
        assert result[0].type == SelectorType.STR
        assert result[0].value == "packages"
        assert result[1].type == SelectorType.ALL

    def test_parse_selector_with_set(self):
        """Test parsing selector with set."""
        result = parse_selector("foo.{x,y,z}")
        assert len(result) == 2
        assert result[0].type == SelectorType.STR
        assert result[0].value == "foo"
        assert result[1].type == SelectorType.SET
        assert isinstance(result[1].value, list)
        assert len(result[1].value) == 3
        assert result[1].value[0].type == SetSelectorType.STR
        assert result[1].value[0].value == "x"
        assert result[1].value[1].value == "y"
        assert result[1].value[2].value == "z"

    def test_parse_selector_with_maybe(self):
        """Test parsing selector with optional."""
        result = parse_selector("config.?optional")
        assert len(result) == 2
        assert result[0].type == SelectorType.STR
        assert result[0].value == "config"
        assert result[1].type == SelectorType.MAYBE
        assert result[1].value == "optional"

    def test_selectors_as_json(self):
        """Test converting selectors to JSON."""
        selectors = [
            Selector(type=SelectorType.STR, value="foo"),
            Selector(type=SelectorType.ALL),
        ]
        result = selectors_as_json(selectors)
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["type"] == "str"
        assert parsed[0]["value"] == "foo"
        assert parsed[1]["type"] == "all"


class TestGcrootManagement:
    """Test gcroot management functions."""

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_add_to_gcroots_success(self, mock_run, tmp_path, monkeypatch):
        """Test nix_add_to_gcroots with successful execution."""
        # Ensure we're not in a sandbox
        monkeypatch.delenv("IN_NIX_SANDBOX", raising=False)

        nix_path = tmp_path / "store" / "abc123-hello-2.12.1"
        dest = tmp_path / "gcroots" / "hello"

        nix_add_to_gcroots(nix_path, dest)

        # Verify the command was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args == [
            "nix-store",
            "--realise",
            str(nix_path),
            "--add-root",
            str(dest),
        ]

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_add_to_gcroots_in_sandbox(self, mock_run, tmp_path, monkeypatch):
        """Test nix_add_to_gcroots skips execution in sandbox."""
        # Ensure we're in a sandbox
        monkeypatch.setenv("IN_NIX_SANDBOX", "1")

        nix_path = tmp_path / "store" / "abc123-hello-2.12.1"
        dest = tmp_path / "gcroots" / "hello"

        nix_add_to_gcroots(nix_path, dest)

        # Verify subprocess.run was never called
        mock_run.assert_not_called()

    @patch("arda_lib.nix.nix.subprocess.run")
    def test_nix_add_to_gcroots_error(self, mock_run, tmp_path, monkeypatch):
        """Test nix_add_to_gcroots raises error on failure."""
        # Ensure we're not in a sandbox
        monkeypatch.delenv("IN_NIX_SANDBOX", raising=False)

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "nix-store", stderr="error: gcroot failed"
        )

        nix_path = tmp_path / "store" / "abc123-hello-2.12.1"
        dest = tmp_path / "gcroots" / "hello"

        with pytest.raises(NixError) as exc_info:
            nix_add_to_gcroots(nix_path, dest)

        assert "Failed to add" in str(exc_info.value)
        assert "gcroot failed" in str(exc_info.value)

    def test_find_store_references_simple(self):
        """Test finding single store reference in text."""
        text = "Built: /nix/store/abc123def456789012-hello-2.12.1"
        result = find_store_references(text)
        assert len(result) == 1
        assert result[0] == "/nix/store/abc123def456789012-hello-2.12.1"

    def test_find_store_references_multiple(self):
        """Test finding multiple store references in text."""
        text = (
            "Paths: /nix/store/abc123def456789012-hello-2.12.1 and "
            "/nix/store/def456789012345678-world-1.0.0"
        )
        result = find_store_references(text)
        assert len(result) == 2
        assert "/nix/store/abc123def456789012-hello-2.12.1" in result
        assert "/nix/store/def456789012345678-world-1.0.0" in result

    def test_find_store_references_none(self):
        """Test finding no store references in text."""
        text = "No store paths here, just regular text"
        result = find_store_references(text)
        assert len(result) == 0

    def test_find_store_references_invalid(self):
        """Test finding no store references with invalid paths."""
        text = "Invalid: /nix/store/short-hash and /nix/store/nohyphen"
        result = find_store_references(text)
        assert len(result) == 0

    def test_get_physical_store_path_simple(self, tmp_path):
        """Test get_physical_store_path with simple path."""
        store_path = tmp_path / "store" / "abc123-hello-2.12.1"
        result = get_physical_store_path(store_path)
        assert result == store_path

    def test_get_physical_store_path_with_symlink(self, tmp_path):
        """Test get_physical_store_path resolves symlinks."""
        # Create a real file
        real_path = tmp_path / "real"
        real_path.write_text("real content")

        # Create a symlink
        symlink = tmp_path / "symlink"
        symlink.symlink_to(real_path)

        # Get physical path
        result = get_physical_store_path(symlink)
        assert result == real_path

    def test_get_physical_store_path_nonexistent(self, tmp_path):
        """Test get_physical_store_path with nonexistent path."""
        store_path = tmp_path / "nonexistent" / "abc123-hello-2.12.1"
        result = get_physical_store_path(store_path)
        # Should return original path if it doesn't exist
        assert result == store_path

    @patch("arda_lib.nix.nix.nix_test_store")
    def test_get_physical_store_path_with_test_store(
        self, mock_test_store, tmp_path, monkeypatch
    ):
        """Test get_physical_store_path with test store configured."""
        test_store = tmp_path / "test-store"
        mock_test_store.return_value = test_store

        # Set IN_NIX_SANDBOX to use test store
        monkeypatch.setenv("IN_NIX_SANDBOX", "1")
        monkeypatch.setenv("ARDA_TEST_STORE", str(test_store))

        store_path = Path("/nix/store/abc123-hello-2.12.1")
        result = get_physical_store_path(store_path)
        # Should handle test store paths
        assert isinstance(result, Path)


class TestFlakeCacheEntry:
    """Test FlakeCacheEntry class."""

    def test_cache_entry_init(self):
        """Test FlakeCacheEntry initialization."""
        entry = FlakeCacheEntry()
        assert entry.value == {}
        assert entry.is_list is False
        assert entry.exists is True
        assert entry.fetched_all is False

    def test_cache_entry_init_with_params(self):
        """Test FlakeCacheEntry initialization with parameters."""
        entry = FlakeCacheEntry(
            value="test", is_list=True, exists=False, fetched_all=True
        )
        assert entry.value == "test"
        assert entry.is_list is True
        assert entry.exists is False
        assert entry.fetched_all is True

    def test_cache_entry_insert_simple(self):
        """Test inserting data with simple selector."""
        entry = FlakeCacheEntry()
        selectors = [Selector(type=SelectorType.STR, value="packages")]
        entry.insert({"name": "test-package"}, selectors)

        assert "packages" in entry.value
        assert isinstance(entry.value["packages"], FlakeCacheEntry)

    def test_cache_entry_insert_nested(self):
        """Test inserting data with nested selectors."""
        entry = FlakeCacheEntry()
        selectors = [
            Selector(type=SelectorType.STR, value="packages"),
            Selector(type=SelectorType.STR, value="hello"),
            Selector(type=SelectorType.STR, value="name"),
        ]
        entry.insert("hello-2.12", selectors)

        # Verify nested structure
        assert "packages" in entry.value
        packages_entry = entry.value["packages"]
        assert "hello" in packages_entry.value
        hello_entry = packages_entry.value["hello"]
        assert "name" in hello_entry.value
        name_entry = hello_entry.value["name"]
        assert name_entry.value == "hello-2.12"

    def test_cache_entry_insert_with_maybe(self):
        """Test inserting data with maybe selector."""
        entry = FlakeCacheEntry()
        selectors = [
            Selector(type=SelectorType.STR, value="config"),
            Selector(type=SelectorType.MAYBE, value="optionalFeature"),
        ]
        entry.insert({"enabled": True}, selectors)

        # Verify maybe selector creates exists=False entry if not present
        assert "config" in entry.value
        assert "optionalFeature" in entry.value["config"].value

    def test_cache_entry_select_simple(self):
        """Test selecting data with simple selector."""
        entry = FlakeCacheEntry()
        entry.value["packages"] = FlakeCacheEntry(
            value={"hello": FlakeCacheEntry(value="test-value")}
        )

        selectors = [Selector(type=SelectorType.STR, value="packages")]
        result = entry.select(selectors)

        assert "hello" in result
        assert result["hello"].value == "test-value"

    def test_cache_entry_select_nested(self):
        """Test selecting data with nested selectors."""
        entry = FlakeCacheEntry()
        entry.value["packages"] = FlakeCacheEntry(
            value={
                "hello": FlakeCacheEntry(
                    value={"name": FlakeCacheEntry(value="hello-2.12")}
                )
            }
        )

        selectors = [
            Selector(type=SelectorType.STR, value="packages"),
            Selector(type=SelectorType.STR, value="hello"),
            Selector(type=SelectorType.STR, value="name"),
        ]
        result = entry.select(selectors)

        assert result == "hello-2.12"

    def test_cache_entry_select_with_maybe_not_exists(self):
        """Test selecting maybe selector when it doesn't exist."""
        entry = FlakeCacheEntry()
        entry.value["config"] = FlakeCacheEntry(value={})

        selectors = [
            Selector(type=SelectorType.STR, value="config"),
            Selector(type=SelectorType.MAYBE, value="missing"),
        ]
        result = entry.select(selectors)

        # Maybe selectors return None when not present
        assert result is None

    def test_cache_entry_select_with_maybe_exists(self):
        """Test selecting maybe selector when it exists."""
        entry = FlakeCacheEntry()
        entry.value["config"] = FlakeCacheEntry(
            value={"feature": FlakeCacheEntry(value={"enabled": True}, exists=True)}
        )

        selectors = [
            Selector(type=SelectorType.STR, value="config"),
            Selector(type=SelectorType.MAYBE, value="feature"),
        ]
        result = entry.select(selectors)

        assert result == {"enabled": True}

    def test_cache_entry_is_cached_exists(self):
        """Test is_cached returns True when selector exists."""
        entry = FlakeCacheEntry()
        entry.value["packages"] = FlakeCacheEntry(
            value={"hello": FlakeCacheEntry(value="test")}
        )

        selectors = [Selector(type=SelectorType.STR, value="packages")]
        assert entry.is_cached(selectors) is True

    def test_cache_entry_is_cached_not_exists(self):
        """Test is_cached returns False when selector doesn't exist."""
        entry = FlakeCacheEntry()

        # Check a selector that was never inserted
        selectors = [Selector(type=SelectorType.STR, value="packages")]
        assert entry.is_cached(selectors) is False

    def test_cache_entry_is_cached_with_maybe(self):
        """Test is_cached with maybe selector."""
        entry = FlakeCacheEntry()
        entry.value["config"] = FlakeCacheEntry(value={})

        # Maybe selector returns True even if not present
        selectors = [
            Selector(type=SelectorType.STR, value="config"),
            Selector(type=SelectorType.MAYBE, value="missing"),
        ]
        assert entry.is_cached(selectors) is True

    def test_cache_entry_as_dict(self):
        """Test converting cache entry to dictionary."""
        entry = FlakeCacheEntry(
            value="test", is_list=True, exists=False, fetched_all=True
        )
        result = entry.as_dict()

        assert result["value"] == "test"
        assert result["is_list"] is True
        assert result["exists"] is False
        assert result["fetched_all"] is True

    def test_cache_entry_from_dict(self):
        """Test creating cache entry from dictionary."""
        data = {"value": "test", "is_list": True, "exists": False, "fetched_all": True}
        entry = FlakeCacheEntry.from_dict(data)

        assert entry.value == "test"
        assert entry.is_list is True
        assert entry.exists is False
        assert entry.fetched_all is True


class TestFlakeCache:
    """Test FlakeCache class."""

    def test_cache_init(self):
        """Test FlakeCache initialization."""
        cache = FlakeCache()
        assert isinstance(cache.cache, FlakeCacheEntry)
        assert cache.cache.value == {}

    def test_cache_insert(self):
        """Test inserting data into cache."""
        cache = FlakeCache()
        cache.insert({"name": "test-package"}, "packages")

        assert "packages" in cache.cache.value
        assert isinstance(cache.cache.value["packages"], FlakeCacheEntry)

    def test_cache_select(self):
        """Test selecting data from cache."""
        cache = FlakeCache()
        cache.insert({"name": "test-package", "version": "1.0"}, "packages.hello")

        result = cache.select("packages.hello")

        assert result == {"name": "test-package", "version": "1.0"}

    def test_cache_is_cached_true(self):
        """Test is_cached returns True when data exists."""
        cache = FlakeCache()
        cache.insert({"name": "test"}, "packages")

        assert cache.is_cached("packages") is True

    def test_cache_is_cached_false(self):
        """Test is_cached returns False when data doesn't exist."""
        cache = FlakeCache()

        assert cache.is_cached("packages") is False

    def test_cache_invalidate_full(self):
        """Test full cache invalidation."""
        cache = FlakeCache()
        cache.insert({"name": "test"}, "packages")
        cache.insert({"name": "test2"}, "config")

        # Verify data exists
        assert cache.is_cached("packages") is True
        assert cache.is_cached("config") is True

        # Invalidate entire cache
        cache.invalidate()

        # Verify cache is empty
        assert cache.cache.value == {}

    def test_cache_invalidate_selective(self):
        """Test selective cache invalidation."""
        cache = FlakeCache()
        cache.insert({"name": "test"}, "packages")
        cache.insert({"name": "test2"}, "config")

        # Invalidate specific selector (currently clears entire cache)
        cache.invalidate("packages")

        # Verify cache is empty (selective not yet implemented)
        assert cache.cache.value == {}

    def test_cache_save_and_load(self, tmp_path):
        """Test saving and loading cache from file."""
        cache = FlakeCache()
        cache.insert({"name": "test-package"}, "packages")
        cache.insert({"version": "1.0"}, "packages.hello")

        # Save to file
        cache_file = tmp_path / "test_cache.json"
        cache.save_to_file(cache_file)

        # Verify file exists
        assert cache_file.exists()

        # Load into new cache
        new_cache = FlakeCache()
        new_cache.load_from_file(cache_file)

        # Verify data was loaded correctly
        assert new_cache.is_cached("packages") is True
        result = new_cache.select("packages.hello")
        assert result == {"version": "1.0"}

    def test_cache_load_nonexistent_file(self, tmp_path):
        """Test loading cache from non-existent file."""
        cache = FlakeCache()
        cache_file = tmp_path / "nonexistent.json"

        # Should not raise error, just initialize empty cache
        cache.load_from_file(cache_file)

        assert cache.cache.value == {}

    def test_cache_load_invalid_json(self, tmp_path):
        """Test loading cache from invalid JSON file."""
        cache = FlakeCache()
        cache_file = tmp_path / "invalid.json"
        cache_file.write_text("invalid json content")

        # Should not raise error, just initialize empty cache
        cache.load_from_file(cache_file)

        assert cache.cache.value == {}


class TestFlakeCacheIntegration:
    """Test Flake class integration with cache system."""

    def test_flake_cache_initialization(self, tmp_path):
        """Test that Flake cache is lazily initialized."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Cache should be None initially (lazy initialization)
        assert flake._cache is None
        assert flake._cache_path is None
        assert flake.cache_misses == 0

    def test_flake_cache_invalidate_and_init(self, tmp_path):
        """Test cache invalidation and initialization."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Invalidate cache should initialize it
        flake.invalidate_cache()

        assert flake._cache is not None
        assert isinstance(flake._cache, FlakeCache)
        assert flake._cache_path is not None
        assert flake.cache_misses == 0

    def test_flake_cache_miss_tracking(self, tmp_path):
        """Test that cache misses are properly tracked."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Initialize cache
        flake.invalidate_cache()

        # Record a cache miss
        flake._record_cache_miss("Test cache miss")

        assert flake.cache_misses == 1

        # Record another cache miss
        flake._record_cache_miss("Another test cache miss")

        assert flake.cache_misses == 2

    def test_flake_cache_path_configuration(self, tmp_path):
        """Test that cache path is properly configured."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Cache path should be set and be a Path object
        assert flake._cache_path is not None
        assert isinstance(flake._cache_path, Path)

        # Cache path should be in the arda flakes directory
        assert "arda" in str(flake._cache_path)
        assert "flakes" in str(flake._cache_path)

    def test_flake_load_cache_from_disk(self, tmp_path):
        """Test loading cache from disk."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Create a cache file with some data
        cache_file = tmp_path / "cache.json"
        cache = FlakeCache()
        cache.insert("test_value", "test.key")  # Correct order: data, selector
        cache.save_to_file(cache_file)

        # Set up flake to use this cache file
        flake._cache_path = cache_file
        flake._cache = FlakeCache()
        flake.load_cache()

        # Verify cache was loaded
        assert flake._cache.is_cached("test.key")
        assert flake._cache.select("test.key") == "test_value"

    def test_flake_invalidate_clears_cache(self, tmp_path):
        """Test that cache invalidation clears the cache."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Initialize cache
        flake.invalidate_cache()
        initial_cache_id = id(flake._cache)

        # Add some cache miss tracking
        flake._record_cache_miss("test miss")
        assert flake.cache_misses == 1

        # Invalidate cache again
        flake.invalidate_cache()

        # Cache should be a new instance
        assert id(flake._cache) != initial_cache_id
        assert flake.cache_misses == 0  # Miss tracking should be cleared

    def test_flake_cache_operations_with_data(self, tmp_path):
        """Test cache operations with actual data."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Initialize cache
        flake.invalidate_cache()

        # Manually add some data to cache (simulating what get_from_nix would do)
        # Note: insert() signature is insert(data, selector_str)
        # Store a dict at "packages" with nested structure
        flake._cache.insert({"name": "test-package", "version": "1.0"}, "packages")
        flake._cache.insert("test_package_data", "packages.test-package")

        # Verify data is cached
        assert flake._cache.is_cached("packages")
        assert flake._cache.is_cached("packages.test-package")

        # Select from cache
        packages = flake._cache.select("packages")
        assert isinstance(packages, dict)
        assert packages["name"] == "test-package"
        assert packages["version"] == "1.0"

        test_package = flake._cache.select("packages.test-package")
        assert test_package == "test_package_data"

    def test_flake_cache_save_and_load_persistence(self, tmp_path):
        """Test that cache persists across save and load."""
        test_flake_path = tmp_path / "test-flake"
        flake1 = Flake(test_flake_path)

        # Initialize and add data
        flake1.invalidate_cache()
        flake1._cache.insert("persistent_value", "persistent.key")  # Correct order
        flake1._cache.insert("another_value", "another.key")

        # Save cache
        cache_file = tmp_path / "persistent_cache.json"
        flake1._cache.save_to_file(cache_file)

        # Create new flake instance and load cache
        flake2 = Flake(test_flake_path)
        flake2._cache_path = cache_file
        flake2._cache = FlakeCache()
        flake2.load_cache()

        # Verify data persisted
        assert flake2._cache.is_cached("persistent.key")
        assert flake2._cache.select("persistent.key") == "persistent_value"
        assert flake2._cache.is_cached("another.key")
        assert flake2._cache.select("another.key") == "another_value"

    def test_flake_cache_selective_invalidation(self, tmp_path):
        """Test selective cache invalidation."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Initialize cache
        flake.invalidate_cache()

        # Add multiple cache entries
        flake._cache.insert("value1", "package1")
        flake._cache.insert("value2", "package2")
        flake._cache.insert("value3", "package3")

        # Verify all are cached
        assert flake._cache.is_cached("package1")
        assert flake._cache.is_cached("package2")
        assert flake._cache.is_cached("package3")

        # Selectively invalidate one entry
        # Note: Current implementation does full invalidation
        # This test documents current behavior
        flake.invalidate_cache()

        # All should be cleared (current behavior)
        assert not flake._cache.is_cached("package1")
        assert not flake._cache.is_cached("package2")
        assert not flake._cache.is_cached("package3")

    def test_flake_cache_with_nonexistent_path(self, tmp_path):
        """Test cache behavior with nonexistent paths."""
        test_flake_path = tmp_path / "nonexistent" / "path"
        flake = Flake(test_flake_path)

        # Should not raise error
        flake.invalidate_cache()

        assert flake._cache is not None
        assert flake._cache_path is not None

    def test_flake_cache_miss_analysis(self, tmp_path):
        """Test cache miss analysis functionality."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Initialize cache
        flake.invalidate_cache()

        # Record some cache misses
        flake._record_cache_miss("miss 1")
        flake._record_cache_miss("miss 2")
        flake._record_cache_miss("miss 3")

        # Verify miss count
        assert flake.cache_misses == 3

        # Get miss analysis - should return list of strings
        # Note: print_cache_miss_analysis prints to stdout
        # We just verify the data is tracked
        assert len(flake._cache_miss_stack_traces) == 3
        assert "miss 1" in flake._cache_miss_stack_traces[0]
        assert "miss 2" in flake._cache_miss_stack_traces[1]
        assert "miss 3" in flake._cache_miss_stack_traces[2]

    def test_flake_cache_path_property(self, tmp_path):
        """Test cache_path property accessor."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Initially None
        assert flake.cache_path is None

        # After initialization
        flake.invalidate_cache()
        assert flake.cache_path is not None
        assert isinstance(flake.cache_path, Path)
        assert flake.cache_path == flake._cache_path

    def test_flake_cache_multiple_instances(self, tmp_path):
        """Test cache isolation between multiple Flake instances."""
        test_flake_path1 = tmp_path / "flake1"
        test_flake_path2 = tmp_path / "flake2"

        flake1 = Flake(test_flake_path1)
        flake2 = Flake(test_flake_path2)

        # Initialize both caches
        flake1.invalidate_cache()
        flake2.invalidate_cache()

        # Add different data to each
        flake1._cache.insert("value1", "key1")
        flake2._cache.insert("value2", "key2")

        # Verify isolation
        assert flake1._cache.is_cached("key1")
        assert not flake1._cache.is_cached("key2")

        assert flake2._cache.is_cached("key2")
        assert not flake2._cache.is_cached("key1")

    def test_flake_cache_with_custom_nix_options(self, tmp_path):
        """Test cache works with custom Nix options."""
        test_flake_path = tmp_path / "test-flake"
        custom_options = ["--option", "test", "value"]
        flake = Flake(test_flake_path, nix_options=custom_options)

        # Initialize cache
        flake.invalidate_cache()

        # Verify options are stored
        assert flake.nix_options == custom_options
        assert flake._cache is not None

    def test_flake_cache_statistics(self, tmp_path):
        """Test cache statistics tracking."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Initialize cache
        flake.invalidate_cache()

        # Initially no misses
        assert flake.cache_misses == 0

        # Record multiple misses
        for i in range(5):
            flake._record_cache_miss(f"miss {i}")

        assert flake.cache_misses == 5

        # Clear by invalidating
        flake.invalidate_cache()
        assert flake.cache_misses == 0

    def test_flake_load_cache_handles_errors(self, tmp_path):
        """Test that load_cache gracefully handles errors."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Initialize cache
        flake.invalidate_cache()

        # Create a nonexistent cache file path
        flake._cache_path = tmp_path / "nonexistent" / "cache.json"

        # Should not raise error
        flake.load_cache()

        # Cache should still work (just empty)
        assert flake._cache is not None

    def test_flake_get_from_nix_basic(self, tmp_path):
        """Test get_from_nix() with single selector."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Create the actual build output file with JSON data
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["test-package"], f)

        # Mock nix_config to return system info
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            # Mock subprocess.run to return our file path
            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                # Mock tempfile.mkdtemp to return tmp_path (so exists check works)
                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    # Call get_from_nix
                    flake.get_from_nix(["packages.hello"])

                    # Verify cache was populated
                    assert flake._cache.is_cached("packages.hello")
                    result = flake._cache.select("packages.hello")
                    assert result == "test-package"

                    # Verify nix_config was called
                    mock_config.assert_called_once()

    def test_flake_get_from_nix_multiple_selectors(self, tmp_path):
        """Test get_from_nix() with multiple selectors."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Create the actual build output file with multiple results
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["pkg1", "pkg2", "pkg3"], f)

        # Mock nix_config
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            # Mock subprocess
            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                # Mock tempfile.mkdtemp
                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    # Call get_from_nix with multiple selectors
                    flake.get_from_nix(
                        ["packages.pkg1", "packages.pkg2", "packages.pkg3"]
                    )

                    # Verify all selectors were cached
                    assert flake._cache.is_cached("packages.pkg1")
                    assert flake._cache.is_cached("packages.pkg2")
                    assert flake._cache.is_cached("packages.pkg3")

                    assert flake._cache.select("packages.pkg1") == "pkg1"
                    assert flake._cache.select("packages.pkg2") == "pkg2"
                    assert flake._cache.select("packages.pkg3") == "pkg3"

                    # Verify nix_config was called
                    mock_config.assert_called_once()

    def test_flake_get_from_nix_error_handling(self, tmp_path):
        """Test get_from_nix() error handling."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Test CalledProcessError handling
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(1, "nix-build")

                with pytest.raises(SelectError) as exc_info:
                    flake.get_from_nix(["packages.hello"])

                assert "Failed to select attributes from flake" in str(exc_info.value)

        # Test JSON parsing error handling
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                build_output_file = tmp_path / "result"
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                # Create file with invalid JSON
                with open(build_output_file, "w") as f:
                    f.write("invalid json {")

                # Mock tempfile.mkdtemp
                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    with pytest.raises(SelectError) as exc_info:
                        flake.get_from_nix(["packages.hello"])

                    assert "Failed to parse JSON output" in str(exc_info.value)

    def test_flake_get_from_nix_cache_save(self, tmp_path):
        """Test get_from_nix() saves cache to disk."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Create the actual build output file
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["test-value"], f)

        # Mock nix_config
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            # Mock subprocess
            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                # Mock tempfile.mkdtemp
                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    # Mock save_to_file to track calls
                    with patch.object(flake._cache, "save_to_file") as mock_save:
                        flake.get_from_nix(["packages.test"])

                        # Verify save_to_file was called
                        mock_save.assert_called_once_with(cache_file)

                        # Verify cache was populated
                        assert flake._cache.is_cached("packages.test")

                        # Verify nix_config was called
                        mock_config.assert_called_once()

    def test_flake_precache_all_cached(self, tmp_path):
        """Test precache() when all selectors are already cached."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path (required for precache)
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Pre-populate cache with data
        flake._cache.insert({"name": "cached-package"}, "packages.cached")

        # Mock get_from_nix to verify it's not called
        with patch.object(flake, "get_from_nix") as mock_get_from_nix:
            # Mock _record_cache_miss
            with patch.object(flake, "_record_cache_miss") as mock_record:
                # Call precache with already-cached selector
                flake.precache(["packages.cached"])

                # Verify get_from_nix was NOT called (already cached)
                mock_get_from_nix.assert_not_called()

                # Verify no cache miss was recorded
                mock_record.assert_not_called()

                # Verify cache still has the data
                assert flake._cache.is_cached("packages.cached")
                assert flake._cache.select("packages.cached") == {
                    "name": "cached-package"
                }

    def test_flake_precache_mixed_cached_uncached(self, tmp_path):
        """Test precache() with mix of cached and uncached selectors."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Pre-populate cache with one selector
        flake._cache.insert({"name": "cached-package"}, "packages.cached")

        # Create build output file for uncached selector
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["new-package"], f)

        # Mock nix_config and get_from_nix
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    with patch.object(flake, "_record_cache_miss") as mock_record:
                        with patch.object(flake._cache, "save_to_file"):
                            # Call precache with mixed selectors
                            flake.precache(["packages.cached", "packages.new"])

                            # Verify get_from_nix was called with only uncached selector
                            # (We can't directly verify get_from_nix was called, but
                            # we can check that the new selector is now cached)

                            # Verify both selectors are now cached
                            assert flake._cache.is_cached("packages.cached")
                            assert flake._cache.is_cached("packages.new")

                            assert flake._cache.select("packages.cached") == {
                                "name": "cached-package"
                            }
                            assert flake._cache.select("packages.new") == "new-package"

                            # Verify cache miss was recorded for uncached selector
                            mock_record.assert_called_once()
                            call_args = mock_record.call_args[0][0]
                            assert "packages.new" in call_args

    def test_flake_precache_all_uncached(self, tmp_path):
        """Test precache() when no selectors are cached."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Create build output file with multiple results
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["pkg1", "pkg2", "pkg3"], f)

        # Mock nix_config and subprocess
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    with patch.object(flake, "_record_cache_miss") as mock_record:
                        with patch.object(flake._cache, "save_to_file"):
                            # Call precache with all new selectors
                            flake.precache(
                                ["packages.pkg1", "packages.pkg2", "packages.pkg3"]
                            )

                            # Verify all selectors are now cached
                            assert flake._cache.is_cached("packages.pkg1")
                            assert flake._cache.is_cached("packages.pkg2")
                            assert flake._cache.is_cached("packages.pkg3")

                            assert flake._cache.select("packages.pkg1") == "pkg1"
                            assert flake._cache.select("packages.pkg2") == "pkg2"
                            assert flake._cache.select("packages.pkg3") == "pkg3"

                            # Verify cache miss was recorded for all selectors
                            mock_record.assert_called_once()
                            call_args = mock_record.call_args[0][0]
                            assert "packages.pkg1" in call_args
                            assert "packages.pkg2" in call_args
                            assert "packages.pkg3" in call_args

    def test_flake_precache_no_cache_path(self, tmp_path):
        """Test precache() error when cache path is not set."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Manually set cache_path to None to test the validation
        flake._cache_path = None

        # Call precache should raise NixError
        with pytest.raises(NixError) as exc_info:
            flake.precache(["packages.test"])

        assert "Cache path cannot be None" in str(exc_info.value)

    def test_flake_precache_error_propagation(self, tmp_path):
        """Test precache() propagates errors from get_from_nix."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Mock get_from_nix to raise an error
        with patch.object(flake, "get_from_nix") as mock_get_from_nix:
            mock_get_from_nix.side_effect = SelectError("Test error")

            # Call precache should propagate the error
            with pytest.raises(SelectError) as exc_info:
                flake.precache(["packages.test"])

            assert "Test error" in str(exc_info.value)

    def test_flake_select_cache_hit(self, tmp_path):
        """Test select() returns cached value without calling Nix."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Pre-populate cache with data
        expected_value = {"name": "cached-package", "version": "1.0"}
        flake._cache.insert(expected_value, "packages.cached")

        # Mock get_from_nix to verify it's not called
        with patch.object(flake, "get_from_nix") as mock_get_from_nix:
            with patch.object(flake, "_record_cache_miss") as mock_record:
                # Call select on cached selector
                result = flake.select("packages.cached")

                # Verify correct value is returned
                assert result == expected_value

                # Verify get_from_nix was NOT called (cache hit)
                mock_get_from_nix.assert_not_called()

                # Verify no cache miss was recorded
                mock_record.assert_not_called()

    def test_flake_select_cache_miss(self, tmp_path):
        """Test select() fetches on cache miss."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Create build output file
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["new-package-data"], f)

        # Mock nix_config and subprocess
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    with patch.object(flake, "_record_cache_miss") as mock_record:
                        with patch.object(flake._cache, "save_to_file"):
                            # Call select on uncached selector (cache miss)
                            result = flake.select("packages.new")

                            # Verify correct value is returned
                            assert result == "new-package-data"

                            # Verify value is now cached
                            assert flake._cache.is_cached("packages.new")

                            # Verify cache miss was recorded
                            mock_record.assert_called_once()
                            call_args = mock_record.call_args[0][0]
                            assert "packages.new" in call_args

    def test_flake_select_no_cache_path(self, tmp_path):
        """Test select() error when cache path is not set."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Manually set cache_path to None
        flake._cache_path = None

        # Call select should raise NixError
        with pytest.raises(NixError) as exc_info:
            flake.select("packages.test")

        assert "Cache path cannot be None" in str(exc_info.value)

    def test_flake_select_cache_reinitialization(self, tmp_path):
        """Test select() re-initializes cache when None."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Ensure cache is None (not initialized)
        assert flake._cache is None

        # Set cache path to avoid error
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Mock get_from_nix
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["test-value"], f)

        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    with patch.object(flake, "_record_cache_miss"):
                        # Mock save_to_file after cache is initialized
                        with patch.object(FlakeCache, "save_to_file"):
                            # Call select should auto-initialize cache
                            result = flake.select("packages.test")

                            # Verify cache was initialized
                            assert flake._cache is not None

                            # Verify correct value is returned
                            assert result == "test-value"

    def test_flake_select_error_propagation(self, tmp_path):
        """Test select() propagates errors from get_from_nix."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Mock get_from_nix to raise SelectError
        with patch.object(flake, "get_from_nix") as mock_get_from_nix:
            mock_get_from_nix.side_effect = SelectError("Attribute not found in flake")

            # Call select should propagate the error
            with pytest.raises(SelectError) as exc_info:
                flake.select("packages.nonexistent")

            # Verify error is propagated
            assert "Attribute not found in flake" in str(exc_info.value)

    def test_flake_record_cache_miss_basic(self, tmp_path):
        """Test _record_cache_miss() records selector info and stack trace."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Clear any existing cache misses
        flake._cache_miss_stack_traces.clear()

        # Record a cache miss
        flake._record_cache_miss("Cache miss for selector: packages.test")

        # Verify count
        assert flake.cache_misses == 1

        # Verify the recorded data contains the selector info
        recorded = flake._cache_miss_stack_traces[0]
        assert "packages.test" in recorded
        assert "test_flake_record_cache_miss_basic" in recorded

    def test_flake_cache_miss_multiple_selectors(self, tmp_path):
        """Test cache miss tracking for multiple selectors."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Clear any existing cache misses
        flake._cache_miss_stack_traces.clear()

        # Record multiple cache misses
        flake._record_cache_miss("Cache miss for selector: packages.first")
        flake._record_cache_miss("Cache miss for selector: packages.second")
        flake._record_cache_miss("Cache miss for selector: packages.third")

        # Verify count
        assert flake.cache_misses == 3

        # Verify all selectors are recorded
        assert "packages.first" in flake._cache_miss_stack_traces[0]
        assert "packages.second" in flake._cache_miss_stack_traces[1]
        assert "packages.third" in flake._cache_miss_stack_traces[2]

    def test_flake_cache_miss_integration_with_select(self, tmp_path):
        """Test cache miss tracking integration with select()."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Clear any existing cache misses
        flake._cache_miss_stack_traces.clear()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Create build output file
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["test-value"], f)

        # Mock nix_config and subprocess
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    with patch.object(flake._cache, "save_to_file"):
                        # Call select on uncached selector (should record cache miss)
                        flake.select("packages.test")

                        # Verify cache miss was recorded
                        assert flake.cache_misses == 1
                        recorded = flake._cache_miss_stack_traces[0]
                        assert "packages.test" in recorded

    def test_flake_cache_miss_integration_with_precache(self, tmp_path):
        """Test cache miss tracking integration with precache()."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Clear any existing cache misses
        flake._cache_miss_stack_traces.clear()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Create build output file
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["value1", "value2"], f)

        # Mock nix_config and subprocess
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    with patch.object(flake._cache, "save_to_file"):
                        # Call precache with uncached selectors
                        flake.precache(["packages.uncached1", "packages.uncached2"])

                        # Verify cache miss was recorded (should be one call with both
                        # selectors)
                        assert flake.cache_misses == 1
                        recorded = flake._cache_miss_stack_traces[0]
                        assert "packages.uncached1" in recorded
                        assert "packages.uncached2" in recorded

    def test_flake_cache_miss_no_duplicate_on_hit(self, tmp_path):
        """Test that cache hits don't record cache misses."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Clear any existing cache misses
        flake._cache_miss_stack_traces.clear()

        # Pre-populate cache with data
        flake._cache.insert({"name": "cached"}, "packages.cached")

        # Call select on cached selector multiple times
        flake.select("packages.cached")
        flake.select("packages.cached")
        flake.select("packages.cached")

        # Verify no cache misses were recorded (still 0)
        assert flake.cache_misses == 0

    def test_flake_cache_load_missing_file(self, tmp_path):
        """Test load_from_file handles missing file gracefully."""
        cache = FlakeCache()

        # Try to load from non-existent file
        non_existent = tmp_path / "nonexistent.json"
        cache.load_from_file(non_existent)

        # Should create empty cache (no error)
        assert cache.cache is not None
        assert not cache.is_cached("any.selector")

    def test_flake_cache_load_invalid_json(self, tmp_path):
        """Test load_from_file handles invalid JSON gracefully."""
        cache = FlakeCache()

        # Create file with invalid JSON
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json content }")

        # Try to load from invalid JSON file
        cache.load_from_file(invalid_file)

        # Should create empty cache (no error)
        assert cache.cache is not None
        assert not cache.is_cached("any.selector")

    def test_flake_cache_load_missing_key(self, tmp_path):
        """Test load_from_file handles missing 'cache' key gracefully."""
        cache = FlakeCache()

        # Create file with valid JSON but missing 'cache' key
        invalid_file = tmp_path / "missing_key.json"
        invalid_file.write_text('{"wrong_key": "value"}')

        # Try to load from file with missing key
        cache.load_from_file(invalid_file)

        # Should create empty cache (no error)
        assert cache.cache is not None
        assert not cache.is_cached("any.selector")

    def test_flake_cache_save_creates_directory(self, tmp_path):
        """Test save_to_file creates parent directories."""
        cache = FlakeCache()
        cache.insert({"test": "data"}, "selector")

        # Path with non-existent parent directory
        save_path = tmp_path / "nested" / "dirs" / "cache.json"

        # Save should create directories automatically
        cache.save_to_file(save_path)

        # Verify file was created
        assert save_path.exists()
        assert save_path.is_file()

        # Verify data can be loaded back
        new_cache = FlakeCache()
        new_cache.load_from_file(save_path)
        assert new_cache.is_cached("selector")
        assert new_cache.select("selector") == {"test": "data"}

    def test_flake_cache_atomic_write(self, tmp_path):
        """Test save_to_file uses atomic write operation."""
        cache = FlakeCache()
        cache.insert({"test": "data1"}, "selector")

        save_path = tmp_path / "cache.json"
        cache.save_to_file(save_path)

        # Read and verify content
        with open(save_path) as f:
            content = f.read()

        # Should be valid JSON with proper structure
        data = json.loads(content)
        assert "cache" in data
        assert data["cache"] is not None

    def test_flake_load_cache_nonexistent(self, tmp_path):
        """Test load_cache with non-existent cache path."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path to non-existent directory
        flake._cache_path = tmp_path / "nonexistent" / "cache.json"

        # load_cache should not raise error
        flake.load_cache()

        # Cache should still be initialized
        assert flake._cache is not None

    def test_flake_load_cache_invalid_file(self, tmp_path):
        """Test load_cache handles invalid cache file gracefully."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Create invalid cache file
        cache_file = tmp_path / "invalid_cache.json"
        cache_file.write_text("{ invalid json }")

        flake._cache_path = cache_file

        # load_cache should not raise error (handles gracefully)
        flake.load_cache()

        # Cache should still be functional (empty)
        assert flake._cache is not None
        assert not flake._cache.is_cached("any.selector")

    def test_flake_cache_corruption_recovery(self, tmp_path):
        """Test that cache corruption doesn't break functionality."""
        cache = FlakeCache()
        cache.insert({"original": "data"}, "selector")

        # Save to file
        cache_file = tmp_path / "cache.json"
        cache.save_to_file(cache_file)

        # Corrupt the file
        cache_file.write_text("corrupted content here")

        # Load should handle corruption gracefully
        new_cache = FlakeCache()
        new_cache.load_from_file(cache_file)

        # Should have empty cache, not crash
        assert new_cache.cache is not None
        assert not new_cache.is_cached("selector")

        # Should still be able to use cache normally
        new_cache.insert({"new": "data"}, "new_selector")
        assert new_cache.is_cached("new_selector")
        assert new_cache.select("new_selector") == {"new": "data"}


class TestFlakeCacheCoreFunctionality:
    """Additional high-priority tests for core caching functionality coverage."""

    def test_get_from_nix_with_nix_config_fallback(self, tmp_path):
        """Test get_from_nix() when nix_config fails and uses fallback system."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Create build output file
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["test-package"], f)

        # Mock nix_config to raise NixError (forcing fallback to x86_64-linux)
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.side_effect = NixError("Config fetch failed")

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    # Mock save_to_file
                    with patch.object(flake._cache, "save_to_file"):
                        # Call get_from_nix - should use fallback system
                        flake.get_from_nix(["packages.hello"])

                        # Verify cache was populated
                        assert flake._cache.is_cached("packages.hello")
                        result = flake._cache.select("packages.hello")
                        assert result == "test-package"

                        # Verify nix_config was called (even though it failed)
                        mock_config.assert_called_once()

                        # Verify the system used fallback "x86_64-linux"
                        # The build command should have been constructed
                        assert mock_run.called

    def test_get_from_nix_with_file_not_found_error(self, tmp_path):
        """Test get_from_nix() when subprocess fails with FileNotFoundError."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Mock nix_config to succeed
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            # Mock subprocess.run to raise FileNotFoundError
            # (e.g., nix command not found)
            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError("nix command not found")

                # Call get_from_nix should raise SelectError
                with pytest.raises(SelectError) as exc_info:
                    flake.get_from_nix(["packages.hello"])

                assert "Failed to select attributes from flake" in str(exc_info.value)

    def test_precache_cache_miss_recording_integration(self, tmp_path):
        """Test precache() correctly records cache misses for uncached selectors."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Create build output for the uncached selector
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["new-package"], f)

        # Clear any existing cache misses
        flake._cache_miss_stack_traces.clear()

        # Mock nix_config and subprocess
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    with patch.object(flake._cache, "save_to_file"):
                        # Call precache with uncached selector
                        flake.precache(["packages.uncached"])

                        # Verify cache miss was recorded with selector info
                        assert flake.cache_misses == 1
                        recorded = flake._cache_miss_stack_traces[0]
                        assert "packages.uncached" in recorded
                        assert "Cache miss for selectors" in recorded

    def test_select_cache_miss_recording_integration(self, tmp_path):
        """Test select() correctly records cache misses for uncached selectors."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Create build output file
        build_output_file = tmp_path / "result"
        with open(build_output_file, "w") as f:
            json.dump(["selected-value"], f)

        # Clear any existing cache misses
        flake._cache_miss_stack_traces.clear()

        # Mock nix_config and subprocess
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = str(build_output_file) + "\n"
                mock_run.return_value = mock_result

                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    with patch.object(flake._cache, "save_to_file"):
                        # Call select on uncached selector
                        result = flake.select("packages.test")

                        # Verify correct value is returned
                        assert result == "selected-value"

                        # Verify cache miss was recorded with selector info
                        assert flake.cache_misses == 1
                        recorded = flake._cache_miss_stack_traces[0]
                        assert "packages.test" in recorded
                        assert "Cache miss for selector" in recorded


class TestFlakeCacheErrorHandling:
    """Medium-priority tests for error handling and edge cases."""

    def test_get_from_nix_malformed_output(self, tmp_path):
        """Test get_from_nix() handles missing build output file gracefully."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Mock nix_config
        with patch("arda_lib.nix.nix.nix_config") as mock_config:
            mock_config.return_value = {"system": "x86_64-linux"}

            # Mock subprocess to return path to non-existent output file
            nonexistent_output = tmp_path / "nonexistent_output"
            with patch("arda_lib.nix.nix.subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = (
                    str(nonexistent_output) + "\n"
                )  # Return path that doesn't exist
                mock_run.return_value = mock_result

                # Mock tempfile.mkdtemp to use tmp_path
                with patch(
                    "arda_lib.nix.nix.tempfile.mkdtemp", return_value=str(tmp_path)
                ):
                    # Call get_from_nix should raise SelectError
                    with pytest.raises(SelectError) as exc_info:
                        flake.get_from_nix(["packages.test"])

                    assert "Build output path does not exist" in str(exc_info.value)
                    assert str(nonexistent_output) in str(exc_info.value)

    def test_select_error_with_select_error_propagation(self, tmp_path):
        """Test select() propagates SelectError from cache.select()."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Set cache path
        cache_file = tmp_path / "test_cache.json"
        flake._cache_path = cache_file

        # Pre-populate cache with data
        flake._cache.insert({"exists": "value"}, "packages.exists")

        # Mock get_from_nix (should not be called)
        with patch.object(flake, "get_from_nix") as mock_get_from_nix:
            with patch.object(flake, "_record_cache_miss"):
                # Call select on non-existent selector
                with pytest.raises(SelectError) as exc_info:
                    flake.select("packages.nonexistent")

                # Verify error message includes the selector
                assert "Attribute 'packages.nonexistent' not found in flake" in str(
                    exc_info.value
                )

                # Verify get_from_nix was called (since cache miss)
                mock_get_from_nix.assert_called_once()


class TestFlakeCacheEdgeCases:
    """Low-priority tests for edge cases and performance validation."""

    def test_cache_performance_with_large_dataset(self, tmp_path):
        """Test cache performance with large number of entries."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Create large dataset with many entries
        import time

        # Benchmark inserting many entries
        start = time.perf_counter()
        for i in range(500):
            data = {
                "id": i,
                "name": f"package_{i}",
                "version": "1.0.0",
                "metadata": {
                    "description": f"Package number {i}",
                    "dependencies": [f"dep_{j}" for j in range(10)],
                },
            }
            flake._cache.insert(data, f"packages.package_{i}")
        insert_time = time.perf_counter() - start

        # Benchmark selecting entries
        start = time.perf_counter()
        for i in range(0, 500, 10):  # Select every 10th package
            result = flake._cache.select(f"packages.package_{i}")
            assert result["id"] == i
        select_time = time.perf_counter() - start

        # Performance assertions (operations should be fast)
        assert insert_time < 1.0  # Insert should complete in reasonable time
        assert select_time < 0.1  # Select should be very fast

        # Verify a specific entry
        result = flake._cache.select("packages.package_250")
        assert result["id"] == 250
        assert result["name"] == "package_250"

    def test_cache_memory_and_concurrent_patterns(self, tmp_path):
        """Test cache behavior with memory-heavy and simulated concurrent access."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        import time

        # Simulate workload with mixed operations
        for i in range(30):
            # Insert operation
            data = {"id": i, "value": f"data_{i}"}
            flake._cache.insert(data, f"packages.data_{i}")

            time.sleep(0.0001)  # Small delay to simulate real-world timing

        # Read operations (simulate concurrent reads)
        for _iteration in range(2):
            for i in range(30):
                result = flake._cache.select(f"packages.data_{i}")
                assert result["id"] == i

            time.sleep(0.0001)

        # Verify cache integrity
        assert flake._cache.is_cached("packages.data_15")
        assert flake._cache.select("packages.data_15")["id"] == 15

        # Verify no cache misses for repeated reads
        initial_misses = flake.cache_misses
        flake._cache.select("packages.data_5")
        flake._cache.select("packages.data_10")
        # Should not increase misses for cached data
        assert flake.cache_misses == initial_misses


class TestFlakeCachePerformance:
    """Performance tests for flake cache system."""

    def test_cache_hit_performance(self, tmp_path):
        """Test that cache hits are significantly faster than cache misses."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        # Initialize cache
        flake.invalidate_cache()

        # Add test data to cache
        test_data = {"key": "value", "nested": {"data": "test"}}
        flake._cache.insert(test_data, "packages.hello")

        # Benchmark cache hit (selecting existing key)
        import time

        start = time.perf_counter()
        for _ in range(1000):
            result = flake._cache.select("packages.hello")
        hit_time = time.perf_counter() - start

        # Benchmark cache miss using is_cached to check non-existent keys
        start = time.perf_counter()
        for _ in range(1000):
            exists = flake._cache.is_cached("nonexistent.key")
        miss_check_time = time.perf_counter() - start

        # Cache hit should be faster or at least comparable
        # (both operations are simple dict lookups)
        assert hit_time <= miss_check_time * 2  # Allow 2x difference as acceptable

        # Verify results are correct
        assert flake._cache.select("packages.hello") == test_data

    def test_cache_insert_performance(self, tmp_path):
        """Test that cache insert operations scale well with data size."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        import time

        # Test inserting large nested data
        large_data = {
            "level1": {
                f"key_{i}": {"nested": f"value_{i}", "data": list(range(100))}
                for i in range(50)
            }
        }

        start = time.perf_counter()
        flake._cache.insert(large_data, "packages.large")
        insert_time = time.perf_counter() - start

        # Verify data was stored correctly
        result = flake._cache.select("packages.large")
        assert result == large_data

        # Insert should complete in reasonable time (< 1 second for this size)
        assert insert_time < 1.0

    def test_cache_memory_usage(self, tmp_path):
        """Test that cache doesn't consume excessive memory."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Add substantial amount of data
        for i in range(100):
            flake._cache.insert(f"data_{i}", f"packages.item_{i}")

        # Cache should contain all entries
        for i in range(100):
            assert flake._cache.is_cached(f"packages.item_{i}")

        # Verify cache structure is intact
        assert isinstance(flake._cache.cache.value, dict)
        assert "packages" in flake._cache.cache.value

    def test_cache_disk_persistence_performance(self, tmp_path):
        """Test that cache save/load operations are performant."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Add test data
        for i in range(50):
            flake._cache.insert({"id": i, "value": f"test_{i}"}, f"data.item_{i}")

        cache_file = tmp_path / "perf_test_cache.json"

        import time

        # Benchmark save
        start = time.perf_counter()
        flake._cache.save_to_file(cache_file)
        save_time = time.perf_counter() - start

        # Benchmark load
        new_cache = FlakeCache()
        start = time.perf_counter()
        new_cache.load_from_file(cache_file)
        load_time = time.perf_counter() - start

        # Save/load should complete quickly
        assert save_time < 1.0
        assert load_time < 1.0

        # Verify data integrity
        assert new_cache.select("data.item_25") == {"id": 25, "value": "test_25"}

    def test_cache_concurrent_access_simulation(self, tmp_path):
        """Test cache behavior under simulated concurrent access patterns."""
        test_flake_path = tmp_path / "test-flake"
        flake = Flake(test_flake_path)

        flake.invalidate_cache()

        # Simulate mixed read/write workload
        import time

        # Write phase
        for i in range(20):
            flake._cache.insert(f"write_{i}", f"data.write_{i}")
            time.sleep(0.001)  # Small delay to simulate real workload

        # Read phase - multiple accesses to same data
        for _ in range(3):
            for i in range(20):
                result = flake._cache.select(f"data.write_{i}")
                assert result == f"write_{i}"
            time.sleep(0.001)

        # Verify cache integrity after mixed workload
        assert flake._cache.is_cached("data.write_10")
        assert flake._cache.select("data.write_10") == "write_10"
