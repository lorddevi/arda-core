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

# Run all unit tests (fast + slow)
test-all:
    python -m pytest -v --tb=short

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
    @echo "  test-integration - Run all integration tests (slower)"
    @echo "  test-arda-cli   - Run arda-cli build-time tests"
    @echo "  test-watch      - Run tests in watch mode (requires pytest-watch)"
    @echo ""
    @echo "Utility Commands:"
    @echo "  clean           - Remove all result symlinks"
    @echo "  help            - Show this help message"
