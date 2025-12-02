# Development Installation Testing Guide

This guide explains how to test `arda-cli` installation during development without pushing changes to GitHub.

## Development Workflow

### 1. Build arda-cli Locally

From the arda-core root directory (`/home/ld/src/arda-core/`):

```bash
nix build .#arda-cli
```

This creates a `result` symlink pointing to the built package at `/home/ld/src/arda-core/result`.

### 2. Test Installation Using Local Build

From your test directory (e.g., `/home/ld/src/arda/`):

```bash
nix run /home/ld/src/arda-core/.#arda-cli -- flakes create ardatest1 --force
```

Or, from anywhere:

```bash
/home/ld/src/arda-core/result/bin/arda flakes create ardatest1 --force
```

### 3. Iterative Development

After making changes to arda-cli:

1. Rebuild: `nix build .#arda-cli`
2. Test installation: `nix run /home/ld/src/arda-core/.#arda-cli -- flakes create <name> --force`
3. Repeat until working

### 4. Testing with GitHub URL (Production)

When ready to test with the published version:

```bash
cd /home/ld/src/arda
nix run "https://github.com/lorddevi/arda-core/archive/master.tar.gz#arda-cli" --refresh -- flakes create <name>
```

## Test Directory Structure

```
/home/ld/src/arda/          # Test installation directory
├── ardatest1/     # First test world
├── ardatest2/     # Second test world
└── ...
```

## Quick Commands

```bash
# Build and test
nix build .#arda-cli && nix run /home/ld/src/arda-core/.#arda-cli -- flakes create test1 --force

# Clean test worlds
rm -rf /home/ld/src/arda/ardatest*

# Check result
ls -la /home/ld/src/arda-core/result/bin/arda
```

## Troubleshooting

If templates are not found during installation:

1. Verify templates are in the package: `find $(readlink result) -name "*.nix" -path "*/data/arda/*"`
2. Check that MANIFEST.in includes templates
3. Verify pyproject.toml has correct package-data settings
4. Check flake create.py uses correct template path

Template inclusion is tracked in bead issue arda-core-4ps.
