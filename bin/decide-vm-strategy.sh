#!/bin/bash
# Decision Helper for VM Testing Strategy
# This helps you decide whether to use VMs or containers for Phase 4

echo "==================================================================="
echo "  VM Testing Strategy Decision Helper"
echo "==================================================================="
echo ""

# Run the smoke test first
echo "Step 1: Running VM smoke test..."
echo "==================================================================="
./bin/vm-smoke-test.sh
SMOKE_EXIT_CODE=$?
echo ""
echo ""

# Analyze results
echo "Step 2: Analyzing your environment..."
echo "==================================================================="

# Check platform
PLATFORM="unknown"
if grep -q Microsoft /proc/version 2>/dev/null; then
    PLATFORM="WSL2"
elif [ "$(uname -s)" = "Linux" ]; then
    PLATFORM="Linux"
fi

# Check VM support
VM_SUPPORT=false
if [ -e /dev/kvm ] && command -v virsh >/dev/null 2>&1; then
    VM_SUPPORT=true
fi

# Check container support
CONTAINER_SUPPORT=false
if command -v docker >/dev/null 2>&1 || command -v podman >/dev/null 2>&1; then
    CONTAINER_SUPPORT=true
fi

echo "Platform: $PLATFORM"
echo "VM Support: $VM_SUPPORT"
echo "Container Support: $CONTAINER_SUPPORT"
echo ""

# Make recommendation
echo "Step 3: Recommendation..."
echo "==================================================================="

if [ "$PLATFORM" = "WSL2" ]; then
    echo "⚠️  Detected WSL2"
    echo ""
    echo "Recommendation: Use CONTAINERS for Phase 4"
    echo ""
    echo "Why:"
    echo "  - WSL2 has limited nested virtualization"
    echo "  - /dev/kvm may not be available"
    echo "  - Libvirt may have issues"
    echo "  - Containers work reliably in WSL2"
    echo ""
    echo "Implementation Plan:"
    echo "  1. Use Docker Desktop for WSL2"
    echo "  2. Create container-based integration tests"
    echo "  3. Fast startup (< 5 seconds per test)"
    echo "  4. Good for CI/CD"
    echo ""
    STRATEGY="containers"

elif [ "$VM_SUPPORT" = true ] && [ "$PLATFORM" = "Linux" ]; then
    echo "✓ Detected native Linux with VM support"
    echo ""
    echo "Recommendation: Use VMs for Phase 4"
    echo ""
    echo "Why:"
    echo "  - Full KVM/QEMU/Virsh stack available"
    echo "  - Best for integration testing"
    echo "  - Can test NixOS, systemd, networking"
    echo "  - Full OS isolation"
    echo ""
    echo "Implementation Plan:"
    echo "  1. Create VM lifecycle management"
    echo "  2. Test NixOS VM integration"
    echo "  3. Test multi-host scenarios"
    echo "  4. Slower but more comprehensive"
    echo ""
    STRATEGY="vms"

elif [ "$CONTAINER_SUPPORT" = true ]; then
    echo "✓ Detected container support"
    echo ""
    echo "Recommendation: Use CONTAINERS for Phase 4"
    echo ""
    echo "Why:"
    echo "  - Container support detected"
    echo "  - Faster and more reliable than VMs"
    echo "  - Good for integration testing"
    echo "  - Works in any environment"
    echo ""
    echo "Implementation Plan:"
    echo "  1. Use Docker/Podman for testing"
    echo "  2. Create container-based integration tests"
    echo "  3. Fast startup and teardown"
    echo "  4. Excellent for CI/CD"
    echo ""
    STRATEGY="containers"

else
    echo "⚠️  Limited virtualization support detected"
    echo ""
    echo "Recommendation: Use CI-based container testing"
    echo ""
    echo "Why:"
    echo "  - No local VM or container support"
    echo "  - Use GitHub Actions with container runners"
    echo "  - Isolated, consistent environment"
    echo "  - No local setup required"
    echo ""
    echo "Implementation Plan:"
    echo "  1. Create container-based tests"
    echo "  2. Run tests in CI/CD pipeline"
    echo "  3. Manual local testing optional"
    echo "  4. Consistent across all environments"
    echo ""
    STRATEGY="ci-containers"
fi

echo ""
echo "==================================================================="
echo "  Decision: $STRATEGY"
echo "==================================================================="
echo ""

# Ask user
read -p "Do you want to proceed with this recommendation? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Great! I'll implement Phase 4 using: $STRATEGY"
    echo ""

    if [ "$STRATEGY" = "vms" ]; then
        echo "Next steps:"
        echo "  1. I'll create VM management infrastructure"
        echo "  2. Create real VM lifecycle tests"
        echo "  3. Test NixOS VM integration"
        echo "  4. Add multi-host test scenarios"
        echo ""
        echo "Commands to run:"
        echo "  just test-vm          # Run VM tests"
        echo "  nix build .#tests.vm  # Build VM tests"
    elif [ "$STRATEGY" = "containers" ]; then
        echo "Next steps:"
        echo "  1. I'll create container management infrastructure"
        echo "  2. Create container-based integration tests"
        echo "  3. Test app deployment to containers"
        echo "  4. Add multi-container scenarios"
        echo ""
        echo "Commands to run:"
        echo "  just test-container   # Run container tests"
        echo "  nix build .#tests.container  # Build container tests"
    else
        echo "Next steps:"
        echo "  1. I'll create CI-friendly container tests"
        echo "  2. Tests will run in GitHub Actions"
        echo "  3. Manual testing optional"
        echo "  4. Focus on CI/CD integration"
        echo ""
        echo "Commands to run:"
        echo "  nix build .#arda-cli  # Runs all tests"
        echo "  nix build             # Runs CI pipeline"
    fi
else
    echo ""
    echo "No problem! You can:"
    echo "  1. Run this script again after installing components"
    echo "  2. Tell me your preference manually"
    echo "  3. Read VM-TESTING-GUIDE.md for more details"
fi
