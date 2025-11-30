"""SSH connection utilities for VM testing.

Based on clan-core's nixos_test_lib/ssh.py
"""

import subprocess
from typing import Optional


class SSHConnection:
    """SSH connection wrapper for remote command execution."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 22,
        user: str = "root",
    ):
        """Initialize SSH connection.

        Args:
            host: SSH server hostname
            port: SSH server port
            user: SSH username

        """
        self.host = host
        self.port = port
        self.user = user
        self._connected = False

    def connect(self, key_file: str | None = None) -> bool:
        """Establish SSH connection.

        Args:
            key_file: Path to SSH private key file

        Returns:
            True if connection succeeded, False otherwise

        """
        try:
            ssh_cmd = ["ssh"]

            if key_file:
                ssh_cmd.extend(["-i", key_file])

            ssh_cmd.extend(
                [
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-p",
                    str(self.port),
                    f"{self.user}@{self.host}",
                    "true",
                ]
            )

            result = subprocess.run(  # noqa: S603
                ssh_cmd,
                capture_output=True,
                timeout=10,
            )

            self._connected = result.returncode == 0
            return self._connected

        except Exception:
            self._connected = False
            return False

    def execute(
        self,
        command: str,
        timeout: int = 30,
        key_file: str | None = None,
    ) -> tuple[int, str, str]:
        """Execute command via SSH.

        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            key_file: Path to SSH private key file

        Returns:
            Tuple of (return_code, stdout, stderr)

        Raises:
            RuntimeError: If SSH not connected

        """
        if not self._connected:
            raise RuntimeError("SSH not connected")

        ssh_cmd = ["ssh"]

        if key_file:
            ssh_cmd.extend(["-i", key_file])

        ssh_cmd.extend(
            [
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-p",
                str(self.port),
                f"{self.user}@{self.host}",
                command,
            ]
        )

        result = subprocess.run(  # noqa: S603
            ssh_cmd,
            capture_output=True,
            timeout=timeout,
            text=True,
        )

        return result.returncode, result.stdout, result.stderr

    def disconnect(self) -> None:
        """Disconnect SSH connection."""
        self._connected = False


def test_ssh_connectivity(host: str = "localhost", port: int = 22) -> bool:
    """Test if SSH port is accessible.

    Args:
        host: Hostname to test
        port: SSH port to test

    Returns:
        True if SSH is accessible, False otherwise

    """
    try:
        result = subprocess.run(  # noqa: S603
            ["nc", "-z", "-w", "5", host, str(port)],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, Exception):
        return False
