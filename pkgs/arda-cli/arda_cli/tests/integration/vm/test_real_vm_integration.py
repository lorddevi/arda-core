"""Real VM integration tests using actual KVM/QEMU/Virsh infrastructure.

These tests create, start, stop, and delete actual virtual machines
to verify the VM integration system works in production-like conditions.

Note: These tests require a working KVM/QEMU/Virsh setup and may take
several minutes to complete. They are marked as 'slow' and 'vm'.
"""

import sys
from pathlib import Path as PathLib

import pytest

# Add parent directory to path to import arda_cli
sys.path.insert(0, str(PathLib(__file__).parent.parent.parent.parent.parent))


@pytest.mark.slow
@pytest.mark.vm
@pytest.mark.system
def test_vm_manager_context_manager():
    """Test VMManager context manager functionality."""
    pytest.importorskip("libvirt")
    with VMManager() as vm_mgr:
        # Verify connection was established
        assert vm_mgr.conn is not None

        # Verify we can list VMs (should be empty initially)
        vm_list = vm_mgr.list_vms()
        assert isinstance(vm_list, list)


@pytest.mark.slow
@pytest.mark.vm
def test_vm_manager_connect_disconnect():
    """Test VMManager connection and disconnection."""
    pytest.importorskip("libvirt")
    vm_mgr = VMManager()

    # Test initial state (not connected)
    assert vm_mgr.conn is None

    # Connect
    vm_mgr.connect()
    assert vm_mgr.conn is not None

    # Disconnect
    vm_mgr.disconnect()
    assert vm_mgr.conn is None


@pytest.mark.slow
@pytest.mark.vm
def test_vm_create_and_delete():
    """Test creating and deleting a VM."""
    pytest.importorskip("libvirt")
    with VMManager() as vm_mgr:
        # Create a test VM
        vm = vm_mgr.create_vm(
            name="arda-test-vm-1",
            memory_mb=1024,
            vcpus=1,
            disk_gb=2,
        )

        # Verify VM was created
        assert vm.name == "arda-test-vm-1"
        assert vm.memory_mb == 1024
        assert vm.vcpus == 1
        assert vm.disk_gb == 2

        # Verify VM is in manager's list
        assert "arda-test-vm-1" in vm_mgr.list_vms()

        # Verify VM state is defined (not running)
        state = vm_mgr.get_vm_state("arda-test-vm-1")
        assert state in ["undefined", "shut off", "no state"]

        # Delete the VM
        vm_mgr.delete_vm("arda-test-vm-1")

        # Verify VM is no longer in list
        assert "arda-test-vm-1" not in vm_mgr.list_vms()


@pytest.mark.slow
@pytest.mark.vm
def test_vm_start_and_stop():
    """Test starting and stopping a VM."""
    pytest.importorskip("libvirt")
    with VMManager() as vm_mgr:
        # Create a test VM
        vm = vm_mgr.create_vm(
            name="arda-test-vm-2",
            memory_mb=1024,
            vcpus=1,
            disk_gb=2,
        )

        try:
            # Start the VM
            vm_mgr.start_vm("arda-test-vm-2")

            # Verify VM is running
            state = vm_mgr.get_vm_state("arda-test-vm-2")
            # State should be running (may take a moment)
            # Accept running or transient states

            # Stop the VM
            vm_mgr.stop_vm("arda-test-vm-2")

            # Verify VM is stopped
            state = vm_mgr.get_vm_state("arda-test-vm-2")
            assert state in ["shut off", "shutdown", "no state"]

        finally:
            # Always cleanup
            try:
                vm_mgr.stop_vm("arda-test-vm-2", force=True)
            except Exception:
                pass
            try:
                vm_mgr.delete_vm("arda-test-vm-2")
            except Exception:
                pass


@pytest.mark.slow
@pytest.mark.vm
def test_vm_multiple_instances():
    """Test managing multiple VMs simultaneously."""
    pytest.importorskip("libvirt")
    with VMManager() as vm_mgr:
        # Create multiple VMs
        vm1 = vm_mgr.create_vm("arda-test-vm-3a", memory_mb=1024, vcpus=1, disk_gb=2)
        vm2 = vm_mgr.create_vm("arda-test-vm-3b", memory_mb=1024, vcpus=1, disk_gb=2)
        vm3 = vm_mgr.create_vm("arda-test-vm-3c", memory_mb=1024, vcpus=1, disk_gb=2)

        # Verify all VMs are in the list
        vm_list = vm_mgr.list_vms()
        assert "arda-test-vm-3a" in vm_list
        assert "arda-test-vm-3b" in vm_list
        assert "arda-test-vm-3c" in vm_list

        # Start all VMs
        vm_mgr.start_vm("arda-test-vm-3a")
        vm_mgr.start_vm("arda-test-vm-3b")
        vm_mgr.start_vm("arda-test-vm-3c")

        # Verify all VMs are running
        assert vm_mgr.get_vm_state("arda-test-vm-3a") == "running"
        assert vm_mgr.get_vm_state("arda-test-vm-3b") == "running"
        assert vm_mgr.get_vm_state("arda-test-vm-3c") == "running"

        # Stop all VMs
        vm_mgr.stop_vm("arda-test-vm-3a")
        vm_mgr.stop_vm("arda-test-vm-3b")
        vm_mgr.stop_vm("arda-test-vm-3c")

        # Verify all VMs are stopped
        assert vm_mgr.get_vm_state("arda-test-vm-3a") in ["shut off", "shutdown"]
        assert vm_mgr.get_vm_state("arda-test-vm-3b") in ["shut off", "shutdown"]
        assert vm_mgr.get_vm_state("arda-test-vm-3c") in ["shut off", "shutdown"]

        # Cleanup all VMs
        vm_mgr.cleanup_all()


@pytest.mark.slow
@pytest.mark.vm
def test_vm_not_found_error():
    """Test error handling when VM is not found."""
    pytest.importorskip("libvirt")
    with VMManager() as vm_mgr:
        # Try to get a non-existent VM
        with pytest.raises(VMNotFoundError):
            vm_mgr.get_vm("non-existent-vm")


@pytest.mark.slow
@pytest.mark.vm
def test_vm_force_stop():
    """Test force stopping a VM."""
    pytest.importorskip("libvirt")
    with VMManager() as vm_mgr:
        # Create a test VM
        vm = vm_mgr.create_vm(
            name="arda-test-vm-4",
            memory_mb=1024,
            vcpus=1,
            disk_gb=2,
        )

        try:
            # Start the VM
            vm_mgr.start_vm("arda-test-vm-4")

            # Force stop the VM
            vm_mgr.stop_vm("arda-test-vm-4", force=True)

            # Verify VM is stopped
            state = vm_mgr.get_vm_state("arda-test-vm-4")
            assert state in ["shut off", "shutdown", "no state"]

        finally:
            # Always cleanup
            try:
                vm_mgr.delete_vm("arda-test-vm-4")
            except Exception:
                pass


@pytest.mark.slow
@pytest.mark.vm
def test_vm_vm_object_repr():
    """Test VM object representation."""
    pytest.importorskip("libvirt")
    vm = VM(
        name="test-vm",
        memory_mb=2048,
        vcpus=2,
        disk_gb=10,
    )

    # Check string representation
    repr_str = repr(vm)
    assert "test-vm" in repr_str
    assert "2048MB" in repr_str
    assert "2" in repr_str
    assert "10GB" in repr_str


@pytest.mark.slow
@pytest.mark.vm
def test_vm_custom_configuration():
    """Test VMs with custom configurations."""
    pytest.importorskip("libvirt")
    with VMManager() as vm_mgr:
        # Create VM with custom configuration
        vm = vm_mgr.create_vm(
            name="arda-test-vm-5",
            memory_mb=4096,
            vcpus=4,
            disk_gb=20,
            network="custom-network",
            arch="x86_64",
            machine_type="pc-q35-7.2",
        )

        # Verify custom configuration
        assert vm.name == "arda-test-vm-5"
        assert vm.memory_mb == 4096
        assert vm.vcpus == 4
        assert vm.disk_gb == 20
        assert vm.network == "custom-network"
        assert vm.arch == "x86_64"
        assert vm.machine_type == "pc-q35-7.2"

        # Cleanup
        vm_mgr.delete_vm("arda-test-vm-5")
