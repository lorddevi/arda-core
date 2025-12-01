"""Unit tests for SSH connection utilities.

This test suite ensures comprehensive coverage of all SSH-related
functions in the arda_cli.testing.network module.
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from arda_cli.testing.network.ssh import SSHConnection, test_ssh_connectivity


class TestSSHConnectionInit:
    """Test SSHConnection initialization."""

    @pytest.mark.unit
    def test_ssh_connection_default_init(self):
        """Test SSHConnection with default parameters."""
        conn = SSHConnection()

        assert conn.host == "localhost"
        assert conn.port == 22
        assert conn.user == "root"
        assert conn._connected is False

    @pytest.mark.unit
    def test_ssh_connection_custom_params(self):
        """Test SSHConnection with custom parameters."""
        conn = SSHConnection(host="example.com", port=2222, user="ubuntu")

        assert conn.host == "example.com"
        assert conn.port == 2222
        assert conn.user == "ubuntu"
        assert conn._connected is False

    @pytest.mark.unit
    def test_ssh_connection_connected_state(self):
        """Test SSHConnection tracks connection state."""
        conn = SSHConnection()

        # Initially not connected
        assert conn._connected is False

        # Set connected state
        conn._connected = True
        assert conn._connected is True


class TestSSHConnectionConnect:
    """Test SSHConnection.connect method."""

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_connect_success(self, mock_run):
        """Test successful SSH connection."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        result = conn.connect()

        assert result is True
        assert conn._connected is True

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_connect_failure(self, mock_run):
        """Test failed SSH connection."""
        # Mock failed subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        result = conn.connect()

        assert result is False
        assert conn._connected is False

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_connect_with_key_file(self, mock_run):
        """Test SSH connection with key file."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        result = conn.connect(key_file="/path/to/key")

        assert result is True

        # Verify SSH command includes key file
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        ssh_cmd = args[0]

        assert "-i" in ssh_cmd
        assert "/path/to/key" in ssh_cmd

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_connect_without_key_file(self, mock_run):
        """Test SSH connection without key file."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        result = conn.connect(key_file=None)

        assert result is True

        # Verify SSH command does not include key file
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        ssh_cmd = args[0]

        assert "-i" not in ssh_cmd

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_connect_command_structure(self, mock_run):
        """Test SSH connection command structure."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        conn = SSHConnection(host="example.com", port=2222, user="ubuntu")
        result = conn.connect()

        assert result is True

        # Verify command structure
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        ssh_cmd = args[0]

        # Check command elements
        assert ssh_cmd[0] == "ssh"
        assert "-o" in ssh_cmd
        assert "StrictHostKeyChecking=no" in ssh_cmd
        assert "UserKnownHostsFile=/dev/null" in ssh_cmd
        assert "-p" in ssh_cmd
        assert "2222" in ssh_cmd
        assert "ubuntu@example.com" in ssh_cmd
        assert "true" in ssh_cmd

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_connect_timeout(self, mock_run):
        """Test SSH connection respects timeout."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        conn = SSHConnection()
        result = conn.connect()

        # Verify timeout parameter
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 10

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_connect_exception_handling(self, mock_run):
        """Test SSH connection handles exceptions."""
        # Mock subprocess.run to raise exception
        mock_run.side_effect = Exception("Connection failed")

        conn = SSHConnection(host="localhost", port=22)
        result = conn.connect()

        # Should return False and not raise exception
        assert result is False
        assert conn._connected is False

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_connect_exception_captures_output(self, mock_run):
        """Test SSH connection captures output."""
        # Mock successful subprocess.run with output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"success"
        mock_result.stderr = b""
        mock_run.return_value = mock_result

        conn = SSHConnection()
        result = conn.connect()

        # Verify capture_output is used
        _, kwargs = mock_run.call_args
        assert kwargs["capture_output"] is True

        assert result is True
        assert conn._connected is True


class TestSSHConnectionExecute:
    """Test SSHConnection.execute method."""

    @pytest.mark.unit
    def test_execute_not_connected(self):
        """Test execute raises error when not connected."""
        conn = SSHConnection(host="localhost", port=22)

        with pytest.raises(RuntimeError, match="SSH not connected"):
            conn.execute("echo test")

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_execute_success(self, mock_run):
        """Test successful command execution."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "command output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        conn._connected = True  # Simulate connected state

        return_code, stdout, stderr = conn.execute("echo test")

        assert return_code == 0
        assert stdout == "command output"
        assert stderr == ""

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_execute_with_output(self, mock_run):
        """Test execute with command output."""
        # Mock subprocess.run with output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello, world!"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        conn._connected = True

        return_code, stdout, stderr = conn.execute("ls -la")

        assert return_code == 0
        assert stdout == "Hello, world!"
        assert stderr == ""

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_execute_with_error(self, mock_run):
        """Test execute with command error."""
        # Mock subprocess.run with error
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "command not found"
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        conn._connected = True

        return_code, stdout, stderr = conn.execute("invalid-command")

        assert return_code == 1
        assert stdout == ""
        assert stderr == "command not found"

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_execute_with_key_file(self, mock_run):
        """Test execute with SSH key file."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        conn._connected = True

        conn.execute("echo test", key_file="/path/to/key")

        # Verify SSH command includes key file
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        ssh_cmd = args[0]

        assert "-i" in ssh_cmd
        assert "/path/to/key" in ssh_cmd

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_execute_without_key_file(self, mock_run):
        """Test execute without SSH key file."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        conn._connected = True

        conn.execute("echo test")

        # Verify SSH command does not include key file
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        ssh_cmd = args[0]

        assert "-i" not in ssh_cmd

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_execute_command_structure(self, mock_run):
        """Test execute command structure."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        conn = SSHConnection(host="example.com", port=2222, user="ubuntu")
        conn._connected = True

        conn.execute("pwd")

        # Verify command structure
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        ssh_cmd = args[0]

        # Check command elements
        assert ssh_cmd[0] == "ssh"
        assert "-o" in ssh_cmd
        assert "StrictHostKeyChecking=no" in ssh_cmd
        assert "UserKnownHostsFile=/dev/null" in ssh_cmd
        assert "-p" in ssh_cmd
        assert "2222" in ssh_cmd
        assert "ubuntu@example.com" in ssh_cmd
        assert "pwd" in ssh_cmd  # The actual command

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_execute_timeout(self, mock_run):
        """Test execute respects timeout."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        conn._connected = True

        conn.execute("sleep 5", timeout=60)

        # Verify timeout parameter
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 60

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_execute_default_timeout(self, mock_run):
        """Test execute uses default timeout."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        conn._connected = True

        conn.execute("echo test")

        # Verify default timeout
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 30

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_execute_text_mode(self, mock_run):
        """Test execute uses text mode for output."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        conn = SSHConnection(host="localhost", port=22)
        conn._connected = True

        conn.execute("echo test")

        # Verify text=True parameter
        _, kwargs = mock_run.call_args
        assert kwargs["text"] is True


class TestSSHConnectionDisconnect:
    """Test SSHConnection.disconnect method."""

    @pytest.mark.unit
    def test_disconnect(self):
        """Test disconnect sets connected to False."""
        conn = SSHConnection(host="localhost", port=22)

        # Simulate connected state
        conn._connected = True
        assert conn._connected is True

        # Disconnect
        conn.disconnect()

        # Verify disconnected
        assert conn._connected is False

    @pytest.mark.unit
    def test_disconnect_when_already_disconnected(self):
        """Test disconnect when already disconnected."""
        conn = SSHConnection(host="localhost", port=22)

        # Already disconnected
        assert conn._connected is False

        # Disconnect again
        conn.disconnect()

        # Should still be disconnected
        assert conn._connected is False


class TestTestSSHConnectivity:
    """Test test_ssh_connectivity function."""

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_ssh_connectivity_success(self, mock_run):
        """Test successful SSH connectivity check."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = test_ssh_connectivity(host="localhost", port=22)

        assert result is True

        # Verify netcat command
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        nc_cmd = args[0]

        assert nc_cmd == ["nc", "-z", "-w", "5", "localhost", "22"]

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_ssh_connectivity_failure(self, mock_run):
        """Test failed SSH connectivity check."""
        # Mock failed subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = test_ssh_connectivity(host="localhost", port=22)

        assert result is False

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_ssh_connectivity_timeout(self, mock_run):
        """Test SSH connectivity with timeout."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = test_ssh_connectivity(host="localhost", port=22)

        # Verify timeout parameter
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 10

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_ssh_connectivity_file_not_found(self, mock_run):
        """Test SSH connectivity when nc not available."""
        # Mock netcat not found
        mock_run.side_effect = FileNotFoundError("nc not found")

        result = test_ssh_connectivity(host="localhost", port=22)

        # Should return False gracefully
        assert result is False

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_ssh_connectivity_exception(self, mock_run):
        """Test SSH connectivity handles exceptions."""
        # Mock generic exception
        mock_run.side_effect = Exception("Unexpected error")

        result = test_ssh_connectivity(host="localhost", port=22)

        # Should return False gracefully
        assert result is False

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_ssh_connectivity_custom_host_port(self, mock_run):
        """Test SSH connectivity with custom host and port."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = test_ssh_connectivity(host="example.com", port=2222)

        assert result is True

        # Verify custom host and port
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        nc_cmd = args[0]

        assert "example.com" in nc_cmd
        assert "2222" in nc_cmd

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_ssh_connectivity_capture_output(self, mock_run):
        """Test SSH connectivity uses capture_output."""
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = test_ssh_connectivity(host="localhost", port=22)

        # Verify capture_output parameter
        _, kwargs = mock_run.call_args
        assert kwargs["capture_output"] is True
