# ruff: noqa: S603,S608
"""Core Nix operations for arda.

This module provides low-level Nix command wrappers and utilities.
Inspired by clan-lib's nix operations but adapted for arda's architecture.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, ClassVar

# Allow subprocess calls and string formatting in error messages

# Nix-select hash placeholder
# This will be replaced with the actual hash during build by ardaSource function
NIX_SELECT_HASH: str = "@nix_select_hash@"

# Default Nix options
DEFAULT_NIX_OPTIONS = [
    "experimental-features",
    "nix-command",
    "flakes",
]

# Nix-select path (will be available via symlink during build)
# The ardaSource function creates: $out/arda_cli/select -> nix-select-source
NIX_SELECT_PATH = os.path.join(os.path.dirname(__file__), "select")


class NixError(Exception):
    """Base exception for Nix operations."""

    pass


class FlakeError(NixError):
    """Exception specific to flake operations."""

    pass


class BuildError(NixError):
    """Exception specific to build operations."""

    pass


def nix_command(
    args: list[str],
    nix_options: list[str] | None = None,
    **kwargs,
) -> list[str]:
    """Build a nix command with proper options.

    Args:
        args: Nix subcommand and arguments
        nix_options: Additional Nix options
        **kwargs: Additional arguments passed to subprocess

    Returns:
        Full command list for subprocess

    """
    cmd = ["nix"]

    # Add experimental features
    options = DEFAULT_NIX_OPTIONS.copy()
    if nix_options:
        options.extend(nix_options)

    for option in options:
        cmd.extend(["--option", option, "true"])

    cmd.extend(args)
    return cmd


def nix_eval(
    flake_ref: str,
    attribute: str | None = None,
    json_output: bool = True,
    **kwargs,
) -> Any:
    """Evaluate a Nix expression or flake attribute.

    Args:
        flake_ref: Flake reference (e.g., "nixpkgs#hello" or "flake:path:/my/flake")
        attribute: Specific attribute to evaluate
        json_output: Whether to request JSON output
        **kwargs: Additional arguments passed to subprocess

    Returns:
        Evaluated result (parsed JSON if json_output=True)

    Raises:
        NixError: If evaluation fails

    """
    args = ["eval", "--impure", "--no-write-lock-file"]

    # Construct flake reference
    if attribute:
        ref = f"{flake_ref}#{attribute}"
    else:
        ref = flake_ref

    if json_output:
        args.append("--json")
        args.append(ref)

    cmd = nix_command(args, **kwargs)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        if json_output:
            return json.loads(result.stdout)
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        raise NixError(f"Nix eval failed: {e.stderr}") from e


def nix_build(
    flake_ref: str,
    attribute: str | None = None,
    out_link: str | None = None,
    **kwargs,
) -> list[str]:
    """Build a Nix derivation.

    Args:
        flake_ref: Flake reference
        attribute: Specific attribute to build
        out_link: Output symlink name
        **kwargs: Additional arguments passed to subprocess

    Returns:
        List of built output paths

    Raises:
        BuildError: If build fails

    """
    args = ["build", "--impure", "--no-write-lock-file"]

    # Construct flake reference
    ref = f"{flake_ref}#{attribute}" if attribute else flake_ref
    args.append(ref)

    # Add output link if specified
    if out_link:
        args.extend(["--out-link", out_link])

    cmd = nix_command(args, **kwargs)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse output paths
        output = result.stdout.strip()
        if output:
            return output.split("\n")
        return []

    except subprocess.CalledProcessError as e:
        raise BuildError(f"Nix build failed: {e.stderr}") from e


def nix_shell(
    packages: list[str],
    command: str | None = None,
    **kwargs,
) -> int:
    """Run a command in a Nix shell with specified packages.

    Args:
        packages: List of packages to include in shell
        command: Command to run (if None, starts interactive shell)
        **kwargs: Additional arguments passed to subprocess

    Returns:
        Return code of the command

    """
    args = ["shell", "--impure", "--no-write-lock-file"]

    # Add packages
    for pkg in packages:
        args.append(pkg)

    # Add command if specified
    if command:
        args.extend(["--command", command])

    cmd = nix_command(args, **kwargs)

    try:
        result = subprocess.run(cmd, **kwargs)
        return result.returncode

    except subprocess.CalledProcessError as e:
        raise NixError(f"Nix shell failed: {e.stderr}") from e


def nix_metadata(flake_ref: str, **kwargs) -> dict[str, Any]:
    """Get metadata about a flake.

    Args:
        flake_ref: Flake reference
        **kwargs: Additional arguments passed to subprocess

    Returns:
        Flake metadata as dictionary

    Raises:
        FlakeError: If metadata fetch fails

    """
    args = ["flake", "metadata", "--json", flake_ref]

    cmd = nix_command(args, **kwargs)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    except subprocess.CalledProcessError as e:
        raise FlakeError(f"Flake metadata fetch failed: {e.stderr}") from e


def nix_config(**kwargs) -> dict[str, Any]:
    """Get current Nix configuration.

    Args:
        **kwargs: Additional arguments passed to subprocess

    Returns:
        Nix configuration as dictionary

    Raises:
        NixError: If config fetch fails

    """
    args = ["config", "show", "--json"]

    cmd = nix_command(args, **kwargs)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    except subprocess.CalledProcessError as e:
        raise NixError(f"Nix config fetch failed: {e.stderr}") from e


def nix_store(query: str, **kwargs) -> dict[str, Any]:
    """Query Nix store information.

    Args:
        query: Store query command
        **kwargs: Additional arguments passed to subprocess

    Returns:
        Query result

    Raises:
        NixError: If store query fails

    """
    args = ["store", "query", query]

    cmd = nix_command(args, **kwargs)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    except subprocess.CalledProcessError as e:
        raise NixError(f"Nix store query failed: {e.stderr}") from e


class Flake:
    """Flake class for flake introspection and operations.

    This class wraps flake operations and integrates with nix-select
    for advanced attribute selection.

    Attributes:
        path: Path to the flake
        flake_ref: Flake reference string
        metadata: Cached flake metadata

    """

    def __init__(self, path: str | Path, nix_options: list[str] | None = None):
        """Initialize Flake instance.

        Args:
            path: Path to the flake
            nix_options: Additional Nix options

        """
        self.path = Path(path)
        self.flake_ref = f"path:{self.path}"
        self.nix_options = nix_options or []
        self.metadata = None
        self._cache = {}

    def get_metadata(self) -> dict[str, Any]:
        """Get flake metadata, cached.

        Returns:
            Flake metadata

        """
        if self.metadata is None:
            self.metadata = nix_metadata(self.flake_ref, nix_options=self.nix_options)
        return self.metadata

    def eval(self, attribute: str | None = None, **kwargs) -> Any:
        """Evaluate a flake attribute.

        Args:
            attribute: Attribute to evaluate (if None, evaluates the whole flake)
            **kwargs: Additional arguments for nix_eval

        Returns:
            Evaluated attribute

        """
        return nix_eval(
            self.flake_ref,
            attribute=attribute,
            nix_options=self.nix_options,
            **kwargs,
        )

    def select(self, selector: str) -> Any:
        """Select attributes using nix-select syntax.

        Args:
            selector: nix-select selector string (e.g., "packages.*.name")

        Returns:
            Selected attributes

        Raises:
            FlakeError: If selection fails

        """
        # Import nix-select dynamically
        # The select module is symlinked during build
        try:
            select_module_path = NIX_SELECT_PATH
            if not os.path.exists(select_module_path):
                # Try from arda_cli for compatibility
                select_module_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "arda_cli",
                    "select",
                )

            # Add to path for import
            if select_module_path not in os.sys.path:
                os.sys.path.insert(0, select_module_path)

            from select.select import select as nix_select

            # Get flake data as JSON
            flake_data = self.eval()

            # Use nix-select to query
            result = nix_select(selector, flake_data)
            return result

        except ImportError as e:
            raise FlakeError(
                f"Failed to import nix-select module from {select_module_path}: {e}"
            ) from e
        except Exception as e:
            raise FlakeError(f"Nix-select query failed: {e}") from e

    def build(
        self,
        attribute: str | None = None,
        out_link: str | None = None,
        **kwargs,
    ) -> list[str]:
        """Build a flake attribute.

        Args:
            attribute: Attribute to build
            out_link: Output symlink name
            **kwargs: Additional arguments for nix_build

        Returns:
            List of built output paths

        """
        return nix_build(
            self.flake_ref,
            attribute=attribute,
            out_link=out_link,
            nix_options=self.nix_options,
            **kwargs,
        )

    def __repr__(self) -> str:
        """Return string representation of Flake object."""
        return f"Flake(path={self.path})"


class Packages:
    """Class for managing Nix package allowlists.

    This provides security by restricting which packages can be used
    in shell operations, similar to clan's approach.
    """

    # Default allowed packages (from clan-clan's allowed-packages.json)
    DEFAULT_ALLOWED: ClassVar[set[str]] = {
        "git",
        "nix",
        "bash",
        "python3",
        "python3Packages.pip",
        "python3Packages.virtualenv",
        "python3Packages.pytest",
        "curl",
        "wget",
        "jq",
        "yq",
        "tree",
        "htop",
        "vim",
        "nano",
    }

    def __init__(self, allowed_packages: set | None = None):
        """Initialize Packages with allowlist.

        Args:
            allowed_packages: Set of allowed packages

        """
        self.allowed_packages = allowed_packages or self.DEFAULT_ALLOWED.copy()

    def is_allowed(self, package: str) -> bool:
        """Check if package is allowed.

        Args:
            package: Package name to check

        Returns:
            True if package is allowed

        """
        # Check exact match
        if package in self.allowed_packages:
            return True

        # Check if package is a attribute path that's allowed
        # e.g., "python3Packages pytest" is allowed if "python3Packages" is in allowlist
        parts = package.split(".")
        for i in range(len(parts)):
            parent = ".".join(parts[: i + 1])
            if parent in self.allowed_packages:
                return True

        return False

    def assert_allowed(self, package: str) -> None:
        """Assert that package is allowed.

        Args:
            package: Package name to check

        Raises:
            NixError: If package is not allowed

        """
        if not self.is_allowed(package):
            raise NixError(f"Package '{package}' is not in allowed packages list")

    def shell(self, packages: list[str], **kwargs) -> int:
        """Run command in shell with allowed packages.

        Args:
            packages: List of packages
            **kwargs: Additional arguments for nix_shell

        Returns:
            Return code of the command

        Raises:
            NixError: If any package is not allowed

        """
        # Verify all packages are allowed
        for pkg in packages:
            self.assert_allowed(pkg)

        return nix_shell(packages, **kwargs)
