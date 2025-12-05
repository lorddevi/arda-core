# Clan-Core Nix Interactions Research

## Executive Summary

This document provides a comprehensive analysis of Nix interactions in the clan-core project. The research reveals a sophisticated multi-layered approach to Nix integration, from low-level command wrappers to high-level CLI operations for managing NixOS systems.

### Key Findings

- Centralized Nix interaction library (`clan_lib/nix`)
- Flake-centric architecture with custom selector system
- Integration with nixos-anywhere for system deployment
- Extensive use of `nix build`, `nix eval`, and `nix shell`
- Command-line interface supporting 10+ major operation categories

---

## 1. Core Nix Library (`clan_lib/nix/__init__.py`)

The foundation module providing low-level Nix command wrappers and utilities.

### 1.1 Command Construction

### `nix_command(flags: list[str]) -> list[str]`

- Constructs nix command with experimental features enabled
- Adds `--extra-experimental-features nix-command flakes`
- Supports test store override via `CLAN_TEST_STORE` environment variable
- **Usage:** Base function for all other command builders

### Example Usage

```python
cmd = nix_command(["eval", "--json", "nixpkgs#hello"])
run(cmd)
```

### 1.2 Nix Operations

#### Build Operations

### `nix_build(flags: list[str], gcroot: Path | None) -> list[str]`

- Constructs `nix build` commands
- Flags: `--print-out-paths`, `--print-build-logs`, `--show-trace`
- Optional gcroot support with `--out-root`
- Defaults to `--no-link` when no gcroot provided

### `nix_add_to_gcroots(nix_path: Path, dest: Path)`

- Uses `nix-store --realise` to add paths to gcroots
- Only runs outside nix sandbox (`IN_NIX_SANDBOX` env var check)

### Store Operations

### `nix-store --realise`

- Used by: `nix_add_to_gcroots()` for managing gcroots
- Pattern: `["nix-store", "--realise", path, "--add-root", dest]`

#### Evaluation Operations

### `nix_eval(flags: list[str]) -> list[str]`

- Constructs `nix eval` commands
- Always uses: `--json`, `--print-build-logs`, `--show-trace` (if debug)
- In sandbox: Overrides nixpkgs input with specific source
- **Used by:** flake evaluation, machine config parsing

### `nix_flake_show(flake_url: str | Path) -> list[str]`

- Returns command for `nix flake show --json`
- Includes `--show-trace` when debug enabled
- **Used by:** flake metadata retrieval

#### Flake Metadata

### `nix_metadata(flake_url: str | Path) -> dict[str, Any]`

- Runs `nix flake metadata --json`
- Returns parsed JSON metadata
- **Used by:** Flake class initialization

#### Configuration

### `nix_config() -> dict[str, Any]`

- Runs `nix config show --json`
- Returns parsed config as flat key-value dict
- **Cache:** Memoized with `@cache`
- **Used by:** Getting system type, configuring builds

### 1.3 Shell Environment

### `nix_shell(packages: list[str], cmd: list[str]) -> list[str]`

- Creates `nix shell` commands for package provisioning
- **Features:**
  - Allowlist enforcement (packages must be in `allowed-packages.json`)
  - Static package detection (via `CLAN_PROVIDED_PACKAGES`)
  - Sandbox-aware (returns cmd directly in sandbox)
  - Uses `nixpkgs#package` format for missing packages

### Class: `Packages`

- **allowed_packages:** Loaded from `allowed-packages.json`
- **static_packages:** From `CLAN_PROVIDED_PACKAGES` env var
- **Methods:**
  - `ensure_allowed(package)` - Validates against allowlist
  - `is_provided(program)` - Checks if program is statically available

### 1.4 Test Store Support

### `nix_test_store() -> Path | None`

- Handles `CLAN_TEST_STORE` environment variable
- Creates locked temporary directory for test isolation
- Only active when `IN_NIX_SANDBOX` is set

---

## 2. Flake Library (`clan_lib/flake/flake.py`)

Sophisticated flake handling with custom selector system and caching.

### 2.1 Core Flake Class

### Class: `Flake`

- Represents a Nix flake with caching and metadata
- **Key Attributes:**
  - `identifier`: Flake URL or path
  - `store_path`: Cached store path
  - `hash`: Flake narHash
  - `_is_local`: Boolean for local vs remote flakes

### Initialization

```python
flake = Flake("path:/my/flake", nix_options=["--option", "foo", "bar"])
flake.invalidate_cache()  # Loads metadata and cache
```

### 2.2 Nix Command Invocation Patterns

#### Flake Prefetch

**Location:** Lines 880-916

```python
cmd = [
    "flake",
    "info",
    "--json",
    *self.nix_options,
    "--option", "flake-registry", "",
    self.identifier,
]
flake_prefetch = run(nix_command(cmd), RunOpts(trace=trace_prefetch))
```

### Error Handling

- `No such file or directory` → `FlakeDoesNotExistError`
- `could not find a flake.nix file` → `FlakeInvalidError`

#### Attribute Selection via Build

**Location:** Lines 956-1063

- Most sophisticated Nix integration
- Uses `nix build --expr` to evaluate complex expressions
- Generates Nix code that:
  1. Gets flake via `builtins.getFlake`
  2. Uses custom `selectLib.applySelectors` function
  3. Outputs JSON via derivation

### Example Generated Expression

```nix
let
  flake = builtins.getFlake "path:/nix/store/...?narHash=abc";
  selectLib = (builtins.getFlake "path:/select-lib?narHash=xyz").lib;
in
derivation {
  name = "clan-flake-select";
  result = builtins.toJSON [
    (selectLib.applySelectors (builtins.fromJSON '{"type":"str","value":"machines"}') flake)
  ];
  preferLocalBuild = true;
  allowSubstitutes = false;
  passAsFile = [ "result" ];
  system = "x86_64-linux";
  builder = "/bin/sh";
  args = [ "-c", "read -r x < \"$resultPath\"; printf %s \"$x\" > $out" ];
}
```

### Execution

```python
build_output = Path(
    run(
        nix_build(["--expr", nix_code, *nix_options]),
        RunOpts(log=Log.NONE, trace=trace),
    ).stdout.strip(),
)
```

### 2.3 Selector System

### Custom Selector Language

- Parses dot-separated paths: `a.b.c`
- Supports wildcards: `*` (select all)
- Supports optional attributes: `?` (maybef)
- Supports multisets: `{key1,key2}`
- JSON-serialized and embedded in Nix expressions

### Examples

- `machines` → Select machines dict
- `machines.*.config` → Select all machine configs
- `machines.myhost?network` → Select network if present
- `machines.{name,ip}` → Select name and ip fields

### 2.4 Store Path Utilities

### `find_store_references(text: str) -> list[str]`

- Regex-based store path detection
- Handles chroot environments via `NIX_STORE_DIR`

### `get_physical_store_path(store_path: str) -> Path`

- Converts `/nix/store/hash-name` to physical location
- Handles `CLAN_TEST_STORE` for test environments

---

## 3. Machine Management (`clan_lib/machines/`)

NixOS machine lifecycle management including installation and updates.

### 3.1 Installation Process (`install.py`)

### `run_machine_install(opts: InstallOptions, target_host: Remote)`

#### Steps

1. **Nix Configuration:** `nix_config()` gets system type
2. **Precaching:** Pre-load machine attributes via flake selectors
3. **Generators:** Run var generators
4. **Secrets:** Upload secret facts and vars
5. **NixOS-Anywhere:** Deploy system

### NixOS-Anywhere Invocation (Lines 125-150)

```python
cmd = [
    "nixos-anywhere",
    "--flake",
    f"{machine.flake}#{machine.name}",
    "--extra-files",
    str(activation_secrets),
]

# Disk encryption keys
for path in partitioning_secrets.rglob("*"):
    if path.is_file():
        cmd.extend([
            "--disk-encryption-keys",
            str("/run/partitioning-secrets" / path.relative_to(partitioning_secrets)),
            str(path),
        ])

if opts.no_reboot:
    cmd.append("--no-reboot")

if opts.phases:
    cmd += ["--phases", str(opts.phases)]
```

#### Nix Shell Usage

- Ensures `nixos-anywhere` is available in shell
- Uses allowlist enforcement
- Supports offline building

### 3.2 Machine Class (`machines.py`)

### Class: `Machine`

- Represents a single machine configuration
- Loads flake attributes: `clanInternals.machines.{system}.{name}.*`
- Queries system type from Nix config

### Key Methods

- `select()`: Retrieves machine attributes from flake
- `flake.precache()`: Pre-loads multiple attributes

### 3.3 Hardware Configuration (`hardware.py`)

### Hardware Configuration Generation

- Generates NixOS hardware configuration
- Uses nix eval to check existing config
- Integrates with flake system

---

## 4. CLI Command Structure (`clan_cli/`)

### 4.1 Main CLI (`cli.py`)

### Global Flags

- `--flake PATH`: Path to flake (env: CLAN_DIR)
- `--option name value`: Set Nix option
- `--debug`: Enable debug logging

### Subcommands

- `machines/*`: Machine lifecycle management
- `secrets`: Secret management
- `vars`: Variable management
- `facts`: Fact generation
- `select`: Flake attribute selection
- `templates`: Template operations
- `backups`: Backup operations
- `network`: Network operations
- `flash`: Flashing operations
- `vms`: Virtual machine operations
- `state`: State management

### 4.2 Machine Commands (`machines/`)

| Command | Purpose | Nix Operations |
|---------|---------|----------------|
| `create` | Create new machine | Flake eval, nix build |
| `install` | Install OS via nixos-anywhere | nixos-anywhere, nix config |
| `update` | Update machine configuration | nix build, flake eval |
| `delete` | Remove machine | Nix store operations |
| `generations` | List boot generations | nix-env, nix-store |
| `hardware` | Generate hardware config | nix eval |
| `list` | List machines | Flake eval |
| `morph` | Morph deployment | nix build |

### 4.3 Select Command (`select.py`)

**Purpose:** Query arbitrary flake attributes

```bash
clan select machines.myhost.config
```

**Implementation:** Uses Flake.select() with JSON output

---

## 5. Nix Tool Integrations

### 5.1 nixos-anywhere

**Usage:** System installation and deployment
**Called by:** `machines install`
**Command:** `nixos-anywhere --flake <flake>#<machine>`

### Features

- Disk encryption key handling
- Phase-based installation
- Secret file upload
- No-reboot option

### 5.2 nix-shell

**Usage:** Package environment provisioning
**Called by:** Various commands needing external tools
**Integration:** `nix_shell()` wrapper with allowlist

### Example

```python
cmd = nix_shell(["git", "rsync"], ["my-script.sh"])
run(cmd)
```

### 5.3 nix-build

**Usage:** Building derivations and expressions

### Called by

- Flake attribute selection
- Machine config building
- Template instantiation

### 5.4 nix-eval

**Usage:** Querying flake attributes

### Called by

- Machine listing
- Config validation
- Metadata retrieval

### 5.5 nix flake

### Operations

- `show`: Query flake structure
- `metadata`: Get flake metadata
- `info`: Get detailed info with JSON output

### 5.6 nix-store

### Operations

- `--realise`: Realize derivations
- `--add-root`: Add to gcroots

### 5.7 nixos-rebuild

**Usage:** Updating running systems and testing configurations

### Called by

- `machines update` - For live system updates
- `machines morph` - For morph deployment with dry-run

### Operations

### Switch (update.py)

```python
switch_cmd = ["nixos-rebuild", "switch", "--flake", f"{flake}#{machine}"]
if target_host.user != "root":
    switch_cmd += ["--use-remote-sudo"]
run(switch_cmd)
```

### Dry-Activate (morph.py)

```python
run([
    f"{result_path}/sw/bin/nixos-rebuild",
    "dry-activate",
    "--flake",
    f"{flakedir}#{name}",
])
```

### Test (morph.py)

```python
run([
    f"{result_path}/sw/bin/nixos-rebuild",
    "test",
    "--flake",
    f"{flakedir}#{name}",
])
```

### Features

- `--flake`: Specifies flake and target
- `--use-remote-sudo`: For non-root deployments
- Multiple operations: switch, dry-activate, test
- Uses system-specific path: `/run/current-system/sw/bin/nixos-rebuild`

**Note:** For Darwin systems, uses `/run/current-system/sw/bin/darwin-rebuild`

---

## 6. Common Patterns

### 6.1 Command Execution Pattern

```python
from clan_lib.cmd import run, RunOpts, Log

# Build command
cmd = nix_command(["build", "--print-out-paths", "flake#package"])

# Run with logging options
proc = run(cmd, RunOpts(trace=debug, log=Log.ALL))

# Parse output
result = proc.stdout.strip()
```

### 6.2 Error Handling Pattern

```python
try:
    cmd = nix_command(["eval", "flake#attr"])
    result = run(cmd)
except ClanCmdError as e:
    if "attribute missing" in str(e):
        raise ClanError("Attribute not found") from e
    raise
```

### 6.3 Flake Selection Pattern

```python
flake = Flake(flake_path)
flake.invalidate_cache()

# Cache multiple attributes
flake.precache([
    "machines.{name,config}",
    "clan.core.vars.generators",
])

# Select single attribute
value = flake.select("machines.myhost.config")
```

### 6.4 Nix Shell Pattern

```python
# Ensure packages available
cmd = nix_shell(["nixos-anywhere", "git"], ["/path/to/script"])
run(cmd)
```

---

## 7. Environment Variables

| Variable | Purpose |
|----------|---------|
| `CLAN_TEST_STORE` | Test Nix store path |
| `LOCK_NIX` | Lock file for test store |
| `IN_NIX_SANDBOX` | Indicates running in Nix sandbox |
| `CLAN_DEBUG_NIX_PREFETCH` | Trace flake prefetch |
| `CLAN_DEBUG_NIX_SELECTORS` | Trace selector execution |
| `CLAN_PROVIDED_PACKAGES` | Colon-separated static packages |
| `CLAN_DIR` | Default flake path |

---

## 8. Configuration Files

### 8.1 allowed-packages.json

- JSON array of allowed package names
- Enforced by `nix_shell()` for security
- Located in `clan_lib/nix/allowed-packages.json`

### 8.2 flake.nix

- Standard Nix flake definition
- Must export `clan` attribute
- Pattern: `clan = clan.config;`

---

## 9. Library Dependencies

### 9.1 Internal Libraries

- `clan_lib.cmd`: Process execution (`run()`, `RunOpts`)
- `clan_lib.errors`: Error handling (`ClanError`, `ClanCmdError`)
- `clan_lib.dirs`: Directory management
- `clan_lib.machines`: Machine operations
- `clan_lib.ssh`: SSH operations
- `clan_lib.vars`: Variable management

### 9.2 External Tools

- **nix**: Core Nix commands
- **nixos-anywhere**: System deployment
- **git**: Flake repository management
- **ssh**: Remote operations

---

## 10. Testing Infrastructure

### 10.1 Test Store

- Isolated Nix store for testing
- Controlled by `CLAN_TEST_STORE`
- Locked access via `LOCK_NIX`
- Enabled only when `IN_NIX_SANDBOX` set

### 10.2 Fixtures

- `flake_hooks.py`: Flake test utilities
- `flakes/flakes.py`: Mock flake setup

---

## 11. Key Insights for arda-cli

### 11.1 Essential Nix Operations to Implement

1. **nix_command()** - Base command builder with experimental features
2. **nix_eval()** - Attribute querying with JSON output
3. **nix_build()** - Building derivations and expressions
4. **nix_shell()** - Package environment provisioning
5. **nix_metadata()** - Flake metadata retrieval

### 11.2 Flake Architecture

- Central Flake class with caching
- Custom selector language for attribute access
- Precaching system for performance
- Store path abstraction for chroot environments

### 11.3 CLI Design Patterns

- Global `--flake` and `--option` flags
- Modular subcommand structure
- Rich error messages with Nix trace context
- Debug logging with `CLAN_DEBUG_*` variables

### 11.4 Integration Points

- **nixos-anywhere**: For system installation
- **Custom Nix expressions**: For complex queries
- **Store path handling**: For build artifacts
- **Shell provisioning**: For tool availability

### 11.5 Security Considerations

- Package allowlist enforcement
- Static package verification
- Sandbox-aware execution
- Store path validation

---

## 12. Recommended Module Structure (OBSOLETE - See Section 15)

**This section is outdated.** The original monolithic `nix.py` module design has been superseded by the **modular architecture** detailed in **Section 15**.

### Historical approach (Section 12)

```python
# Single monolithic module
nix.py
├── nix_command()
├── Flake class
├── nix_build()
└── ...
```

### Current recommended approach (Section 15)

```python
# Modular structure with separation of concerns
lib/nix/
├── core.py      # Command builders
├── flake.py     # Flake class & selectors
├── store.py     # Store operations
├── shell.py     # Shell provisioning
├── system.py    # System operations
├── user.py      # User operations (NEW)
└── types.py     # Shared types
```

### Rationale for modular approach

- ✓ Better testability (test modules in isolation)
- ✓ Clear separation of concerns
- ✓ Easier to maintain and extend
- ✓ Prevents monolithic bloat
- ✓ Supports both system and user management

### See Section 15 for the complete modular architecture specification

---

## 13. Command Mapping for arda

Based on clan-cli, arda should support:

| Clan Command | Purpose | arda Equivalent | Nix Ops |
|--------------|---------|-----------------|---------|
| `machines create` | Create machine | `arda host create` | nix eval, build |
| `machines install` | Install OS | `arda host deploy` | nixos-anywhere |
| `machines update` | Update config | `arda host update` | nix build |
| `machines list` | List machines | `arda host list` | nix eval |
| `machines delete` | Delete machine | `arda host delete` | nix-store |
| `machines generations` | Boot entries | `arda host generations` | nix-env |
| `machines hardware` | HW config | `arda host hardware` | nix eval |
| `select` | Query attrs | `arda eval` | nix build |
| `secrets` | Secret mgt | `arda secrets` | nix eval |
| `vars` | Variables | `arda vars` | nix eval |
| `templates` | Templates | `arda templates` | nix build |

---

## 14. Clan's Limitations: Missing User Profile Management

A key architectural limitation discovered during analysis: **clan does not manage user environments or home-manager profiles**.

### 14.1 Clan's System-Only Focus

### What clan manages

- ✓ NixOS system profiles (via nixos-rebuild)
- ✓ Machine configurations through flakes
- ✓ System-level secrets and variables
- ✓ Hardware configurations

### What clan DOES NOT manage

- ✗ User profiles (nix-env style)
- ✗ Home-manager profiles
- ✗ User dotfiles and configurations
- ✗ Personal package collections
- ✗ User-level secrets

### 14.2 Why This Matters for arda

Arda's design goal is **unified system + user management**, going beyond clan's infrastructure-only approach:

```
Clan's Scope:
  System Profiles (NixOS) ✓
  User Environments        ✗

Arda's Scope:
  System Profiles (NixOS) ✓
  User Environments       ✓  ← NEW
```

### User environment management includes

- Declarative home-manager configurations
- Dotfile management through templates
- User-specific package collections
- Shell configurations (zsh, bash, fish)
- Application settings (vim, neovim, etc.)
- User-level secrets
- Development environment templates

### 14.3 Impact on Architecture

Clan's single-module approach (`clan_lib/nix/__init__.py`) is sufficient for system-only management but **inadequate for arda's expanded scope**.

### Required extensions for arda

1. **User/Profile module** - Home-manager integration
2. **Dotfile management** - Template system extension
3. **User secrets** - Separate from system secrets
4. **Multi-user support** - Per-user configurations

---

## 15. Proposed Modular Architecture for arda-cli

To support both system and user management while maintaining code quality, arda-cli will use a **modular nix library structure** with clear separation of concerns.

### 15.1 Directory Structure

```
pkgs/arda-cli/arda_cli/lib/nix/
├── __init__.py           # Public API, main exports
├── core.py               # Core command builders (nix_command, nix_eval, etc.)
├── flake.py              # Flake class, selectors, caching (from clan)
├── store.py              # Store operations (gcroots, paths, references)
├── shell.py              # Shell provisioning (nix_shell, packages)
├── system.py             # System operations (nixos-rebuild, nixos-anywhere)
├── user.py               # User operations (home-manager, profiles)
└── types.py              # Shared types, exceptions, dataclasses
```

### 15.2 Module Responsibilities

#### 15.2.1 `core.py` - Foundation

**Adapted from clan_lib/nix/**init**.py:**

```python
def nix_command(flags: list[str]) -> list[str]:
    """Construct nix command with experimental features enabled"""

def nix_eval(flags: list[str]) -> list[str]:
    """Construct nix eval commands with JSON output"""

def nix_build(flags: list[str], gcroot: Path | None) -> list[str]:
    """Construct nix build commands with gcroot support"""

def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    """Create nix shell commands with package provisioning"""

def nix_metadata(flake_url: str | Path) -> dict[str, Any]:
    """Get flake metadata via nix flake metadata --json"""

def nix_config() -> dict[str, Any]:
    """Get nix config (memoized)"""

class Packages:
    """Package allowlist and static package management"""
    @staticmethod
    def ensure_allowed(package: str) -> None: ...
    @staticmethod
    def is_provided(program: str) -> bool: ...
```

#### 15.2.2 `flake.py` - Flake Management

### Direct adaptation from clan_lib/flake/flake.py

```python
class Flake:
    """Represents a flake with caching and attribute selection"""
    def __init__(self, identifier: str, nix_options: list[str] | None = None):
        self.identifier = identifier
        self.nix_options = nix_options or []

    def invalidate_cache(self) -> None:
        """Prefetch and cache flake metadata"""

    def select(self, selector: str) -> Any:
        """Select attribute using clan's selector system"""

    def precache(self, selectors: list[str]) -> None:
        """Pre-cache multiple attributes for performance"""

    def select_machine(self, machine: str, selector: str) -> Any:
        """Select machine-specific attribute"""

    def select_user(self, user: str, selector: str) -> Any:
        """Select user-specific attribute (NEW in arda)"""

def parse_selector(selector: str) -> list[Selector]:
    """Parse clan's custom selector language"""

def selectors_as_json(selectors: list[Selector]) -> str:
    """Serialize selectors for embedding in Nix expressions"""
```

#### 15.2.3 `store.py` - Store Operations

### From clan_lib/flake/flake.py store utilities

```python
def find_store_references(text: str) -> list[str]:
    """Find all Nix store path references in text"""

def get_physical_store_path(store_path: str) -> Path:
    """Convert store path to physical location (handles chroot)"""

def is_pure_store_path(path: str) -> bool:
    """Check if path is a pure Nix store path"""

def nix_add_to_gcroots(nix_path: Path, dest: Path) -> None:
    """Add path to Nix gcroots (indirect gcroot via nix-store)"""
```

#### 15.2.4 `system.py` - System Operations

### Adapted from clan_lib/machines/

```python
def run_nixos_anywhere(flake: Flake, machine: str, host: Remote,
                      options: dict[str, Any]) -> None:
    """Deploy system via nixos-anywhere"""

def run_nixos_rebuild(flake: Flake, machine: str, operation: str,
                     target_host: Remote | None = None) -> None:
    """Update system via nixos-rebuild"""

def generate_hardware_config(flake: Flake, machine: str, output: Path) -> None:
    """Generate hardware configuration"""

class Machine:
    """Represents a NixOS machine configuration"""
    def __init__(self, flake: Flake, name: str): ...

    def select(self, selector: str) -> Any:
        """Select machine attribute from flake"""

    def update(self, operation: str = "switch") -> None:
        """Update machine configuration"""
```

#### 15.2.5 `user.py` - User Management (NEW)

### Extension beyond clan, for arda

```python
def run_home_manager(flake: Flake, user: str, operation: str,
                    target_host: Remote | None = None) -> None:
    """Apply user environment via home-manager"""

def generate_home_manager_expression(flake: Flake, user: str) -> str:
    """Generate Nix expression for user's home environment"""

class User:
    """Represents a user environment configuration"""
    def __init__(self, flake: Flake, name: str): ...

    def select(self, selector: str) -> Any:
        """Select user attribute from flake"""

    def apply_config(self, operation: str = "switch") -> None:
        """Apply user environment configuration"""

    def list_packages(self) -> list[str]:
        """List user's declared packages"""

    def get_dotfile(self, path: str) -> Path:
        """Get dotfile template location"""
```

#### 15.2.6 `shell.py` - Shell Provisioning

**From clan_lib/nix/**init**.py nix_shell:**

```python
def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    """Create nix shell command for package provisioning"""

def ensure_shell_tool(tool: str) -> None:
    """Ensure tool is available in shell"""

def get_user_shell_path(user: str) -> str:
    """Get user's shell path from system configuration"""
```

#### 15.2.7 `types.py` - Shared Types

```python
# Exceptions
class NixError(Exception): ...
class FlakeError(NixError): ...
class StoreError(NixError): ...
class SystemError(NixError): ...
class UserError(NixError): ...

# Shared dataclasses
@dataclass
class NixOptions:
    extra_experimental: list[str] = field(default_factory=lambda: ["nix-command", "flakes"])
    store: Path | None = None
    debug: bool = False

@dataclass
class SystemConfig:
    flake: Flake
    machine: str
    operation: str
    build_on: str | None = None

@dataclass
class UserConfig:
    flake: Flake
    user: str
    operation: str
    home_directory: Path | None = None

# Selector types (from clan)
class SelectorType(str, Enum): ...
class SelectorType(str, Enum): ...
@dataclass
class Selector: ...
```

### 15.3 Public API (`__init__.py`)

```python
# Core functionality
from .core import nix_command, nix_eval, nix_build, nix_metadata, nix_config, Packages
from .shell import nix_shell

# Flake management
from .flake import Flake, parse_selector

# Store operations
from .store import find_store_references, get_physical_store_path, is_pure_store_path

# System operations
from .system import run_nixos_rebuild, run_nixos_anywhere, Machine

# User operations
from .user import run_home_manager, User

# Shared types
from .types import NixError, FlakeError, SystemError, UserError, NixOptions, SystemConfig, UserConfig

# Public exports
__all__ = [
    # Core
    "nix_command", "nix_eval", "nix_build", "nix_metadata", "nix_config", "Packages",
    "nix_shell",

    # Flake
    "Flake", "parse_selector",

    # Store
    "find_store_references", "get_physical_store_path", "is_pure_store_path",

    # System
    "run_nixos_rebuild", "run_nixos_anywhere", "Machine",

    # User
    "run_home_manager", "User",

    # Types
    "NixError", "FlakeError", "StoreError", "SystemError", "UserError",
    "NixOptions", "SystemConfig", "UserConfig",
]
```

### 15.4 Module Dependencies

Clean dependency graph (DAG):

```
types.py (base types/exceptions)
    ↑
    ├── core.py (command builders)
    │     ↑
    │     ├── flake.py (uses core)
    │     │     ↑
    │     │     ├── store.py (uses flake)
    │     │     │
    │     │     ├── system.py (uses flake, core)
    │     │     │
    │     │     └── user.py (uses flake, core)  [NEW]
    │     │
    │     └── shell.py (uses core)
    │
    └── system.py
```

### 15.5 Usage Examples

### System management (clan pattern)

```python
# arda host update myserver
from arda_cli.lib.nix import Flake, SystemConfig, run_nixos_rebuild

flake = Flake(args.flake)
config = SystemConfig(flake=flake, machine="myserver", operation="switch")
run_nixos_rebuild(flake, "myserver", "switch")
```

### User management (NEW in arda)

```python
# arda user apply alice
from arda_cli.lib.nix import Flake, UserConfig, run_home_manager

flake = Flake(args.flake)
config = UserConfig(flake=flake, user="alice", operation="switch")
run_home_manager(flake, "alice", "switch")
```

### Combined system + user

```python
# arda machine setup myserver --with-user alice
from arda_cli.lib.nix import Flake, Machine, User

flake = Flake(args.flake)
machine = Machine(flake, "myserver")
user = User(flake, "alice")

machine.update("switch")
user.apply_config("switch")
```

### 15.6 Benefits Over Clan's Monolithic Approach

### 1. Testability

```python
# Test individual modules in isolation
pytest tests/test_nix/test_core.py      # Test command builders
pytest tests/test_nix/test_flake.py     # Test flake operations
pytest tests/test_nix/test_system.py    # Test system deployment
pytest tests/test_nix/test_user.py      # Test user management [NEW]
```

### 2. Discoverability

```python
# Easy to find what you need
from arda_cli.lib.nix.core import nix_build
from arda_cli.lib.nix.flake import Flake
from arda_cli.lib.nix.system import run_nixos_anywhere
from arda_cli.lib.nix.user import User  # NEW
```

### 3. Separation of Concerns

- **core.py**: "How do I run a Nix command?"
- **flake.py**: "How do I interact with a flake?"
- **system.py**: "How do I manage NixOS systems?"
- **user.py**: "How do I manage user environments?" [NEW]

### 4. No Circular Imports

Clean dependency structure prevents import cycles

### 5. Scalability

- Easy to add new modules (e.g., `disko.py` for disk management)
- Each module has single, clear responsibility
- New contributors can work on one module at a time

### 6. Reusability

Core utilities can be used by both system and user modules

### 15.7 Flake Structure for arda

Arda's flake will extend clan's structure:

```nix
{
  clan.core = {
    # System management (clan's approach)
    machines = {
      "myserver" = {
        config = { ... };
        network = { ... };
      };
    };

    # User management (NEW in arda)
    users = {
      "alice" = {
        homeDirectory = "/home/alice";
        shell = "zsh";
        stateVersion = "23.11";

        # Declarative packages (like machines)
        packages = [ pkgs.vim pkgs.git ];

        # Program configurations (home-manager style)
        programs = {
          vim = {
            enable = true;
            plugins = with pkgs.vimPlugins; [ vim-nix ];
          };
          zsh.enable = true;
        };

        # Dotfiles as templates (extends clan's template system)
        dotfiles = {
          ".vimrc" = ./users/alice/templates/vimrc;
          ".zshrc" = ./users/alice/templates/zshrc;
          ".gitconfig" = ./users/alice/templates/gitconfig;
        };

        # User-specific secrets (separate from system secrets)
        secrets = ./users/alice/secrets.nix;

        # Development environment templates
        devShells = {
          python = ./users/alice/shells/python;
          nodejs = ./users/alice/shells/nodejs;
        };
      };
    };

    # Shared infrastructure (clan's approach)
    vars.generators = { ... };
    templates = { ... };
    secrets = { ... };
  };
}
```

### 15.8 Implementation Phases

### Phase 1: Foundation (Clan parity)

- Implement `core.py`, `flake.py`, `store.py`, `shell.py`, `system.py`
- Support system management (clan's feature set)
- Testing and documentation

### Phase 2: User Management (Arda extension)

- Implement `user.py`
- Add home-manager integration
- Extend flake structure for users
- Add `arda user` commands

### Phase 3: Advanced Features

- Dotfile management
- User-level secrets
- Development environment templates
- Multi-user coordination

---

## 16. Further Research Needed

1. **nix store operations** - gcroot management, realization patterns
2. **flake locking** - How clan handles flake.lock updates
3. **remote builders** - Configuration and usage patterns
4. **binary caches** - substituter configuration
5. **disko integration** - disk configuration via Nix
6. **nixos-rebuild** - If/when used vs nixos-anywhere

---

## Document Metadata

- **Source Branch:** clan-core
- **Analysis Date:** 2025-11-24
- **Files Analyzed:** 45+ Python files
- **Total Lines Reviewed:** ~4,000+ lines
- **Nix Commands Identified:** 15+ distinct operations
- **CLI Commands Documented:** 30+ subcommands
- **Architecture Analysis:** Complete system + user management design
- **Modular Design Sections:** 15.1-15.8

---

## Conclusion

The clan-core project demonstrates a mature, well-architected approach to Nix integration. The modular design separates concerns between low-level command wrappers (nix module), flake handling (flake module), and CLI operations (clan_cli module). The extensive use of caching, selector systems, and sandboxing provides both performance and security.

**Key Architectural Insight:** Clan's system-only focus leaves a critical gap in user environment management. Arda-cli addresses this by extending clan's proven patterns with a **modular architecture** that supports both:

1. **System Management** (clan's approach): nixos-anywhere, nixos-rebuild, system profiles
2. **User Management** (arda's extension): home-manager integration, dotfiles, user profiles

The proposed 7-module structure (`core`, `flake`, `store`, `shell`, `system`, `user`, `types`) provides:

- Clean separation of concerns
- Enhanced testability
- Improved discoverability
- Scalable architecture for future features
- Direct adaptation of clan's most successful patterns (flake selectors, caching, command builders)

For arda-cli, adopting clan's patterns while extending to user management will provide a solid foundation for comprehensive NixOS management with the flexibility to adapt to specific use cases.
