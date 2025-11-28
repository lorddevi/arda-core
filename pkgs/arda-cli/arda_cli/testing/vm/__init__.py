"""VM Testing Infrastructure for Arda CLI.

This module provides VM management utilities for integration testing,
allowing tests to create, start, stop, and delete virtual machines.

Features:
- VM lifecycle management using KVM/QEMU/Virsh
- SSH connectivity for testing inside VMs
- Configurable VM resources (memory, disk, network)
- Automatic cleanup after tests
"""

from .exceptions import (
    VMCreateError,
    VMDeleteError,
    VMError,
    VMNotFoundError,
    VMStartError,
    VMStopError,
    VMTimeoutError,
)
from .vm import VM
from .vm_manager import VMManager

__all__ = [
    "VM",
    "VMCreateError",
    "VMDeleteError",
    "VMError",
    "VMManager",
    "VMNotFoundError",
    "VMStartError",
    "VMStopError",
    "VMTimeoutError",
]
