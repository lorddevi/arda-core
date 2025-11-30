"""Network utilities for testing.

This module provides port management and SSH connection utilities
for VM and container testing scenarios.
"""

from .port import (
    PortUtilsError,
    check_host_port_open,
    find_free_port,
    setup_port_forwarding,
    wait_for_port,
)
from .ssh import SSHConnection, test_ssh_connectivity

__all__ = [
    "PortUtilsError",
    "SSHConnection",
    "check_host_port_open",
    "find_free_port",
    "setup_port_forwarding",
    "test_ssh_connectivity",
    "wait_for_port",
]
