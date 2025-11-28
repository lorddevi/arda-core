"""VM Manager for managing multiple virtual machines during testing."""

try:
    import libvirt
except ImportError:
    libvirt = None

import tempfile
from pathlib import Path

from .exceptions import VMError, VMNotFoundError
from .vm import VM


class VMManager:
    """Manages multiple virtual machines for testing.

    Provides high-level API for creating, starting, stopping, and deleting VMs.
    """

    def __init__(self, uri: str = "qemu:///session"):
        """Initialize VM manager.

        Args:
            uri: libvirt connection URI (default: qemu:///session for user session)

        Raises:
            ImportError: If libvirt is not installed
            VMError: If libvirt is not available

        """
        if libvirt is None:
            raise ImportError(
                "libvirt Python module not found. Please install it with:\n"
                "  pip install libvirt-python\n"
                "Or on Debian/Ubuntu:\n"
                "  sudo apt install python3-libvirt"
            )

        self.uri = uri
        self.conn: libvirt.virConnect | None = None
        self.vms: dict[str, VM] = {}
        self._temp_dirs: list[Path] = []

    def connect(self) -> None:
        """Connect to libvirt.

        Raises:
            VMError: If connection fails

        """
        try:
            self.conn = libvirt.open(self.uri)
            if self.conn is None:
                raise VMError(f"Failed to connect to libvirt at {self.uri}")
        except Exception as e:
            raise VMError("Failed to connect to libvirt", e) from e

    def disconnect(self) -> None:
        """Disconnect from libvirt and cleanup."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_vm(
        self,
        name: str,
        memory_mb: int = 2048,
        vcpus: int = 2,
        disk_gb: int = 10,
        network: str = "default",
        arch: str = "x86_64",
        machine_type: str = "pc-q35-7.2",
    ) -> VM:
        """Create a new VM.

        Args:
            name: VM name
            memory_mb: Memory in megabytes
            vcpus: Number of virtual CPUs
            disk_gb: Disk size in gigabytes
            network: Network bridge name
            arch: CPU architecture
            machine_type: QEMU machine type

        Returns:
            Created VM instance

        Raises:
            VMError: If VM creation fails

        """
        if not self.conn:
            self.connect()

        # Create VM configuration
        vm = VM(
            name=name,
            memory_mb=memory_mb,
            vcpus=vcpus,
            disk_gb=disk_gb,
            network=network,
            arch=arch,
            machine_type=machine_type,
        )

        # Create temporary directory for VM data
        temp_dir = Path(tempfile.mkdtemp(prefix=f"vm-{name}-"))
        self._temp_dirs.append(temp_dir)

        # Create VM
        vm.create(self.conn, data_dir=temp_dir)

        # Store VM
        self.vms[name] = vm

        return vm

    def get_vm(self, name: str) -> VM:
        """Get a VM by name.

        Args:
            name: VM name

        Returns:
            VM instance

        Raises:
            VMNotFoundError: If VM doesn't exist

        """
        if name not in self.vms:
            raise VMNotFoundError(name)

        return self.vms[name]

    def start_vm(self, name: str) -> VM:
        """Start a VM.

        Args:
            name: VM name

        Returns:
            Started VM instance

        Raises:
            VMError: If VM start fails

        """
        vm = self.get_vm(name)
        vm.start()
        return vm

    def stop_vm(self, name: str, force: bool = False) -> VM:
        """Stop a VM.

        Args:
            name: VM name
            force: If True, force stop (kill). If False, graceful shutdown.

        Returns:
            Stopped VM instance

        Raises:
            VMError: If VM stop fails

        """
        vm = self.get_vm(name)
        vm.stop(force=force)
        return vm

    def delete_vm(self, name: str, remove_disks: bool = True) -> None:
        """Delete a VM.

        Args:
            name: VM name
            remove_disks: If True, also remove VM disk images

        Raises:
            VMError: If VM deletion fails

        """
        if name not in self.vms:
            return

        vm = self.vms[name]
        vm.delete(remove_disks=remove_disks)
        del self.vms[name]

    def list_vms(self) -> list[str]:
        """List all managed VM names.

        Returns:
            List of VM names

        """
        return list(self.vms.keys())

    def get_vm_state(self, name: str) -> str:
        """Get VM state.

        Args:
            name: VM name

        Returns:
            VM state string

        Raises:
            VMNotFoundError: If VM doesn't exist

        """
        vm = self.get_vm(name)
        return vm.get_state()

    def cleanup_all(self, remove_disks: bool = True) -> None:
        """Stop and delete all managed VMs.

        Args:
            remove_disks: If True, also remove VM disk images

        """
        # Get list of VMs to avoid modification during iteration
        vm_names = list(self.vms.keys())

        for name in vm_names:
            try:
                self.delete_vm(name, remove_disks=remove_disks)
            except Exception as e:
                # Log error but continue cleanup
                print(f"Warning: Failed to delete VM {name}: {e}")

        # Cleanup temp directories
        for temp_dir in self._temp_dirs:
            try:
                if temp_dir.exists():
                    # Note: shutil.rmtree would be better, but keeping it simple
                    import shutil

                    shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Failed to cleanup temp dir {temp_dir}: {e}")

        self._temp_dirs.clear()

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup_all()
        self.disconnect()
