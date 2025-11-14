# Integration Architecture

## Executive Summary

The **Integration Architecture** describes how the four main parts of Clan Core work together to provide a cohesive system management platform. This document explains the **data flow**, **service dependencies**, **API contracts**, and **operational workflows** across the entire ecosystem.

## System Overview

### Component Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Clan Core Ecosystem                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ clan-cli     │  │ clan-app     │  │ vm-manager   │              │
│  │ (CLI Tool)   │  │ (Desktop UI) │  │ (VM Mgmt)    │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                  │                       │
│         └─────────────────┼──────────────────┘                       │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  clanServices   │
                    │  (20+ Services) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  clanCore       │
                    │  (Infrastructure│
                    │   Modules)      │
                    └─────────────────┘
```

## Integration Points

### 1. CLI ↔ Services Integration

**Communication:** Direct command invocation
**Protocol:** Python subprocess + API calls

```
clan-cli → clanServices
    │
    ├── Deploy Config
    │   └── nixos-rebuild switch --flake .
    │
    ├── Service Management
    │   ├── systemctl start borgbackup
    │   ├── systemctl status wireguard
    │   └── systemctl restart coredns
    │
    ├── Fact Gathering
    │   └── nixos-facter
    │
    └── Secret Management
        └── sops-nix operations
```

**Implementation:**

```python
# clan-cli integration with services
class ServiceController:
    def __init__(self, machine: str):
        self.machine = machine
        self.ssh = SSHConnection(machine)

    def deploy_service(self, service_name: str):
        # Use Nix to enable service
        cmd = f'nixos-rebuild switch --flake .#{self.machine}'
        self.ssh.run(cmd)

    def check_service_status(self, service_name: str) -> ServiceStatus:
        # Query systemd
        result = self.ssh.run(f'systemctl status {service_name}')
        return self._parse_status(result.output)

    def restart_service(self, service_name: str):
        self.ssh.run(f'systemctl restart {service_name}')
```

### 2. Desktop App ↔ CLI Integration

**Communication:** HTTP API + CLI delegation
**Protocol:** Local HTTP server (localhost:8080) + subprocess

```
clan-app → clan-cli
    │
    ├── API Requests (HTTP)
    │   ├── GET /api/machines → clan machines list
    │   ├── POST /api/deploy → clan deploy <machine>
    │   └── GET /api/services → clan services list
    │
    └── Direct Execution
        ├── clan deploy <machine> --config <file>
        ├── clan services status
        └── clan inventory facts
```

**Implementation:**

```python
# clan-app backend integration
class ClanCLIProxy:
    def __init__(self):
        self.cli_path = 'clan'

    async def list_machines(self) -> List[Machine]:
        """List machines via CLI"""
        result = subprocess.run(
            [self.cli_path, 'machines', 'list'],
            capture_output=True,
            text=True
        )
        return self._parse_machines(result.stdout)

    async def deploy_machine(self, machine: str, config: Config):
        """Deploy configuration via CLI"""
        # Write config to temp file
        config_file = self._write_config(config)

        # Execute deploy command
        result = subprocess.run(
            [self.cli_path, 'deploy', machine, '--config', config_file],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise DeploymentError(result.stderr)

        return DeploymentResult.from_output(result.stdout)
```

### 3. VM Manager ↔ CLI Integration

**Communication:** CLI command delegation
**Protocol:** subprocess calls

```
clan-vm-manager → clan-cli
    │
    ├── VM Creation with Deployment
    │   ├── vm-manager create <vm>
    │   └── clan deploy <vm> --config <file>
    │
    ├── VM Integration
    │   ├── Add VM to inventory
    │   ├── Tag VM as managed
    │   └── Configure networking
    │
    └── VM Lifecycle
        ├── Pre-deploy: Start VM
        ├── Deploy: Configure system
        └── Post-deploy: Verify
```

**Implementation:**

```python
# vm-manager integration with CLI
class VMDeploymentOrchestrator:
    def __init__(self):
        self.vm_manager = VMManager()
        self.cli = ClanCLI()

    async def create_and_deploy_vm(self, vm_config: VMConfig, system_config: Config):
        """Create VM and deploy configuration"""

        # 1. Create VM
        vm = self.vm_manager.create_vm(vm_config)
        self.vm_manager.start_vm(vm.name)

        # 2. Add to inventory
        inventory_entry = {
            'name': vm.name,
            'type': 'vm',
            'vm_id': vm.id,
            'created_by': 'clan-vm-manager',
        }
        self.cli.add_to_inventory(inventory_entry)

        # 3. Deploy configuration
        await asyncio.sleep(5)  # Wait for VM boot
        deployment = self.cli.deploy(vm.name, system_config)

        # 4. Verify deployment
        if deployment.success:
            self.vm_manager.snapshot(vm.name, 'initial-deploy')

        return deployment
```

### 4. CLI ↔ VM Manager Integration

**Communication:** CLI command calls
**Protocol:** subprocess

```
clan-cli → clan-vm-manager
    │
    ├── VM Operations
    │   ├── clan vm create <name>
    │   ├── clan vm start <name>
    │   └── clan vm delete <name>
    │
    ├── VM Integration
    │   ├── VM in inventory
    │   ├── VM as deployment target
    │   └── VM service management
    │
    └── Coordinated Operations
        ├── create VM → deploy → manage
        └── delete VM → cleanup → remove from inventory
```

**Implementation:**

```python
# clan-cli VM integration
class VMIntegration:
    def __init__(self):
        self.vm_manager_cmd = 'clan-vm-manager'

    def create_vm_machine(self, vm_name: str, vm_config: VMConfig):
        """Create VM and add as deployable machine"""

        # Create VM
        result = subprocess.run([
            self.vm_manager_cmd,
            'create', vm_name,
            '--cpus', str(vm_config.cpus),
            '--memory', str(vm_config.memory),
        ], capture_output=True, text=True)

        if result.returncode != 0:
            raise VMCreateError(result.stderr)

        # Add to machine inventory
        machine_entry = {
            'name': vm_name,
            'type': 'vm',
            'provider': 'qemu',
            'created_at': datetime.now().isoformat(),
        }
        self._add_to_machines(machine_entry)

        return machine_entry

    def deploy_to_vm(self, vm_name: str, config: Config):
        """Deploy configuration to VM"""

        # Start VM if not running
        self._ensure_vm_running(vm_name)

        # Wait for network
        self._wait_for_network(vm_name)

        # Deploy via SSH
        return self._deploy_via_ssh(vm_name, config)
```

### 5. Infrastructure ↔ All Components

**Communication:** Service definitions + Nix operations
**Protocol:** Nix module system + systemd

```
clanCore (Infrastructure)
    │
    ├── Provides services to:
    │   ├── clan-cli (via Nix operations)
    │   ├── clan-app (via API queries)
    │   └── clan-vm-manager (via VM support)
    │
    ├── Service Ecosystem
    │   ├── borgbackup (backup service)
    │   ├── wireguard (VPN service)
    │   ├── coredns (DNS service)
    │   ├── garage (S3 storage)
    │   ├── matrix-synapse (chat)
    │   └── [15+ more services]
    │
    └── Infrastructure Features
        ├── Secret management (SOPS)
        ├── Network overlays (ZeroTier, Yggdrasil)
        ├── Backup orchestration
        └── VM support (nixosModules/clanCore/vm.nix)
```

**Implementation:**

```python
# Infrastructure integration layer
class ClanCoreInterface:
    """Interface to clanCore infrastructure"""

    def __init__(self, machine: str):
        self.machine = machine
        self.nix_ops = NixOperations(flake_path='.')

    def enable_service(self, service_name: str):
        """Enable service via Nix configuration"""
        # Modify flake.nix to include service
        flake = self._read_flake()
        flake.clan.services[service_name] = {'enable': True}
        self._write_flake(flake)

        # Rebuild system
        self.nix_ops.build(f'nixosConfigurations.{self.machine}')

    def gather_facts(self) -> SystemFacts:
        """Gather system facts from clanCore"""
        facts_module = 'nixosModules/clanCore/facts'

        # Import facts module
        facts = self._load_module(facts_module)

        # Collect facts
        return SystemFacts(
            hostname=facts.hostname,
            services=facts.running_services,
            network=facts.network_interfaces,
            storage=facts.storage_info,
            # ... more facts
        )

    def get_secret(self, secret_name: str) -> Secret:
        """Retrieve secret via SOPS"""
        sops_cmd = ['sops', 'decrypt', f'secrets/{secret_name}.yaml']
        result = subprocess.run(sops_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return self._parse_secret(result.stdout)
        else:
            raise SecretError(f"Failed to decrypt {secret_name}")
```

## Data Flow Patterns

### 1. Deployment Flow

```
User Input (CLI/App)
    ↓
Configuration Editor
    ↓
Validate Config
    ↓
[VM Manager] Create VM (if needed)
    ↓
Nix Build Configuration
    ↓
Deploy to Machine
    │
    ├── SSH Copy System
    ├── Activate Configuration
    ├── Start Services
    └── Update Inventory
    ↓
Report Results
```

**Implementation:**

```python
async def deploy_flow(machine: str, config: Config):
    """End-to-end deployment flow"""

    # 1. Pre-deploy checks
    await validate_config(config)
    check_machine_accessible(machine)

    # 2. Ensure VM exists (if VM target)
    if machine_type(machine) == 'vm':
        ensure_vm_running(machine)

    # 3. Build configuration
    build_result = nix_ops.build(
        f'nixosConfigurations.{machine}.config.system.build.toplevel'
    )

    # 4. Deploy
    deployment = await ssh_ops.deploy(
        machine=machine,
        build_path=build_result.path,
        config=config
    )

    # 5. Post-deploy
    if deployment.success:
        await update_inventory(machine, config)
        await run_post_deploy_scripts(machine)

    return deployment
```

### 2. Status Monitoring Flow

```
User Query (CLI/App)
    ↓
[Desktop App] HTTP API
    ↓
[Backend] Clan CLI Proxy
    ↓
Fact Gathering
    │
    ├── System Facts (nixos-facter)
    ├── Service Status (systemctl)
    ├── Inventory (inventory.json)
    └── Metrics (various sources)
    ↓
Consolidate Results
    ↓
Format Response
    ↓
Display to User
```

**Implementation:**

```python
async def get_system_status(machine: str) -> SystemStatus:
    """Get comprehensive system status"""

    # Gather facts
    facts = await gather_facts(machine)

    # Check services
    services = await check_all_services(machine)

    # Get inventory
    inventory = await get_inventory(machine)

    # Compile status
    return SystemStatus(
        machine=machine,
        facts=facts,
        services=services,
        inventory=inventory,
        uptime=facts.uptime,
        load=facts.load_average,
        # ... more status
    )
```

### 3. Inventory Sync Flow

```
System Changes
    │
    ├── Service State Changes
    ├── Hardware Changes
    └── Software Updates
    ↓
Fact Gathering
    ↓
Update Inventory
    │
    ├── Write to inventory.json
    ├── Update cached facts
    └── Sync to central registry
    ↓
Notify Components
    │
    ├── CLI (cache update)
    ├── App (real-time update)
    └── VM Manager (resource tracking)
```

**Implementation:**

```python
def sync_inventory(machine: str):
    """Sync system inventory"""

    # Gather fresh facts
    facts = gather_facts(machine)

    # Update inventory
    inventory_path = Path(f'.clan/inventory/machines/{machine}.json')
    inventory = load_inventory(inventory_path)

    inventory.update({
        'last_seen': datetime.now().isoformat(),
        'facts': facts,
        'services': facts.running_services,
        'packages': facts.packages,
        'hardware': facts.hardware,
    })

    save_inventory(inventory, inventory_path)

    # Notify other components
    notify_cli_cache_update(machine)
    notify_app_websocket(machine, 'inventory_updated')
```

## API Contracts

### CLI → Services Contract

```python
# Service control contract
class ServiceControlContract:
    """Contract for service control operations"""

    @staticmethod
    def enable_service(machine: str, service: str) -> bool:
        """Enable service on machine"""
        # Implementation: nixos-rebuild with service enabled

    @staticmethod
    def disable_service(machine: str, service: str) -> bool:
        """Disable service on machine"""

    @staticmethod
    def restart_service(machine: str, service: str) -> bool:
        """Restart service"""

    @staticmethod
    def get_service_status(machine: str, service: str) -> ServiceStatus:
        """Get service status"""

# Service configuration contract
class ServiceConfigContract:
    """Contract for service configuration"""

    @staticmethod
    def configure_service(machine: str, service: str, config: dict) -> bool:
        """Configure service with provided config"""

    @staticmethod
    def get_service_config(machine: str, service: str) -> dict:
        """Get current service configuration"""
```

### CLI → VM Manager Contract

```python
# VM lifecycle contract
class VMLifecycleContract:
    """Contract for VM lifecycle operations"""

    @staticmethod
    def create_vm(name: str, config: VMConfig) -> VM:
        """Create VM with configuration"""

    @staticmethod
    def start_vm(name: str) -> bool:
        """Start VM"""

    @staticmethod
    def stop_vm(name: str) -> bool:
        """Stop VM"""

    @staticmethod
    def delete_vm(name: str) -> bool:
        """Delete VM"""

    @staticmethod
    def list_vms() -> List[VM]:
        """List all managed VMs"""

# VM deployment contract
class VMDeploymentContract:
    """Contract for VM deployment integration"""

    @staticmethod
    def deploy_to_vm(name: str, system_config: Config) -> DeploymentResult:
        """Deploy system config to VM"""

    @staticmethod
    def add_vm_to_inventory(name: str, metadata: dict) -> bool:
        """Add VM to machine inventory"""

    @staticmethod
    def configure_vm_networking(name: str, network_config: NetworkConfig) -> bool:
        """Configure VM networking"""
```

### App → CLI Contract (HTTP API)

```python
# HTTP API contract
class HTTPAPIContract:
    """Contract for desktop app HTTP API"""

    @app.route('/api/machines', methods=['GET'])
    def list_machines(self) -> List[Machine]:
        """Get all machines - delegates to: clan machines list"""

    @app.route('/api/machines/<name>', methods=['GET'])
    def get_machine(self, name: str) -> Machine:
        """Get machine details - delegates to: clan machines show <name>"""

    @app.route('/api/deploy', methods=['POST'])
    def deploy_machine(self, data: dict) -> DeploymentResult:
        """Deploy configuration - delegates to: clan deploy <machine>"""

    @app.route('/api/services', methods=['GET'])
    def list_services(self) -> List[Service]:
        """List all services - delegates to: clan services list"""

    @app.route('/api/services/<name>/status', methods=['GET'])
    def get_service_status(self, name: str) -> ServiceStatus:
        """Get service status - delegates to: clan services status <name>"""

    @app.route('/api/vm/create', methods=['POST'])
    def create_vm(self, data: dict) -> VM:
        """Create VM - delegates to: clan-vm-manager create <name>"""

    @app.route('/api/inventory', methods=['GET'])
    def get_inventory(self) -> Inventory:
        """Get inventory - delegates to: clan inventory facts"""
```

## Service Dependencies

### Service Dependency Graph

```
borgbackup
  ↓ depends on
certificates (for encryption)
  ↓ used by
[all services with TLS]

coredns
  ↓ depends on
certificates (for TLS)
  ↓ used by
[clients needing DNS]

garage (S3 storage)
  ↓ depends on
certificates (for TLS)
  ↓ used by
[applications needing S3]

matrix-synapse
  ↓ depends on
certificates, coredns, garage (for chat, DNS, storage)
  ↓ used by
[chat clients]

wireguard
  ↓ depends on
[minimal - just network]
  ↓ used by
[VPN clients]

yggdrasil/zerotier
  ↓ depends on
[network only]
  ↓ provides
[overlay networking]

monitoring
  ↓ monitors
[all services]
```

### Cross-Part Dependencies

```
infrastructure (clanCore)
  │
  ├── provides: nixos-facter, sops-nix, service modules
  └── used by: clan-cli, clan-app

clan-cli
  │
  ├── uses: infrastructure modules, services
  └── used by: clan-app (via HTTP API)

clan-app
  │
  ├── uses: clan-cli (HTTP proxy)
  └── UI for: all CLI operations

clan-vm-manager
  │
  ├── uses: QEMU/KVM, clan-cli (for deployment)
  └── used by: clan-cli (VM commands)
```

## Error Handling Across Components

### Error Propagation

```python
# Error flow: VM Manager → CLI → App
try:
    vm_manager.create_vm(vm_config)
except VMCreateError as e:
    # Log and re-raise as deployment error
    raise DeploymentError(f"VM creation failed: {e}") from e

# In CLI
try:
    vm_manager.create_vm(vm_config)
except VMCreateError:
    click.echo("Error: Failed to create VM", err=True)
    sys.exit(1)

# In App
try:
    response = requests.post('/api/vm/create', json=config)
except ConnectionError:
    # Handle VM manager not available
    display_error("VM Manager service unavailable")
```

### Error Recovery

```python
# Rollback on deployment failure
async def deploy_with_rollback(machine: str, config: Config):
    deployment_id = generate_deployment_id()

    try:
        # Create backup
        await backup_current_config(machine, deployment_id)

        # Deploy
        await deploy_config(machine, config)

    except DeploymentError as e:
        # Rollback
        await rollback_config(machine, deployment_id)

        # Clean up backup
        await cleanup_backup(deployment_id)

        raise
```

## Performance Optimization

### Caching Strategy

```python
# Multi-layer caching
class CacheManager:
    """Manage caching across components"""

    def __init__(self):
        self.cli_cache = LocalCache(ttl=300)  # 5 min
        self.app_cache = MemoryCache(ttl=60)  # 1 min
        self.disk_cache = DiskCache(ttl=3600)  # 1 hour

    def get_machine_facts(self, machine: str) -> SystemFacts:
        # Check CLI cache first
        if cached := self.cli_cache.get(f'facts:{machine}'):
            return cached

        # Fetch from system
        facts = gather_facts(machine)

        # Store in all caches
        self.cli_cache.set(f'facts:{machine}', facts)
        self.app_cache.set(f'facts:{machine}', facts)
        self.disk_cache.set(f'facts:{machine}', facts)

        return facts
```

### Async Operations

```python
# Parallel operations across machines
async def deploy_to_multiple_machines(machines: List[str], config: Config):
    """Deploy to multiple machines in parallel"""

    async def deploy_to_single(machine: str):
        return await deploy_config(machine, config)

    # Run deployments in parallel
    tasks = [deploy_to_single(m) for m in machines]
    results = await asyncio.gather(*tasks)

    # Report results
    for machine, result in zip(machines, results):
        if result.success:
            print(f"✓ {machine}: deployed")
        else:
            print(f"✗ {machine}: {result.error}")
```

## Security Model

### Security Flow

```
User (CLI/App)
  ↓
Authentication (SSH keys / local only)
  ↓
Authorization (permission checks)
  ↓
Operation Execution
  │
  ├── Local operations (no auth needed)
  ├── Remote operations (SSH with keys)
  └── Secret operations (SOPS decryption)
  ↓
Audit Logging
  ↓
Result
```

### Secret Sharing

```python
# Secure secret sharing
class SecretManager:
    """Manage secrets across components"""

    def __init__(self):
        self.sops = SOPS()

    def get_secret(self, secret_name: str, requester: str) -> Secret:
        # Check permissions
        if not self.check_permission(requester, secret_name):
            raise PermissionError(f"{requester} cannot access {secret_name}")

        # Decrypt with SOPS
        secret = self.sops.decrypt(f'secrets/{secret_name}.yaml')

        # Log access
        self.log_access(requester, secret_name)

        return secret

    def share_secret(self, secret_name: str, target_component: str):
        # Use component-specific sharing
        if target_component == 'cli':
            self.share_via_env(secret_name)
        elif target_component == 'app':
            self.share_via_api(secret_name)
        else:
            raise ValueError(f"Unknown target: {target_component}")
```

## Monitoring and Observability

### Observability Stack

```
Application Logs
  │
  ├── clan-cli logs → ~/.clan/logs/cli.log
  ├── clan-app logs → ~/.clan/logs/app.log
  ├── vm-manager logs → ~/.clan/logs/vm-manager.log
  └── system logs → systemd journal
  ↓
Aggregation
  │
  ├── clan-core facts (nixos-facter)
  ├── service status (systemctl)
  └── deployment status (clan inventory)
  ↓
Visualization
  │
  ├── Desktop app (real-time dashboard)
  ├── CLI (clan status command)
  └── Logs (journalctl, log files)
```

### Health Checks

```python
# Health check across components
class HealthChecker:
    """Check health of all components"""

    async def check_system_health(self) -> HealthReport:
        """Comprehensive health check"""

        checks = {
            'infrastructure': await self.check_infrastructure(),
            'cli': await self.check_cli(),
            'app': await self.check_app(),
            'vm_manager': await self.check_vm_manager(),
            'services': await self.check_services(),
            'connectivity': await self.check_connectivity(),
        }

        return HealthReport(
            overall_status=self.determine_overall_status(checks),
            component_health=checks,
            timestamp=datetime.now(),
        )

    async def check_infrastructure(self) -> ComponentHealth:
        try:
            # Check Nix operations
            nix_ops = NixOperations('.')
            await nix_ops.evaluate('flake')

            # Check services
            services = await self.list_running_services()

            return ComponentHealth(
                status='healthy',
                details={'nix_ops': 'ok', 'services': len(services)}
            )
        except Exception as e:
            return ComponentHealth(status='unhealthy', error=str(e))
```

## References

- [Infrastructure Architecture](./architecture-infrastructure.md)
- [CLI Architecture](./architecture-clan-cli.md)
- [Desktop App Architecture](./architecture-clan-app.md)
- [VM Manager Architecture](./architecture-clan-vm-manager.md)
- [Project Overview](./project-overview.md)
- [Source Tree Analysis](./source-tree-analysis.md)
