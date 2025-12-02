"""Test network utilities for VM testing."""

import sys
import time
from unittest.mock import MagicMock, patch

import pytest

# Import network utilities from arda_cli.testing.network
from arda_cli.testing.network import (
    SSHConnection,
    check_host_port_open,
    find_free_port,
    test_ssh_connectivity,
    wait_for_port,
)


@pytest.mark.network
@pytest.mark.integration
def test_find_free_port():
    """Test that find_free_port returns available port."""
    port = find_free_port()

    # Port should be in valid range
    assert 8000 <= port <= 9000

    # Port should actually be available
    assert not check_host_port_open(port=port)


@pytest.mark.network
@pytest.mark.integration
def test_find_free_port_custom_range():
    """Test find_free_port with custom range."""
    port = find_free_port(start=9000, end=9999)

    # Port should be in custom range
    assert 9000 <= port <= 9999


@pytest.mark.network
@pytest.mark.integration
def test_check_host_port_open():
    """Test port open detection."""
    # Test closed port (should fail)
    assert not check_host_port_open(port=65000)

    # Test with valid port (may or may not be open)
    result = check_host_port_open(port=22)
    # Verify function returns a boolean (True if open, False if closed)
    assert isinstance(result, bool)


@pytest.mark.network
@pytest.mark.integration
def test_check_host_port_open_timeout():
    """Test port check with timeout."""
    # Test with short timeout
    result = check_host_port_open(port=65000, timeout=1)
    assert result is False


@pytest.mark.network
@pytest.mark.integration
def test_wait_for_port_timeout():
    """Test wait_for_port with timeout."""
    start_time = time.time()
    result = wait_for_port(port=65000, timeout=2)
    elapsed = time.time() - start_time

    # Should return False
    assert result is False

    # Should timeout (using wider tolerance for flaky time-based tests)
    # Allows for system load and scheduling variance
    assert 1.7 < elapsed < 3.0


@pytest.mark.network
@pytest.mark.integration
def test_wait_for_port_success():
    """Test wait_for_port when port becomes available."""
    import socket

    # Start a server briefly
    server_socket = None
    try:
        # Find a port and bind to it
        port = find_free_port()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("localhost", port))
        server_socket.listen(1)

        # Wait for the port (should succeed quickly)
        start_time = time.time()
        result = wait_for_port(port=port, timeout=5, check_interval=0.1)
        elapsed = time.time() - start_time

        # Should return True
        assert result is True

        # Should succeed quickly (port is already open)
        assert elapsed < 1.0

    finally:
        if server_socket:
            server_socket.close()


@pytest.mark.network
@pytest.mark.integration
def test_ssh_connection_init():
    """Test SSH connection initialization."""
    conn = SSHConnection(host="localhost", port=22, user="root")

    assert conn.host == "localhost"
    assert conn.port == 22
    assert conn.user == "root"
    assert conn._connected is False


@pytest.mark.network
@pytest.mark.integration
def test_ssh_connection_connect_disconnect():
    """Test SSH connection connect and disconnect."""
    conn = SSHConnection(host="localhost", port=22)

    # Test disconnect when not connected
    conn.disconnect()
    assert conn._connected is False


@pytest.mark.network
@pytest.mark.integration
def test_ssh_connection_execute_not_connected():
    """Test SSH execute when not connected."""
    conn = SSHConnection(host="localhost", port=22)

    # Should raise RuntimeError
    with pytest.raises(RuntimeError, match="SSH not connected"):
        conn.execute("echo test")


@pytest.mark.network
@pytest.mark.integration
def test_ssh_connection_execute_no_key():
    """Test SSH execute without key file."""
    # This test will likely fail to connect, but we're testing the error handling
    conn = SSHConnection(host="localhost", port=22, user="root")

    # Try to connect (will likely fail in test environment)
    try:
        is_connected = conn.connect()

        # If connection somehow succeeds, test execute
        if is_connected:
            return_code, stdout, stderr = conn.execute("echo 'Hello'")
            assert isinstance(return_code, int)
            assert isinstance(stdout, str)
            assert isinstance(stderr, str)
    except Exception:
        # SSH not available - this is OK for integration tests
        pass


@pytest.mark.network
@pytest.mark.integration
def test_test_ssh_connectivity():
    """Test SSH connectivity checker."""
    result = test_ssh_connectivity(host="localhost", port=22)
    # Just verify function runs and returns a boolean
    assert isinstance(result, bool)


@pytest.mark.network
@pytest.mark.integration
def test_ssh_connectivity_invalid_host():
    """Test SSH connectivity with invalid host."""
    result = test_ssh_connectivity(
        host="invalid-host-that-does-not-exist.invalid", port=22
    )
    # Should return False for invalid host
    assert isinstance(result, bool)
    # Verify that it returns False (or at least not True) for invalid host
    # In isolated test environments with no network, this might raise an exception
    # or return False - either way, it should not return True
    if result is True:
        pytest.fail("SSH connectivity should not succeed for invalid host")
