"""Arda Nix Library - Shared library for Nix operations.

This library provides comprehensive Nix integration for the arda ecosystem,
including flake querying, system management, and user environment handling.

Main modules:
- nix: Core Nix operations (eval, build, shell, etc.)
- machines: Machine configuration management
- flake: Flake introspection and utilities

Example usage:
    from arda_lib.nix import nix_eval, nix_build
    from arda_lib.machines import Machine

    # Query a flake attribute
    result = nix_eval("nixpkgs#hello", ...)

    # Build a derivation
    build_result = nix_build("flake#package", ...)
"""

# Core Nix operations
from .nix import (
    Flake,
    NixError,
    Packages,
    nix_build,
    nix_command,
    nix_config,
    nix_eval,
    nix_metadata,
    nix_shell,
    nix_store,
)

# Export all by default for convenience
__all__ = [
    "Flake",
    "NixError",
    "Packages",
    "nix_build",
    "nix_command",
    "nix_config",
    "nix_eval",
    "nix_metadata",
    "nix_shell",
    "nix_store",
]

__version__ = "0.1.5"
