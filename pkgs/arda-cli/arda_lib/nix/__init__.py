"""Nix operations module.

This module provides Nix command wrappers and utilities.
"""

from .nix import (
    Flake,
    FlakeCache,
    FlakeCacheEntry,
    FlakeError,
    NixError,
    Packages,
    SelectError,
    find_store_references,
    get_physical_store_path,
    nix_add_to_gcroots,
    nix_build,
    nix_command,
    nix_config,
    nix_eval,
    nix_flake_show,
    nix_metadata,
    nix_shell,
    nix_store,
)

__all__ = [
    "Flake",
    "FlakeCache",
    "FlakeCacheEntry",
    "FlakeError",
    "NixError",
    "Packages",
    "SelectError",
    "find_store_references",
    "get_physical_store_path",
    "nix_add_to_gcroots",
    "nix_build",
    "nix_command",
    "nix_config",
    "nix_eval",
    "nix_flake_show",
    "nix_metadata",
    "nix_shell",
    "nix_store",
]
