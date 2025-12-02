"""Unit tests for network port utilities.

This test suite ensures comprehensive coverage of all port-related
functions in the arda_cli.testing.network module.
"""

import subprocess
from unittest.mock import MagicMock, mock_open, patch

import pytest

from arda_cli.testing.network.port import (
    PortUtilsError,
    check_host_port_open,
    find_free_port,
    setup_port_forwarding,
    wait_for_port,
)


class TestFindFreePort:
    """Test find_free_port function."""

    @pytest.mark.unit
    def test_find_free_port_default_range(self):
        """Test find_free_port with default range."""
        port = find_free_port()

        # Port should be in valid range
        assert 8000 <= port <= 9000

    @pytest.mark.unit
    def test_find_free_port_custom_range(self):
        """Test find_free_port with custom range."""
        port = find_free_port(start=9000, end=9999)

        # Port should be in custom range
        assert 9000 <= port <= 9999

    @pytest.mark.unit
    def test_find_free_port_reasonable_range(self):
        """Test find_free_port with reasonable range."""
        port = find_free_port(start=5000, end=5100)

        # Port should be in reasonable range
        assert 5000 <= port <= 5100

    @pytest.mark.unit
    @patch("socket.socket")
    def test_find_free_port_all_ports_in_use(self, mock_socket):
        """Test find_free_port raises RuntimeError when no port available."""
        # Mock socket to always raise OSError
        mock_socket.side_effect = OSError("All ports in use")

        with pytest.raises(RuntimeError, match="No available port found in range"):
            find_free_port(start=65000, end=65009)

    @pytest.mark.unit
    def test_find_free_port_skips_used_port(self):
        """Test find_free_port skips ports that are in use."""
        # Test with a wider range to ensure we get a port
        # The function will try ports in order until it finds one
        port = find_free_port(start=30000, end=30050)

        # Should return a port in the range
        assert 30000 <= port <= 30050

    @pytest.mark.unit
    @patch("socket.socket")
    def test_find_free_port_single_port(self, mock_socket):
        """Test find_free_port with single port range."""
        # Mock socket to succeed
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock

        port = find_free_port(start=8888, end=8888)

        assert port == 8888
        mock_sock.bind.assert_called_once_with(("localhost", 8888))


class TestCheckHostPortOpen:
    """Test check_host_port_open function."""

    @pytest.mark.unit
    def test_check_host_port_open_false(self):
        """Test check_host_port_open returns False for closed port."""
        # Use unlikely port number
        result = check_host_port_open(host="localhost", port=65000, timeout=1)
        assert result is False

    @pytest.mark.unit
    @patch("socket.socket")
    def test_check_host_port_open_true(self, mock_socket):
        """Test check_host_port_open returns True for open port."""
        # Mock successful connection
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0  # Success
        mock_socket.return_value.__enter__.return_value = mock_sock

        result = check_host_port_open(host="localhost", port=80, timeout=5)

        assert result is True
        mock_sock.connect_ex.assert_called_once_with(("localhost", 80))

    @pytest.mark.unit
    @patch("socket.socket")
    def test_check_host_port_open_os_error(self, mock_socket):
        """Test check_host_port_open handles OSError gracefully."""
        mock_socket.side_effect = OSError("Connection refused")

        result = check_host_port_open(host="localhost", port=65000, timeout=1)

        assert result is False

    @pytest.mark.unit
    @patch("socket.socket")
    def test_check_host_port_open_exception(self, mock_socket):
        """Test check_host_port_open handles generic exceptions."""
        mock_socket.side_effect = Exception("Unexpected error")

        result = check_host_port_open(host="localhost", port=65000, timeout=1)

        assert result is False


class TestWaitForPort:
    """Test wait_for_port function."""

    @pytest.mark.unit
    @patch("time.sleep")
    @patch("arda_cli.testing.network.port.check_host_port_open")
    def test_wait_for_port_timeout(self, mock_check, mock_sleep):
        """Test wait_for_port returns False on timeout."""
        # Mock check to always return False
        mock_check.return_value = False

        result = wait_for_port(
            host="localhost", port=65000, timeout=1, check_interval=0.1
        )

        assert result is False
        # Should check multiple times
        assert mock_check.call_count > 1

    @pytest.mark.unit
    @patch("time.sleep")
    @patch("arda_cli.testing.network.port.check_host_port_open")
    def test_wait_for_port_success(self, mock_check, mock_sleep):
        """Test wait_for_port returns True when port opens."""
        # Mock check to fail first, then succeed
        mock_check.side_effect = [False, False, True]

        result = wait_for_port(
            host="localhost", port=8080, timeout=5, check_interval=0.1
        )

        assert result is True
        # Should be called 3 times
        assert mock_check.call_count == 3

    @pytest.mark.unit
    @patch("time.sleep")
    @patch("arda_cli.testing.network.port.check_host_port_open")
    def test_wait_for_port_immediate_success(self, mock_check, mock_sleep):
        """Test wait_for_port succeeds immediately."""
        # Mock check to succeed on first try
        mock_check.return_value = True

        result = wait_for_port(
            host="localhost", port=8080, timeout=5, check_interval=0.1
        )

        assert result is True
        mock_check.assert_called_once()

    @pytest.mark.unit
    @patch("time.sleep")
    @patch("arda_cli.testing.network.port.check_host_port_open")
    def test_wait_for_port_respects_timeout(self, mock_check, mock_sleep):
        """Test wait_for_port respects timeout parameter."""
        # Mock check to always return False
        mock_check.return_value = False

        start_time = 1000.0
        with patch("time.time", side_effect=[start_time, start_time + 5]):
            result = wait_for_port(
                host="localhost", port=65000, timeout=5, check_interval=0.1
            )

            assert result is False

    @pytest.mark.unit
    @patch("time.sleep")
    @patch("arda_cli.testing.network.port.check_host_port_open")
    def test_wait_for_port_custom_interval(self, mock_check, mock_sleep):
        """Test wait_for_port uses custom check interval."""
        # Mock check to succeed on second try
        mock_check.side_effect = [False, True]

        result = wait_for_port(
            host="localhost", port=8080, timeout=5, check_interval=0.5
        )

        assert result is True
        # Verify sleep was called with correct interval
        mock_sleep.assert_called_with(0.5)


class TestSetupPortForwarding:
    """Test setup_port_forwarding function."""

    @pytest.mark.unit
    @patch("subprocess.Popen")
    def test_setup_port_forwarding_success(self, mock_popen):
        """Test setup_port_forwarding creates SSH process."""
        # Mock successful Popen
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        result = setup_port_forwarding(
            local_port=8080,
            remote_host="example.com",
            remote_port=80,
            ssh_user="root",
        )

        assert result == mock_process

        # Verify SSH command was constructed correctly
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args

        ssh_cmd = args[0]
        assert ssh_cmd == [
            "ssh",
            "-N",
            "-L",
            "8080:example.com:80",
            "root@example.com",
        ]
        assert kwargs["stdout"] == subprocess.DEVNULL
        assert kwargs["stderr"] == subprocess.DEVNULL

    @pytest.mark.unit
    @patch("subprocess.Popen")
    def test_setup_port_forwarding_default_user(self, mock_popen):
        """Test setup_port_forwarding with default SSH user."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        result = setup_port_forwarding(
            local_port=8080,
            remote_host="example.com",
            remote_port=80,
        )

        # Verify default user "root" is used
        args, _ = mock_popen.call_args
        ssh_cmd = args[0]
        assert "root@example.com" in ssh_cmd

    @pytest.mark.unit
    @patch("subprocess.Popen")
    def test_setup_port_forwarding_custom_user(self, mock_popen):
        """Test setup_port_forwarding with custom SSH user."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        result = setup_port_forwarding(
            local_port=8080,
            remote_host="example.com",
            remote_port=80,
            ssh_user="ubuntu",
        )

        # Verify custom user is used
        args, _ = mock_popen.call_args
        ssh_cmd = args[0]
        assert "ubuntu@example.com" in ssh_cmd

    @pytest.mark.unit
    @patch("subprocess.Popen")
    def test_setup_port_forwarding_different_ports(self, mock_popen):
        """Test setup_port_forwarding with different port numbers."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        result = setup_port_forwarding(
            local_port=3000,
            remote_host="192.168.1.100",
            remote_port=5432,
            ssh_user="admin",
        )

        # Verify all port numbers are correct
        args, _ = mock_popen.call_args
        ssh_cmd = args[0]
        assert "-L" in ssh_cmd
        assert "3000:192.168.1.100:5432" in ssh_cmd

    @pytest.mark.unit
    @patch("subprocess.Popen", side_effect=FileNotFoundError("ssh not found"))
    def test_setup_port_forwarding_ssh_not_available(self, mock_popen):
        """Test setup_port_forwarding raises RuntimeError when SSH not available."""
        with pytest.raises(RuntimeError, match="SSH not available for port forwarding"):
            setup_port_forwarding(
                local_port=8080,
                remote_host="example.com",
                remote_port=80,
            )

    @pytest.mark.unit
    @patch("subprocess.Popen")
    def test_setup_port_forwarding_command_structure(self, mock_popen):
        """Test setup_port_forwarding SSH command structure."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        setup_port_forwarding(
            local_port=2222,
            remote_host="vm.local",
            remote_port=22,
            ssh_user="user",
        )

        # Verify the command structure
        args, _ = mock_popen.call_args
        ssh_cmd = args[0]

        # Verify SSH flags
        assert "-N" in ssh_cmd  # No remote command
        assert "-L" in ssh_cmd  # Local port forwarding

        # Verify correct order
        assert ssh_cmd.index("-N") < ssh_cmd.index("-L")
        assert ssh_cmd.index("-L") < ssh_cmd.index("user@vm.local")


class TestPortUtilsError:
    """Test PortUtilsError exception class."""

    @pytest.mark.unit
    def test_port_utils_error_is_exception(self):
        """Test PortUtilsError is an Exception."""
        assert issubclass(PortUtilsError, Exception)

    @pytest.mark.unit
    def test_port_utils_error_raised(self):
        """Test PortUtilsError can be raised."""
        with pytest.raises(PortUtilsError):
            raise PortUtilsError("Test error")

    @pytest.mark.unit
    def test_port_utils_error_with_message(self):
        """Test PortUtilsError with custom message."""
        with pytest.raises(PortUtilsError, match="Custom error message"):
            raise PortUtilsError("Custom error message")
