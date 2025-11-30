"""Port management utilities for VM testing.

Based on clan-core's nixos_test_lib/port.py
"""

import socket
import subprocess
import time


class PortUtilsError(Exception):
    """Port utils related errors."""


def find_free_port(start: int = 8000, end: int = 9000) -> int:
    """Find an available port in the given range.

    Args:
        start: Starting port number (inclusive)
        end: Ending port number (inclusive)

    Returns:
        Port number that is available

    Raises:
        RuntimeError: If no available port found

    """
    for port in range(start, end + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("localhost", port))
                return port
        except OSError:
            continue

    raise RuntimeError(f"No available port found in range {start}-{end}")


def check_host_port_open(
    host: str = "localhost", port: int = 8000, timeout: int = 5
) -> bool:
    """Check if a port is open on the host.

    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Connection timeout in seconds

    Returns:
        True if port is open, False otherwise

    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except (OSError, Exception) as e:
        print(f"Port check failed: {e}")
        return False


def setup_port_forwarding(
    local_port: int, remote_host: str, remote_port: int, ssh_user: str = "root"
) -> subprocess.Popen:
    """Set up port forwarding using SSH.

    Args:
        local_port: Local port to forward
        remote_host: Remote host to connect to
        remote_port: Remote port
        ssh_user: SSH user for the connection

    Returns:
        SSH process handle

    Raises:
        RuntimeError: If SSH is not available

    """
    ssh_cmd = [
        "ssh",
        "-N",
        "-L",
        f"{local_port}:{remote_host}:{remote_port}",
        f"{ssh_user}@{remote_host}",
    ]

    try:
        return subprocess.Popen(  # noqa: S603
            ssh_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except FileNotFoundError as err:
        raise RuntimeError("SSH not available for port forwarding") from None


def wait_for_port(
    host: str = "localhost",
    port: int = 8000,
    timeout: int = 30,
    check_interval: float = 0.5,
) -> bool:
    """Wait for a port to become available.

    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds

    Returns:
        True if port opened within timeout, False otherwise

    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_host_port_open(host, port, timeout=1):
            return True
        time.sleep(check_interval)

    return False
