# Arda CLI Build System
# Quick builds with predictable result symlink locations

# =================
# Build Commands
# =================

# Build arda-cli with result symlink at ./results/arda-cli
build-arda-cli:
    nix build --out-link ./results/arda-cli .#arda-cli

# Build ea-cli with result symlink at ./results/ea-cli
build-ea-cli:
    nix build --out-link ./results/ea-cli .#ea-cli

# Build all CLI tools
build-all: build-arda-cli build-ea-cli

# =================
# Test Commands
# =================

# Run fast unit tests (the ones that run on pre-commit)
test-fast:
    python -m pytest -v -m "fast" --tb=short

# Run all unit tests (fast + slow, but exclude system tests which need infrastructure)
test-all:
    python -m pytest -v -m "not system" --tb=short

# Run only config-related tests (all types)
test-config:
    python -m pytest -v -m "config" --tb=short

# Run only config unit tests
test-config-unit:
    python -m pytest -v -m "config and unit" --tb=short

# Run only config integration tests
test-config-integration:
    python -m pytest -v -m "config and integration" --tb=short

# Run only theme-related tests
test-themes:
    python -m pytest -v -m "theme" --tb=short

# Run only CLI-related tests
test-cli:
    python -m pytest -v -m "cli" --tb=short

# Run only Nix-related tests
test-nix:
    python -m pytest -v -m "nix" --tb=short

# Run VM integration tests using NixOS framework (no manual setup required)
test-vm:
    @echo "Running NixOS VM tests (NixOS native framework)..."
    @echo "This uses the declarative NixOS test framework instead of libvirt."
    @echo ""
    nix build .#checks.x86_64-linux.arda-cli-vm
    @echo ""
    @echo "✓ VM tests completed successfully!"

# =================
# NixOS VM Test Commands
# =================

# Run NixOS VM tests using native NixOS test framework
test-vm-nixos:
    @echo "Running NixOS VM tests..."
    @echo "Building VM test: arda-cli-vm"
    nix build .#checks.x86_64-linux.arda-cli-vm
    @echo ""
    @echo "VM test built successfully!"
    @echo "To run the test manually, use: nix build .#checks.x86_64-linux.arda-cli-vm --no-out-link"
    @echo "Or check the test derivation at: result"

# Run all NixOS VM tests
test-vm-nixos-all:
    @echo "Running all NixOS VM tests..."
    @echo "Building arda-cli-vm test..."
    nix build .#checks.x86_64-linux.arda-cli-vm
    @echo ""
    @echo "Building treefmt check..."
    nix build .#checks.x86_64-linux.treefmt
    @echo ""
    @echo "All NixOS VM tests built successfully"

# =================
# Integration Test Commands
# =================

# Run all integration tests (slower, requires full environment)
test-integration:
    python -m pytest -v -m "integration" --tb=short

# Run arda-cli build-time tests (with Nix - includes all test types)
test-arda-cli:
    nix build --no-link .#arda-cli
    @echo "Build-time tests executed during nix build"

# Run tests in watch mode (rerun on file changes)
test-watch:
    @if command -v pytest-watch >/dev/null 2>&1; then \
        ptw -v -m "fast" --tb=short; \
    else \
        echo "pytest-watch not installed. Install with: pip install pytest-watch"; \
    fi

# =================
# Utility Commands
# =================

# Clean all result symlinks
clean:
    rm -rf ./results

# List available commands
help:
    @echo "Available commands:"
    @echo ""
    @echo "Build Commands:"
    @echo "  build-arda-cli  - Build arda-cli (result at ./results/arda-cli)"
    @echo "  build-ea-cli    - Build ea-cli (result at ./results/ea-cli)"
    @echo "  build-all       - Build all CLI tools"
    @echo ""
    @echo "Test Commands:"
    @echo "  test-fast       - Run fast unit tests (pre-commit compatible)"
    @echo "  test-all        - Run all unit tests (fast + slow)"
    @echo "  test-config     - Run all config tests (unit + integration)"
    @echo "  test-config-unit     - Run only config unit tests"
    @echo "  test-config-integration - Run only config integration tests"
    @echo "  test-themes     - Run theme-related tests only"
    @echo "  test-cli        - Run CLI-related tests only"
    @echo "  test-nix        - Run Nix integration tests only"
    @echo "  test-vm         - Run VM integration tests (NixOS framework)"
    @echo "  test-vm-nixos   - Run NixOS VM tests (native framework)"
    @echo "  test-vm-nixos-all - Run all checks (arda-cli-vm + treefmt)"
    @echo "  test-integration - Run all integration tests (slower)"
    @echo "  test-arda-cli   - Run arda-cli build-time tests"
    @echo "  test-watch      - Run tests in watch mode (requires pytest-watch)"
    @echo ""
    @echo "Utility Commands:"
    @echo "  clean           - Remove all result symlinks"
    @echo "  help            - Show this help message"
