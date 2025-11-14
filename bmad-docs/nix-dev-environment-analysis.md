# Nix Development Environment Analysis: Clan-Core vs Arda

**Date:** 2025-11-14
**Analyzed by:** Dev Story Workflow
**Subject:** Comparison of development environment setup
**Status:** CRITICAL - Immediate action required

## Executive Summary

❌ **CRITICAL ISSUE IDENTIFIED:** The current arda-core implementation uses a Python virtual environment (`.venv/`) instead of properly utilizing Nix flakes for the development environment. This is fundamentally misaligned with Nix project best practices and the clan-core approach.

## What I Implemented (arda-v1 branch)

### What I Did

1. Created `.venv/` directory with Python virtual environment
2. Installed `pre-commit`, `black`, `flake8` via pip into venv
3. Used `.pre-commit-config.yaml` for pre-commit hooks
4. Created manual documentation files

### What I Ignored

- ❌ No `flake.nix` file
- ❌ No `devShell.nix` file
- ❌ No `formatter.nix` file
- ❌ No Nix-based development environment
- ❌ No flake.lock file

## What Clan-Core Does

### 1. Flake-Based Architecture

**`flake.nix`** (clan-core):

- Uses `flake-parts` for modular flake composition
- Defines inputs for: `nixpkgs`, `flake-parts`, `disko`, `sops-nix`, `treefmt-nix`
- Imports modules conditionally based on path existence
- Supports private inputs via `devFlake/flake-compat.nix`

**`flake.lock`**:

- Locks all Nix dependencies to specific versions
- Ensures reproducible builds across environments
- Tracks: nixpkgs, nix-darwin, flake-parts, disko, sops-nix, treefmt-nix, etc.

### 2. Development Shell (devShell.nix)

```nix
devShells.default = pkgs.mkShell {
  name = "clan";
  packages = [
    select-shell          # Custom tool to switch between dev shells
    pkgs.nix-unit         # Nix testing framework
    pkgs.tea              # GitHub CLI wrapper
    pkgs.nix              # Nix itself
    self'.packages.tea-create-pr
    self'.packages.merge-after-ci
    self'.packages.pending-reviews
    config.treefmt.build.wrapper  # Code formatter
  ];
  shellHook = ''
    # Setup environment, create symlinks, generate code
  '';
}
```

**Key Differences:**

- ✅ Uses Nix-provided packages (no pip/venv)
- ✅ Dev shell includes pre-built tools from the flake
- ✅ Can switch between different shells per package
- ✅ Automatic code generation and symlink management

### 3. Code Formatting (formatter.nix)

Uses **treefmt-nix** instead of pre-commit:

- ✅ `nixfmt` - Nix file formatting (RFC style)
- ✅ `ruff` - Python formatter and linter
- ✅ `mypy` - Python type checking
- ✅ `deadnix` - Remove unused Nix code
- ✅ `shellcheck` - Shell script linting
- ✅ `prettier` - Web assets formatting
- ✅ `clang-format` - C/C++ formatting

**Usage:**

```bash
nix fmt  # Format all code
treefmt --watch  # Watch mode
```

### 4. Package-Based Development

**Individual dev shells per package** (`pkgs/clan-cli/shell.nix`):

```nix
mkShell {
  name = "clan-cli";
  buildInputs = [
    (clan-cli.pythonRuntime.withPackages (
      ps: with ps; [ mypy pytest-cov ] ++ (clan-cli.devshellPyDeps ps)
    ))
    ruff
    nix-unit
  ]
  ++ clan-cli.runtimeDependencies;

  inputsFrom = [ self'.devShells.default ];  # Inherit from default shell
}
```

**Benefits:**

- ✅ Python packages provided via Nix (no venv needed)
- ✅ Type checking with mypy
- ✅ Testing with pytest
- ✅ All runtime dependencies bundled via Nix
- ✅ Consistent across all developers

### 5. Python Package Definition (pkgs/clan-cli/default.nix)

```nix
pythonRuntime.pkgs.buildPythonApplication {
  name = "clan-cli";
  src = sourceWithoutTests;
  format = "pyproject";

  propagatedBuildInputs = [ pythonRuntimeWithDeps ] ++ bundledRuntimeDependencies;

  passthru = {
    devshellPyDeps = ps: (pyTestDeps ps) ++ (pyDeps ps) ++ (devDeps ps);
    pythonRuntime = pythonRuntime;
    runtimeDependencies = bundledRuntimeDependencies;
  };
}
```

**Key Features:**

- ✅ Build with Nix (not pip/setuptools)
- ✅ Define dependencies in Nix
- ✅ Tests run in isolated Nix environment
- ✅ Runtime dependencies bundled
- ✅ Shell completions auto-generated

## Detailed Comparison

| Aspect | My Implementation (WRONG) | Clan-Core (CORRECT) |
|--------|---------------------------|---------------------|
| **Dev Environment** | Python venv (`.venv/`) | Nix flake (`nix develop`) |
| **Package Manager** | pip | Nix |
| **Code Formatting** | pre-commit hooks | treefmt-nix |
| **Python Environment** | venv + pip | Nix-provided Python with packages |
| **Reproducibility** | ❌ Depends on user's Python setup | ✅ 100% reproducible via flake.lock |
| **Team Consistency** | ❌ Each dev has different environment | ✅ Everyone has identical environment |
| **Dependency Tracking** | ❌ No lock file | ✅ flake.lock tracks everything |
| **Testing** | ❌ Manual pytest | ✅ Nix-based test suites |
| **Build System** | ❌ Python-based | ✅ Nix-based |
| **Shell Integration** | ❌ Manual activation | ✅ Automatic via direnv |

## Required Changes for Arda

### 1. Create flake.nix

```nix
{
  description = "arda - minimal infrastructure management for NixOS";

  inputs = {
    nixpkgs.url = "https://nixos.org/channels/nixpkgs-unstable/nixexprs.tar.xz";
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
    systems.url = "github:nix-systems/default";
  };

  outputs = { inputs, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import systems;
      imports = [
        ./devShell.nix
        ./formatter.nix
        ./pkgs/flake-module.nix
      ];
    };
}
```

### 2. Create devShell.nix

```nix
{ ... }:
{
  perSystem = { pkgs, ... }: {
    devShells.default = pkgs.mkShell {
      name = "arda";
      packages = [
        pkgs.nix
        pkgs.nix-unit
        pkgs.tea
        pkgs.git
        pkgs.gh
        pkgs.age
        # formatter will be added by formatter.nix
      ];
      shellHook = ''
        echo "Welcome to Arda development environment"
        # Setup commands
      '';
    };
  };
}
```

### 3. Create formatter.nix

```nix
{ inputs, ... }:
{
  imports = [ inputs.treefmt-nix.flakeModule ];
  perSystem = { self', pkgs, ... }: {
    treefmt.programs.nixfmt.enable = true;
    treefmt.programs.ruff.enable = true;
    treefmt.programs.shellcheck.enable = true;
    treefmt.programs.mypy.enable = true;
  };
}
```

### 4. Create pkgs/flake-module.nix

```nix
{ ... }:
{
  perSystem = { pkgs, self', ... }: {
    packages = {
      # Define arda-cli package here
    };
  };
}
```

### 5. Define arda-cli package

```nix
{ python3, ... }:
python3.pkgs.buildPythonApplication {
  name = "arda-cli";
  src = ./arda-cli;
  format = "pyproject";

  propagatedBuildInputs = with python3.pkgs; [
    click
    pyyaml
    rich
    # etc.
  ];

  meta.mainProgram = "arda";
}
```

### 6. Update .gitignore

Remove `.venv/` from repository and add:

```
# Nix
result
result-*
.devShells/
.flake.lock
```

### 7. Remove Pre-commit

Replace `.pre-commit-config.yaml` with `formatter.nix` + `treefmt`.

### 8. Update Documentation

- Remove pip installation instructions
- Add `nix develop` instructions
- Document `nix fmt` for code formatting

## Directory Structure Comparison

### Current (WRONG) - arda-v1 branch

```
arda-core/
├── .venv/                          ❌ Python venv (should NOT exist)
│   ├── bin/
│   │   ├── activate
│   │   ├── pre-commit              ❌ Installed via pip
│   │   ├── black                   ❌ Installed via pip
│   │   └── flake8                  ❌ Installed via pip
│   └── lib/python3.x/site-packages/
├── .pre-commit-config.yaml         ❌ Pre-commit hooks (not Nix-native)
├── .secrets.baseline               ⚠️ OK but managed differently in Nix
├── .markdownlint.json              ⚠️ OK
├── .gitignore                      ⚠️ Ignores venv (wrong approach)
├── README.md
├── CONTRIBUTING.md
├── pkgs/
│   └── arda-cli/                   ⚠️ Directory exists but no Nix package
│       ├── commands/               ⚠️ Empty - no actual CLI implementation
│       └── lib/arda/
└── modules/nixos/                  ⚠️ Structure exists but no actual modules
    ├── profiles/
    ├── roles/
    └── lib/
```

**Problems:**

- No `flake.nix` - not a Nix project
- `.venv/` tracked in git - breaks Nix reproducibility
- Tools via pip instead of Nix
- No actual package implementations
- Not using direnv

---

### Correct (CLAN-CORE) - clan-core branch

```
clan-core/
├── flake.nix                       ✅ Main flake definition
├── flake.lock                      ✅ Locks all dependencies
├── devShell.nix                    ✅ Development environment
├── formatter.nix                   ✅ Code formatting configuration
├── pkgs/
│   ├── clan-cli/
│   │   ├── default.nix             ✅ Nix package definition
│   │   ├── shell.nix               ✅ Package-specific dev shell
│   │   ├── pyproject.toml          ✅ Python metadata
│   │   └── clan_cli/               ✅ Actual Python code
│   ├── clan-app/                   ✅ Other packages
│   └── flake-module.nix            ✅ Package module for flake-parts
├── nixosModules/                   ✅ NixOS modules
├── templates/                      ✅ Templates
├── hosts/                          ✅ Host configurations
└── lib/                            ✅ Core library
    └── filter-clan-core/
        └── flake-module.nix

# Developer workflow:
# 1. Clone repo
# 2. nix develop                    ✅ Sets up everything
# 3. nix fmt                        ✅ Formats code
# 4. nix build                      ✅ Builds packages
# 5. direnv allow                   ✅ Auto-activates environment
```

**Benefits:**

- Complete flake-based setup
- All tools via Nix (no pip/venv)
- Reproducible builds
- Standardized development workflow
- Multiple dev shells per package

---

## Development Workflow Comparison

### Current (WRONG)

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install pre-commit black flake8
pre-commit install

# Development
source .venv/bin/activate
black .
flake8 .
pytest
git commit  # Runs pre-commit hooks
```

### Correct (CLAN-CORE)

```bash
# Setup (one time)
git clone <repo>
cd <repo>
nix develop  # Everything installed automatically

# Development
nix fmt      # Format code
nix build    # Build packages
nix test     # Run tests
git commit   # Pre-commit via treefmt-nix

# Auto-activation
echo "use nix" >> .envrc
direnv allow  # Automatically activates environment
```

## Benefits of Proper Nix Setup

1. **100% Reproducible**: Same environment for all developers
2. **No Dependencies Issues**: Everything via Nix, no conflicts
3. **Consistent Builds**: `nix build` works the same everywhere
4. **Better Testing**: `nix flake check` validates everything
5. **Easy Onboarding**: `nix develop` sets up everything
6. **direnv Integration**: Automatic environment activation
7. **Multi-Platform**: Works on Linux, macOS, NixOS

## Next Steps

1. Create proper `flake.nix` following clan-core pattern
2. Remove `.venv/` and all venv-based tooling
3. Define `arda-cli` package in Nix
4. Create `devShell.nix` with all development tools
5. Replace `pre-commit` with `treefmt-nix`
6. Test with `nix develop` and `nix fmt`
7. Update all documentation

## Conclusion

The current implementation fundamentally misunderstands Nix project conventions. Clan-core provides an excellent reference for how to properly set up a Nix-based development environment. Arda should adopt the same approach to ensure consistency, reproducibility, and maintainability.

**Priority:** CRITICAL - Must fix before any feature development
**Impact:** Affects all developers and the entire development workflow
**Effort:** Medium - Requires restructuring the repository setup

---

## Action Items

### Immediate (Story 1.1 Follow-up)

- [ ] Create `flake.nix` file
- [ ] Create `devShell.nix` file
- [ ] Create `formatter.nix` file
- [ ] Create `pkgs/flake-module.nix` file
- [ ] Define `pkgs/arda-cli/default.nix` package
- [ ] Remove `.venv/` directory
- [ ] Remove `.pre-commit-config.yaml`
- [ ] Update `.gitignore` to exclude Nix artifacts and include venv
- [ ] Update README.md with `nix develop` instructions
- [ ] Update CONTRIBUTING.md with Nix workflow
- [ ] Test development environment with `nix develop`
- [ ] Test code formatting with `nix fmt`

### Priority

- **Story 1.1 was completed incorrectly** - it needs to be redone with proper Nix setup
- This is a blocker for all future development
- All team members need consistent Nix-based environment

---

**References:**

- Clan-Core: `git checkout clan-core && ls -la`
- Nix Flakes: <https://nixos.wiki/wiki/Flakes>
- treefmt-nix: <https://github.com/numtide/treefmt-nix>
- flake-parts: <https://github.com/hercules-ci/flake-parts>
