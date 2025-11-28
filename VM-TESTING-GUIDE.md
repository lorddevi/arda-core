# VM Testing Preparation Guide

**Purpose**: Verify VM infrastructure works before Phase 4 integration testing

## Overview

Phase 4 integration tests will require **real VM functionality**, not just mocks. Before we develop Phase 4, we need to ensure your VM infrastructure (KVM/QEMU/Virsh) works correctly.

## What Phase 4 Will Require

### Real VM Operations

Phase 4 tests will actually:

- **Create VMs** using QEMU/KVM
- **Start and stop VMs** using Virsh
- **SSH into VMs** to test functionality
- **Deploy code to VMs** for integration testing
- **Test multi-host scenarios** with multiple VMs

### Example Phase 4 Test (Future)

```python
def test_vm_lifecycle():
    """Test creating, starting, stopping, and deleting a VM."""

    # Create VM (actually creates a VM instance)
    vm = VM(
        name="arda-test-vm",
        memory=2048,
        disk=10,
        network="default"
    )

    # Start VM (actually boots the VM)
    vm.start()
    vm.wait_for_ssh(timeout=60)

    # Test commands in VM (real SSH)
    result = vm.run("arda --version")
    assert result.exit_code == 0

    # Test config in VM (creates real files)
    vm.run("arda config init")
    vm.run("arda config set theme.name dracula")

    # Verify it worked
    result = vm.run("arda config view theme.name")
    assert "dracula" in result.stdout

    # Clean up
    vm.stop()
    vm.delete()
```

## VM Testing Options

### Option 1: Full VM Testing (KVM/QEMU/Virsh)

**Best for**: Native Linux or properly configured WSL2
**Requirements**:

- Linux kernel with KVM support
- QEMU installed
- Libvirt daemon running
- Proper permissions (/dev/kvm access)

**Pros**:

- Full OS isolation
- Test real boot processes
- Test actual networking
- Run NixOS VMs
- Test systemd services

**Cons**:

- Slower to start
- More resource intensive
- May not work in WSL2
- Requires nested virtualization

### Option 2: Container Testing (Docker/Podman)

**Best for**: Development, CI/CD, WSL2 environments
**Requirements**:

- Docker or Podman installed
- User in docker group

**Pros**:

- Much faster startup
- Lower resource usage
- Works reliably in WSL2
- Easy to clean up
- Good isolation for most tests

**Cons**:

- No full OS boot
- No systemd (unless using special containers)
- Different networking model

### Option 3: Hybrid Approach

**Best for**: Maximum compatibility
**Strategy**:

- Use containers for 90% of integration tests
- Use VMs only for tests that require full OS
- Provide alternative tests for both

## Testing Your Infrastructure

### Step 1: Run VM Smoke Test

```bash
cd /home/ld/src/arda-core
./bin/vm-smoke-test.sh
```

This script will check:

- Platform (Linux vs WSL2)
- KVM availability
- QEMU installation
- Libvirt daemon
- Nix VM support
- Networking

### Step 2: Try Nix VM Test

```bash
# Evaluate the VM test (should work even if VMs don't)
nix eval --file vm-tests/simple-vm-test.nix

# Try to build the container test (safer)
nix build --file vm-tests/simple-vm-test.nix arda-container-test
./result/bin/arda-container-test

# Try to build the VM test (only if your system supports it)
nix build --file vm-tests/simple-vm-test.nix arda-vm-smoke-test
```

### Expected Results

#### If VM Testing Works

```
✓ All tests passed! VM infrastructure is ready.
```

You can proceed with Phase 4 using real VMs.

#### If VM Testing Fails (Common in WSL2)

```
⚠ Some tests failed, but this is expected in WSL2
```

Recommendation: Use container-based tests for Phase 4.

#### If Major Components Missing

```
✗ Multiple tests failed. VM infrastructure needs work.
```

**Action**: Install missing components (QEMU, libvirt, etc.)

## Recommended Path Forward

### For Native Linux

1. ✅ Run `./bin/vm-smoke-test.sh`
2. ✅ Ensure all tests pass
3. ✅ Proceed with Phase 4 using **real VMs**
4. Tests will use: KVM + QEMU + Virsh

### For WSL2 (Most Common)

1. ✅ Run `./bin/vm-smoke-test.sh`
2. ⚠ Expect some failures (nested virtualization limits)
3. ✅ Proceed with Phase 4 using **containers**
4. Tests will use: Docker/Podman
5. **Note**: WSL2 can run Docker Desktop or containerd

### For CI/CD (GitHub Actions, etc.)

1. ✅ Always use **containers** (VMs may not be available)
2. ✅ Fast, reliable, and consistent
3. ✅ Proceed with Phase 4 using **containers**

## What We'll Implement

### If You Choose VMs

```python
# pkgs/arda-cli/arda_cli/testing/vm/vm_manager.py
class VMManager:
    def __init__(self, hypervisor="qemu"):
        self.hypervisor = hypervisor
        self.conn = libvirt.open()

    def create_vm(self, name, memory, disk):
        # Creates actual VM using QEMU
        vm = VM(name, memory, disk)
        vm.create()
        return vm

    def delete_vm(self, name):
        # Deletes VM and frees resources
        vm = self.get_vm(name)
        vm.delete()
```

### If You Choose Containers

```python
# pkgs/arda-cli/arda_cli/testing/containers/container_manager.py
class ContainerManager:
    def __init__(self, runtime="docker"):
        self.runtime = runtime

    def create_container(self, name, image):
        # Creates actual container
        container = Container(name, image)
        container.start()
        return container

    def delete_container(self, name):
        # Stops and removes container
        container = self.get_container(name)
        container.remove()
```

## Manual Verification Checklist

Before I develop Phase 4, please verify:

- [ ] I've run `./bin/vm-smoke-test.sh`
- [ ] I know whether my system supports VMs
- [ ] I've tested a simple Nix VM or container
- [ ] I understand the difference between VM and container testing
- [ ] I have a preference for Phase 4 implementation

## Next Steps

Once you've verified your infrastructure:

1. **Tell me the results** of `bin/vm-smoke-test.sh`
2. **Specify your preference**: VMs, Containers, or Hybrid
3. **I'll implement Phase 4** based on your infrastructure
4. **Real integration tests** will be created with actual VM/container operations

## Testing Options Summary

| Option | Speed | Isolation | Reliability | WSL2 Compatible |
|--------|-------|-----------|-------------|-----------------|
| **VMs** | Slow | Full OS | Variable | No |
| **Containers** | Fast | Process | High | Yes |
| **Hybrid** | Medium | Variable | High | Yes |

**Recommendation**: Start with containers, add VMs later for advanced tests.
