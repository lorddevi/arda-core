# Architecture - Clan VM Manager

## Executive Summary

The **Clan VM Manager** is a **specialized CLI tool** for virtual machine lifecycle management in the Clan ecosystem. Built with **Python 3.13**, it provides commands for creating, starting, stopping, and managing virtual machines that integrate seamlessly with Clan infrastructure.

## Technology Stack

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| **Language** | Python | 3.13 | Modern Python with type hints |
| **CLI Framework** | argparse | Built-in | Standard library, lightweight |
| **Build System** | setuptools | Latest | Python packaging |
| **Testing** | pytest | Latest | Testing framework |
| **Type Checking** | mypy | Latest | Static type analysis |
| **VM Backend** | QEMU/KVM | Latest | Full virtualization |
| **Configuration** | YAML | Latest | Human-readable configs |

## Architecture Pattern

**VM Lifecycle Management with Command-Based Interface**

```
┌─────────────────────────────────────────┐
│         CLI Interface Layer             │
│  ┌───────────────────────────────────┐  │
│  │  argparse Command Parser          │  │
│  │  Argument Validation              │  │
│  │  Help & Usage                     │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│       VM Operation Layer                │
│  ┌───────────────────────────────────┐  │
│  │  VM Lifecycle Manager             │  │
│  │  State Tracking                   │  │
│  │  Error Handling                   │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│       VM Backend Layer                  │
│  ┌───────────────────────────────────┐  │
│  │  QEMU/KVM Interface               │  │
│  │  Disk Management                  │  │
│  │  Network Configuration            │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│       Integration Layer                 │
│  ┌───────────────────────────────────┐  │
│  │  Clan Infrastructure Integration  │  │
│  │  Inventory System                 │  │
│  │  Configuration Management         │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Data Architecture

### VM Manager Structure

```
pkgs/clan-vm-manager/
├── clan_vm_manager/              # VM Manager implementation
│   ├── __main__.py              # Entry point
│   ├── cli.py                   # CLI interface
│   ├── vm_ops.py                # VM operations
│   ├── config.py                # Configuration handling
│   ├── history.py               # VM history tracking
│   ├── disk_manager.py          # Disk management
│   ├── network.py               # Network configuration
│   └── templates/               # VM templates
│
├── tests/                       # Test suite
│   ├── test_vm_ops.py           # VM operations tests
│   ├── test_config.py           # Configuration tests
│   └── test_cli.py              # CLI tests
│
├── pyproject.toml               # Python metadata
├── default.nix                  # Nix package
└── flake-module.nix             # Flake integration
```

### VM Configuration Schema

```python
@dataclass
class VMConfig:
    name: str
    cpus: int = 2
    memory: int = 2048  # MB
    disk_size: int = 20480  # MB
    disk_path: Optional[str] = None
    network: NetworkConfig = field(default_factory=NetworkConfig)
    kernel: Optional[str] = None
    initrd: Optional[str] = None
    append: Optional[str] = None
    qemu_args: List[str] = field(default_factory=list)

@dataclass
class NetworkConfig:
    mode: str = "default"  # default, bridge, nat
    bridge: Optional[str] = None
    mac: Optional[str] = None
```

### VM State Tracking

```python
@dataclass
class VMState:
    name: str
    state: VMStateEnum  # RUNNING, STOPPED, PAUSED
    pid: Optional[int] = None
    created_at: datetime
    last_started: Optional[datetime] = None
    last_stopped: Optional[datetime] = None
    history: List[VMEvent] = field(default_factory=list)

@dataclass
class VMEvent:
    timestamp: datetime
    action: str  # create, start, stop, delete
    user: str
    details: str
```

## API Design

### VM Operations API

```python
class VMManager:
    """Main VM Manager interface"""

    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.state_file = Path.home() / '.clan-vm' / 'vm-state.json'

    def create_vm(self, config: VMConfig) -> VM:
        """Create a new VM"""
        ...

    def start_vm(self, name: str) -> bool:
        """Start VM"""
        ...

    def stop_vm(self, name: str, force: bool = False) -> bool:
        """Stop VM"""
        ...

    def delete_vm(self, name: str) -> bool:
        """Delete VM"""
        ...

    def list_vms(self) -> List[VM]:
        """List all VMs"""
        ...

    def get_vm(self, name: str) -> VM:
        """Get VM by name"""
        ...

    def vm_status(self, name: str) -> VMStatus:
        """Get VM status"""
        ...
```

### Command Handlers

```python
def create_command(args):
    """Handle vm create command"""
    config = VMConfig(
        name=args.name,
        cpus=args.cpus,
        memory=args.memory,
        disk_size=args.disk_size,
    )

    vm_manager = VMManager(args.config)
    vm = vm_manager.create_vm(config)

    click.echo(f"VM '{vm.name}' created successfully")

def start_command(args):
    """Handle vm start command"""
    vm_manager = VMManager(args.config)
    if vm_manager.start_vm(args.name):
        click.echo(f"VM '{args.name}' started")
    else:
        click.echo(f"Failed to start VM '{args.name}'", err=True)
        sys.exit(1)
```

## Component Overview

### 1. VM Lifecycle Manager (vm_ops.py)

**Technology:** QEMU/KVM integration
**Purpose:** VM creation, management, and lifecycle

**Operations:**

```python
class VMLifecycleManager:
    def create_vm(self, config: VMConfig) -> VM:
        """Create VM from configuration"""
        # Create disk image
        disk_path = self.disk_manager.create_disk(
            config.name,
            config.disk_size
        )

        # Generate network config
        network_config = self.network.configure(config.network)

        # Write VM definition
        vm_def = self._generate_vm_definition(config, disk_path, network_config)

        # Create VM state
        vm_state = VMState(
            name=config.name,
            state=VMStateEnum.STOPPED,
            created_at=datetime.now()
        )

        return VM(config=vm_def, state=vm_state)

    def start_vm(self, name: str) -> bool:
        """Start VM with QEMU"""
        vm = self.get_vm(name)

        # Generate QEMU command
        cmd = self._build_qemu_command(vm)

        # Launch QEMU process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Update state
        vm.state.pid = process.pid
        vm.state.state = VMStateEnum.RUNNING
        vm.state.last_started = datetime.now()

        self._save_state()
        return True

    def stop_vm(self, name: str, force: bool = False) -> bool:
        """Stop VM"""
        vm = self.get_vm(name)

        if vm.state.pid:
            if force:
                os.kill(vm.state.pid, signal.SIGKILL)
            else:
                os.kill(vm.state.pid, signal.SIGTERM)

        vm.state.state = VMStateEnum.STOPPED
        vm.state.last_stopped = datetime.now()

        self._save_state()
        return True
```

### 2. Disk Management (disk_manager.py)

**Technology:** QEMU disk images (qcow2)
**Purpose:** Create, manage, and resize VM disks

**Features:**

```python
class DiskManager:
    def create_disk(self, name: str, size: int) -> Path:
        """Create qcow2 disk image"""
        disk_path = self.vm_dir / f'{name}.qcow2'

        cmd = [
            'qemu-img', 'create',
            '-f', 'qcow2',
            '-o', f'preallocation=metadata',
            str(disk_path),
            f'{size}M'
        ]

        subprocess.run(cmd, check=True)
        return disk_path

    def resize_disk(self, name: str, new_size: int) -> bool:
        """Resize disk"""
        disk_path = self.vm_dir / f'{name}.qcow2'

        cmd = [
            'qemu-img', 'resize',
            str(disk_path),
            f'{new_size}M'
        ]

        subprocess.run(cmd, check=True)
        return True

    def snapshot_disk(self, name: str, snapshot_name: str) -> bool:
        """Create disk snapshot"""
        disk_path = self.vm_dir / f'{name}.qcow2'

        cmd = [
            'qemu-img', 'snapshot',
            '-c', snapshot_name,
            str(disk_path)
        ]

        subprocess.run(cmd, check=True)
        return True
```

### 3. Network Configuration (network.py)

**Technology:** Linux network bridges + QEMU networking
**Purpose:** Configure VM networking

**Network Modes:**

```python
class NetworkManager:
    def configure(self, config: NetworkConfig) -> NetworkConfig:
        """Configure network based on mode"""

        if config.mode == 'bridge':
            return self._configure_bridge(config)
        elif config.mode == 'nat':
            return self._configure_nat(config)
        else:
            return self._configure_default(config)

    def _configure_bridge(self, config: NetworkConfig) -> NetworkConfig:
        """Configure bridge networking"""
        bridge_name = config.bridge or 'clan-br0'

        # Create bridge if not exists
        self._ensure_bridge(bridge_name)

        return config._replace(bridge=bridge_name)

    def _build_netdev_args(self, network_config: NetworkConfig) -> List[str]:
        """Build QEMU netdev arguments"""
        if network_config.mode == 'bridge':
            return [
                '-netdev', f'bridge,id=net0,br={network_config.bridge}',
                '-device', f'virtio-net,netdev=net0,mac={network_config.mac}'
            ]
        else:
            return [
                '-netdev', f'user,id=net0',
                '-device', f'virtio-net,netdev=net0,mac={network_config.mac}'
            ]
```

### 4. History Tracking (history.py)

**Technology:** Event sourcing
**Purpose:** Track all VM operations

**Features:**

```python
class VMHistory:
    def __init__(self, history_file: Path):
        self.history_file = history_file

    def log_event(self, vm_name: str, action: str, user: str, details: str):
        """Log VM event"""
        event = VMEvent(
            timestamp=datetime.now(),
            action=action,
            user=user,
            details=details
        )

        # Load existing history
        history = self._load_history(vm_name)
        history.append(event)

        # Save updated history
        self._save_history(vm_name, history)

    def get_history(self, vm_name: str) -> List[VMEvent]:
        """Get VM history"""
        return self._load_history(vm_name)

    def get_recent_events(self, limit: int = 10) -> List[VMEvent]:
        """Get recent events across all VMs"""
        all_events = []

        for vm_name in self.list_tracked_vms():
            all_events.extend(self.get_history(vm_name))

        # Sort by timestamp, most recent first
        return sorted(all_events, key=lambda e: e.timestamp, reverse=True)[:limit]
```

## Command Structure

### CLI Command Tree

```
clan-vm-manager
├── create <name>              # Create new VM
│   --cpus <n>                 # Number of CPUs
│   --memory <MB>              # Memory in MB
│   --disk <MB>                # Disk size in MB
│   --network <mode>           # Network mode
│   --bridge <name>            # Bridge name
│   --kernel <path>            # Kernel path
│   --initrd <path>            # Initrd path
│   --append <params>          # Kernel parameters
│
├── start <name>               # Start VM
│   --foreground               # Run in foreground
│
├── stop <name>                # Stop VM
│   --force                    # Force stop
│
├── restart <name>             # Restart VM
│
├── delete <name>              # Delete VM
│   --force                    # Force delete (remove disk)
│
├── list                       # List all VMs
│   --filter <state>           # Filter by state
│
├── show <name>                # Show VM details
│
├── status <name>              # Show VM status
│
├── snapshot <name> <snap>     # Create snapshot
│
├── revert <name> <snap>       # Revert to snapshot
│
├── console <name>             # Connect to console
│
└── history                    # Show VM history
    --vm <name>                # History for specific VM
    --limit <n>                # Limit number of events
```

## Development Workflow

### Prerequisites

- Python 3.13+
- QEMU/KVM
- libvirt (optional)
- Nix (for building)

### Development Commands

```bash
# Install in development mode
pip install -e .

# Run CLI
clan-vm-manager --help

# Run tests
pytest

# Type checking
mypy clan_vm_manager/
```

### Build Process

```bash
# Python package
python -m build

# Nix package
nix build .#clan-vm-manager
```

### Testing Strategy

**Unit Tests:**

```python
def test_create_vm():
    """Test VM creation"""
    config = VMConfig(name='test-vm', cpus=2, memory=2048)
    vm = vm_manager.create_vm(config)

    assert vm.config.name == 'test-vm'
    assert vm.config.cpus == 2
    assert vm.state.state == VMStateEnum.STOPPED

def test_start_stop_vm():
    """Test VM start/stop"""
    vm = create_test_vm()
    assert vm.state.state == VMStateEnum.STOPPED

    vm_manager.start_vm(vm.config.name)
    assert vm.state.state == VMStateEnum.RUNNING

    vm_manager.stop_vm(vm.config.name)
    assert vm.state.state == VMStateEnum.STOPPED
```

## Integration with Clan System

### With Infrastructure

```python
# Integration with clanCore VM module
async def deploy_vm_machine(vm_name: str, vm_config: VMConfig):
    # Create VM
    vm_manager.create_vm(vm_config)
    vm_manager.start_vm(vm_name)

    # Wait for VM to boot
    await asyncio.sleep(10)

    # Deploy Clan configuration
    # (via clan-cli)
    subprocess.run([
        'clan', 'deploy', vm_name
    ], check=True)
```

### With Clan CLI

```python
# clan-cli integration
async def vm_deploy_command(args):
    """clan vm deploy command (delegates to VM manager)"""

    # Create VM if needed
    if not vm_manager.vm_exists(args.vm_name):
        vm_manager.create_vm(args.vm_config)

    # Start VM
    vm_manager.start_vm(args.vm_name)

    # Deploy configuration
    api = ClanAPI()
    api.deploy_to_machine(args.vm_name, args.config)
```

### With Inventory System

```python
# Report VM to inventory
def add_vm_to_inventory(vm_name: str, vm_config: VMConfig):
    """Add VM to Clan inventory"""

    inventory_entry = {
        'name': vm_name,
        'type': 'vm',
        'cpus': vm_config.cpus,
        'memory': vm_config.memory,
        'disk_size': vm_config.disk_size,
        'network_mode': vm_config.network.mode,
        'created_at': datetime.now().isoformat(),
    }

    # Write to inventory file
    inventory_file = Path('.clan/inventory/vms.json')
    add_to_inventory(inventory_entry, inventory_file)
```

## Performance Characteristics

### VM Performance

- **Startup Time:** 5-15 seconds (depending on disk size)
- **Shutdown Time:** 2-5 seconds
- **Memory Overhead:** ~10-20 MB per VM (management)
- **Disk I/O:** Full virtualization performance

### Resource Usage

- **CPU:** Minimal (management only)
- **Memory:** 50-100 MB per VM manager instance
- **Disk:** VM disk images only
- **Network:** Per-VM virtual interfaces

### Limitations

- **Concurrent VMs:** Limited by host CPU/RAM
- **Disk I/O:** Depends on storage type
- **Network:** Bridge mode requires root/privileged

## Security Considerations

### VM Isolation

- KVM provides hardware-level isolation
- Separate VM process spaces
- Independent network namespaces

### Access Control

- Unix permissions on VM state files
- Optional: libvirt ACLs
- No remote access by default

### Secure Defaults

- User-mode networking (NAT) by default
- Read-only disk templates (where applicable)
- Minimal QEMU features enabled

## Known Limitations

1. **Platform Dependent** - Requires KVM support
2. **Root Access** - Bridge networking needs privileges
3. **Manual Integration** - VM integration with Clan infra is manual
4. **No Live Migration** - No hot migration support
5. **Basic GUI** - CLI only (use desktop app for GUI)

## Future Enhancements

1. **libvirt Integration** - Use libvirt for better management
2. **Cloud Integration** - Support cloud VMs (AWS, GCP)
3. **Container Support** - LXC/LXD integration
4. **Snapshots Management** - Better snapshot handling
5. **Templates** - VM template system
6. **Web UI** - Web-based VM management

## Testing

### Test Commands

```bash
# Run all tests
pytest

# With coverage
pytest --cov=clan_vm_manager

# Specific test
pytest tests/test_vm_ops.py -v

# Integration tests
pytest tests/integration/
```

## References

- [QEMU Documentation](https://www.qemu.org/documentation/)
- [KVM Documentation](https://www.linux-kvm.org/page/Documents)
- [VM Manager Source](../pkgs/clan-vm-manager/clan_vm_manager/)
- [Test Suite](../pkgs/clan-vm-manager/tests/)
