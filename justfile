# Arda CLI Build System
# Quick builds with predictable result symlink locations

# Build arda-cli with result symlink at ./results/arda-cli
build-arda-cli:
    nix build --out-link ./results/arda-cli .#arda-cli

# Build ea-cli with result symlink at ./results/ea-cli
build-ea-cli:
    nix build --out-link ./results/ea-cli .#ea-cli

# Build all CLI tools
build-all: build-arda-cli build-ea-cli

# Clean all result symlinks
clean:
    rm -rf ./results

# List available commands
help:
    @echo "Available commands:"
    @echo "  build-arda-cli  - Build arda-cli (result at ./results/arda-cli)"
    @echo "  build-ea-cli    - Build ea-cli (result at ./results/ea-cli)"
    @echo "  build-all       - Build all CLI tools"
    @echo "  clean           - Remove all result symlinks"
    @echo "  help            - Show this help message"
