"""Individual VM instance management."""

import time
import xml.etree.ElementTree as ET
from pathlib import Path

from .exceptions import (
    VMDeleteError,
    VMStartError,
    VMStopError,
    VMTimeoutError,
)


class VM:
    """Represents a single virtual machine instance.

    Provides methods to manage VM lifecycle: start, stop, delete, run commands.
    """

    def __init__(
        self,
        name: str,
        memory_mb: int,
        vcpus: int,
        disk_gb: int,
        network: str = "default",
        arch: str = "x86_64",
        machine_type: str = "pc-q35-7.2",
    ):
        """Initialize VM configuration.

        Args:
            name: VM name
            memory_mb: Memory in megabytes
            vcpus: Number of virtual CPUs
            disk_gb: Disk size in gigabytes
            network: Network bridge name
            arch: CPU architecture
            machine_type: QEMU machine type

        """
        self.name = name
        self.memory_mb = memory_mb
        self.vcpus = vcpus
        self.disk_gb = disk_gb
        self.network = network
        self.arch = arch
        self.machine_type = machine_type

        self._state: str | None = None
        self._virsh_name = "qemu:///system"

    def create(self, libvirt_conn, data_dir: Path | None = None) -> None:
        """Create the VM definition in libvirt.

        Args:
            libvirt_conn: libvirt connection object
            data_dir: Directory for VM data (disk images, etc.)

        Raises:
            VMCreateError: If VM creation fails

        """
        try:
            # Generate domain XML
            domain_xml = self._generate_domain_xml(data_dir)

            # Define domain in libvirt
            domain = libvirt_conn.defineXML(domain_xml)
            if domain is None:
                raise VMCreateError(self.name)

            # Store domain reference
            self._domain = domain

        except Exception as e:
            raise VMCreateError(self.name, e) from e

    def start(self) -> None:
        """Start the VM.

        Raises:
            VMStartError: If VM start fails

        """
        try:
            if not hasattr(self, "_domain"):
                raise VMStartError(self.name, None)

            # Start the domain
            result = self._domain.create()

            # Wait a bit for VM to initialize
            time.sleep(2)

            # Check state
            self._state = self._domain.state(0)[0]

        except Exception as e:
            raise VMStartError(self.name, e) from e

    def stop(self, force: bool = False) -> None:
        """Stop the VM.

        Args:
            force: If True, force stop (kill). If False, graceful shutdown.

        Raises:
            VMStopError: If VM stop fails

        """
        try:
            if not hasattr(self, "_domain"):
                raise VMStopError(self.name, None)

            if force:
                # Force stop - destroy
                self._domain.destroy()
            else:
                # Graceful shutdown
                self._domain.shutdown()

            # Wait for stop
            time.sleep(2)

            # Check state
            self._state = self._domain.state(0)[0]

        except Exception as e:
            raise VMStopError(self.name, e) from e

    def delete(self, remove_disks: bool = True) -> None:
        """Delete the VM and optionally its disks.

        Args:
            remove_disks: If True, also remove VM disk images

        Raises:
            VMDeleteError: If VM deletion fails

        """
        try:
            if hasattr(self, "_domain"):
                # Undefine domain
                # VIR_DOMAIN_UNDEFINE_MANAGED_SAVE = 1
                # VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA = 2
                # VIR_DOMAIN_UNDEFINE_NVRAM = 4
                flags = 1 | 2 | 4  # Remove all metadata
                self._domain.undefineFlags(flags)

                delattr(self, "_domain")

        except Exception as e:
            raise VMDeleteError(self.name, e) from e

    def wait_for_ssh(self, timeout: int = 60, username: str = "root") -> bool:
        """Wait for SSH to become available on the VM.

        Args:
            timeout: Maximum time to wait in seconds
            username: Username for SSH connection

        Returns:
            True if SSH is available, False if timeout

        Raises:
            VMTimeoutError: If timeout is reached

        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try to connect to SSH port (22)
                # In a real implementation, we'd need to get the IP address
                # For now, just simulate the check
                time.sleep(2)
                return True
            except Exception:
                pass

        raise VMTimeoutError("SSH availability", timeout)

    def run_command(self, command: str, timeout: int = 30) -> tuple[int, str, str]:
        """Run a command inside the VM via SSH.

        Args:
            command: Command to execute
            timeout: Command timeout in seconds

        Returns:
            Tuple of (exit_code, stdout, stderr)

        Note:
            This is a placeholder - real implementation would use SSH

        """
        # Placeholder - would implement SSH command execution
        # For now, just return success
        return (0, f"Executed: {command}\n", "")

    def get_state(self) -> str:
        """Get current VM state.

        Returns:
            VM state as string (e.g., 'running', 'stopped', 'paused')

        """
        if hasattr(self, "_domain"):
            state = self._domain.state(0)[0]
            state_map = {
                0: "no state",
                1: "running",
                2: "blocked",
                3: "paused",
                4: "shutdown",
                5: "shut off",
                6: "crashed",
                7: "pmsuspended",
            }
            return state_map.get(state, f"unknown ({state})")
        return "undefined"

    def get_ip_address(self) -> str | None:
        """Get IP address of the VM.

        Returns:
            IP address string or None if not available

        """
        # Placeholder - would query libvirt for IP
        # This requires DHCP lease or network monitoring
        return None

    def _generate_domain_xml(self, data_dir: Path | None = None) -> str:
        """Generate libvirt domain XML for this VM.

        Args:
            data_dir: Directory for VM data

        Returns:
            XML string defining the domain

        """
        # Create XML structure
        domain = ET.Element("domain", type="kvm")
        domain.set("type", "kvm")

        # Name
        name = ET.SubElement(domain, "name")
        name.text = self.name

        # Memory
        memory = ET.SubElement(domain, "memory", unit="MiB")
        memory.text = str(self.memory_mb)

        # VCPUs
        vcpu = ET.SubElement(domain, "vcpu", placement="static")
        vcpu.text = str(self.vcpus)

        # OS
        os_elem = ET.SubElement(domain, "os")
        os_type = ET.SubElement(
            os_elem, "type", arch=self.arch, machine=self.machine_type
        )
        os_type.text = "hvm"

        # Features
        features = ET.SubElement(domain, "features")
        acpi = ET.SubElement(features, "acpi")
        apic = ET.SubElement(features, "apic")
        pae = ET.SubElement(features, "pae")

        # CPU
        cpu = ET.SubElement(domain, "cpu", mode="host-model")
        cpu_model = ET.SubElement(cpu, "model", fallback="allow")

        # Clock
        clock = ET.SubElement(domain, "clock", offset="utc")
        timer = ET.SubElement(clock, "timer", name="rtc", tickpolicy="catchup")

        # Devices
        devices = ET.SubElement(domain, "devices")

        # Disk
        disk = ET.SubElement(devices, "disk", type="file", device="disk")
        driver = ET.SubElement(disk, "driver", name="qemu", type="qcow2")
        source = ET.SubElement(
            disk,
            "source",
            file=str(data_dir / f"{self.name}.qcow2") if data_dir else "",
        )
        target = ET.SubElement(disk, "target", dev="vda", bus="virtio")

        # Interface
        interface = ET.SubElement(devices, "interface", type="bridge")
        source = ET.SubElement(interface, "source", bridge=self.network)
        model = ET.SubElement(interface, "model", type="virtio")

        # Graphics
        graphics = ET.SubElement(devices, "graphics", type="spice", autoport="yes")

        # Serial console
        console = ET.SubElement(devices, "console", type="pty")
        target = ET.SubElement(console, "target", type="serial", port="0")

        return ET.tostring(domain, encoding="unicode", method="xml")

    def __repr__(self) -> str:
        return (
            f"VM(name={self.name!r}, memory={self.memory_mb}MB, "
            f"vcpus={self.vcpus}, disk={self.disk_gb}GB, "
            f"state={self.get_state()!r})"
        )
