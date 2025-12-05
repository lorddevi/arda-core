# nix-select Research Document

## Executive Summary

nix-select is a powerful Nix library that provides sophisticated attribute selection capabilities for querying and navigating nested data structures (both Nix attribute sets and lists) using a concise string-based selector syntax. Originally developed for the clan project, it represents a battle-tested approach to complex Nix attribute operations.

This document covers:

- What nix-select is and its capabilities
- How clan-core and clan-cli use nix-select
- Current integration in arda-core
- Future applications for arda-cli and arda-core
- VM testing considerations
- Best practices and patterns

---

## Table of Contents

1. [What is nix-select?](#what-is-nix-select)
2. [Selector Syntax](#selector-syntax)
3. [How Clan Uses nix-select](#how-clan-uses-nix-select)
   - [clan-core: Flake-level Usage](#clan-core-flake-level-usage)
   - [clan-cli: Integration and Hash Baking](#clan-cli-integration-and-hash-baking)
   - [VM Testing](#vm-testing)
4. [arda-core Integration](#arda-core-integration)
   - [Current Implementation](#current-implementation)
   - [Hash Baking Pattern](#hash-baking-pattern)
5. [Future Applications for Arda](#future-applications-for-arda)
   - [arda-cli Nix Operations](#arda-cli-nix-operations)
   - [arda-core Flake Queries](#arda-core-flake-queries)
6. [Use Cases and Examples](#use-cases-and-examples)
7. [Best Practices](#best-practices)
8. [Comparison with Alternatives](#comparison-with-alternatives)
9. [References](#references)

---

## What is nix-select?

nix-select is a **Nix library** (not Python) that provides a unified, expressive syntax for querying nested Nix data structures. It was developed by the clan project and is maintained as a separate flake.

### Key Characteristics

- **Pure Nix**: All functions are implemented in Nix, no external dependencies
- **Unified API**: Same syntax for both attribute sets and lists
- **Expressiveness**: Supports wildcards, sets, optional access, quoted keys
- **Battle-tested**: Used extensively in clan-core and clan-cli
- **External Dependency**: Available as a flake input from `https://git.clan.lol/clan/nix-select`

### Location

**Source Repository**: <https://git.clan.lol/clan/nix-select>

**Main Files**:

- `select.nix`: Core selector library (365 lines)
- `tests.nix`: Comprehensive test suite (130 lines)
- `flake.nix`: Flake output definition

---

## Selector Syntax

The selector system uses a dot-separated path notation with special operators:

### Basic Selectors

| Syntax | Meaning | Example |
|--------|---------|---------|
| `key` | Direct key access | `foo.bar` accesses `{ foo.bar = "value" }` |
| `*` | Wildcard (all items) | `packages.*` gets all values from packages |
| `.` | Path separator | `nixosConfigurations.foo.system` |

### Advanced Selectors

| Syntax | Meaning | Example |
|--------|---------|---------|
| `{a,b,c}` | Set selector (specific items) | `foo.{x,y,z}` selects x, y, and z keys |
| `?key` | Maybe (optional/conditional) | `config.?optionalFeature.enabled` only if exists |
| `"quoted"` | Special characters | `somedict."foo.bar"` accesses key with dot |
| `\.` | Escape character | `foo\.bar` matches literal "foo.bar" |
| `,` | Separator in sets | `{a,b,c}` selects multiple specific items |

### Example Data Structure

```nix
{
  packages = {
    arda-cli = { name = "arda-cli"; version = "0.1.5"; };
    other = { name = "other"; };
  };
  nixosConfigurations = {
    "test-vm".config = { services.arda.enable = true; };
    "prod".system = { version = "24.11"; };
  };
}
```

### Example Selectors

```nix
# Simple access
select "packages.arda-cli.name" data
=> "arda-cli"

# Wildcard - get all names
select "packages.*.name" data
=> { arda-cli = "arda-cli"; other = "other"; }

# Set selector - specific items only
select "packages.{arda-cli,other}.name" data
=> { arda-cli = "arda-cli"; other = "other"; }

# Nested wildcard
select "nixosConfigurations.*.config" data
=> { "test-vm" = { services.arda.enable = true; }; }

# Maybe operator - safe access
select "nixosConfigurations.?nonexistent.config" data
=> { }
```

---

## How Clan Uses nix-select

nix-select is integral to clan-core and clan-cli's architecture. Here's how:

### clan-core: Flake-level Usage

**Location**: `pkgs/clan-cli/flake-module.nix` (lines 44-45)

```nix
templateDerivation = pkgs.closureInfo {
  rootPaths =
    builtins.attrValues (self.inputs.nix-select.lib.select "clan.templates.clan.*.path" self)
    ++ builtins.attrValues (self.inputs.nix-select.lib.select "clan.templates.machine.*.path" self);
};
```

**Purpose**: Queries clan-core flake outputs to find all template paths dynamically. The selector `"clan.templates.clan.*.path"` walks the flake's `clan.templates` attribute set and extracts all paths.

**Why this is powerful**:

- No hardcoded template list
- Automatic discovery
- Scales as templates are added/removed
- Type-safe querying

### clan-cli: Integration and Hash Baking

**Challenge**: Python code needs to construct Nix flake references to nix-select at runtime, but must know the exact hash for correctness.

**Solution**: Hash baking pattern in `pkgs/clan-cli/default.nix` (lines 76-95):

```nix
cliSource = source:
  runCommand "clan-cli-source"
    { nativeBuildInputs = [ jq ]; }
    ''
      # ... other operations ...

      substituteInPlace $out/clan_lib/flake/flake.py \
        --replace-fail '@select_hash@' "$(jq -r '.nodes."nix-select".locked.narHash' ${../../flake.lock})"

      ln -sf ${nix-select} $out/clan_lib/select
    '';
```

**How it works**:

1. During build, extract nix-select hash from `flake.lock` using `jq`
2. Substitute `@select_hash@` placeholder in Python code with actual hash
3. Python uses this to construct correct flake references

**Python usage** (`pkgs/clan-cli/clan_lib/flake/flake.py`):

```python
select_hash = "@select_hash@"  # Placeholder

# At build time, this becomes: "sha256-abc123..."
if not select_hash.startswith("sha256-"):
    # Fallback logic (shouldn't normally hit)
    select_hash = select_flake.hash

# Python generates Nix code with correct flake reference:
nix_code = f"""
let
  selectLib = (
    builtins.getFlake
      "path:{select_source()}?narHash={select_hash}"
  ).lib;
in
  # ... use selectLib for operations ...
"""
```

### VM Testing

**clan-cli has sophisticated testing** that requires the full source tree including tests:

**Two source variants** (`pkgs/clan-cli/default.nix`):

```nix
# Production package - excludes tests
sourceWithoutTests = cliSource (
  nixFilter.filter {
    root = ./.;
    exclude = [ /* test file patterns */ ];
  }
);

# Test builds - includes all tests
sourceWithTests = cliSource ./.;
passthru.sourceWithTests = sourceWithTests;
```

**Why this matters**:

- **Production**: Smaller builds, faster, no test code
- **Testing**: VM tests can access full source including test files
- **Flexibility**: `passthru.sourceWithTests` exports for test harnesses

**Test usage** (`pkgs/clan-cli/default.nix`):

```bash
# VM tests copy sourceWithTests
cp -r ${sourceWithTests} ./src
cd ./src

# Then run pytest, nix tests, etc.
```

**The symlink pattern**:

```nix
# Created during build:
ln -sf ${nix-select} $out/clan_lib/select
ln -sf ${nixpkgs'} $out/clan_lib/nixpkgs
```

This makes nix-select available:

- In Nix expressions during build
- In test environments
- In runtime Python contexts

---

## arda-core Integration

### Current Implementation

**arda-core** has integrated nix-select in two phases:

#### Phase 1: Basic External Dependency

**Added to `flake.nix`**:

```nix
nix-select.url = "https://git.clan.lol/clan/nix-select/archive/main.tar.gz";
```

**Passed to arda-cli** via `pkgs/flake-module.nix`:

```nix
arda-cli = python313Packages.callPackage ./arda-cli/default.nix {
  inherit (inputs) nix-select;
  inherit (pkgs) jq runCommand;
};
```

#### Phase 2: Hash Baking (ardaSource Pattern)

**arda-core** adapted clan-cli's `cliSource` pattern as `ardaSource` (arda-branded):

**Location**: `pkgs/arda-cli/default.nix` (lines 15-40)

```nix
ardaSource = source:
  runCommand "arda-cli-source"
    { nativeBuildInputs = [ jq ]; }
    ''
      cp -r ${source} $out
      chmod -R +w $out

      # Remove old symlinks
      rm -f $out/arda_cli/select

      # Hash baking: substitute @nix_select_hash@ in Python code
      if [ -f $out/arda_cli/nix.py ]; then
        substituteInPlace $out/arda_cli/nix.py \
          --replace-fail '@nix_select_hash@' "$(jq -r '.nodes."nix-select".locked.narHash' ${../../flake.lock})"
      fi

      # Create nix-select symlink
      ln -sf ${nix-select} $out/arda_cli/select
    '';

# Use ardaSource for package
python.pkgs.buildPythonApplication {
  pname = "arda_cli";
  src = ardaSource ./.;
  # ...
}
```

**Passthru for testing**:

```nix
passthru = {
  ardaSource = ardaSource ./.;
};
```

### Hash Baking Pattern

**Why is hash baking necessary?**

When Python code generates Nix flake references to nix-select, it MUST include the exact narHash:

```nix
# Correct flake reference (must include narHash):
"path:/nix/store/cba1x9mxnwr8b36cw41bya7g6d5v1p7d-source?narHash=sha256-xyz..."

# Without hash, Nix cannot verify the reference
# Python must construct these references dynamically
```

**Hash baking flow**:

1. **Build time**: `jq` reads nix-select hash from `flake.lock`
2. **Substitution**: Replace `@nix_select_hash@` placeholder in Python
3. **Runtime**: Python uses baked hash to construct flake references
4. **Result**: Consistent, valid flake references without runtime discovery

**Example Python usage** (when arda-cli's Nix integration is built):

```python
# This will be generated by arda-cli Python:
nix_select_hash = "sha256-yxcNOha7Cfv2nhVpz9ZXSNKk0R7wt4AiBklJ8D24rVg="  # pragma: allowlist secret  # pragma: allowlist secret  # Baked

# Construct flake reference:
select_flake_ref = f"path:{nix_select_path}?narHash={nix_select_hash}"

# Generate Nix code with correct reference:
nix_code = f"""
let
  selectLib = (builtins.getFlake "{select_flake_ref}").lib;
in
  selectLib.select "packages.*" flakeData
"""
```

---

## Future Applications for Arda

### arda-cli Nix Operations

**arda-cli's primary role**: Provide imperative CLI for declarative NixOS configurations.

nix-select enables:

#### 1. Flake Output Queries

```python
# arda-cli could query flake outputs elegantly:
flake_outputs = nix_eval_flake()
selected = nix_select("packages.{arda-cli,other}.*", flake_outputs)
```

#### 2. Configuration Queries

```python
# Navigate NixOS configurations:
configs = nix_select("nixosConfigurations.*.config", flake_data)
services = nix_select("configs.*.services", configs)
```

#### 3. Dynamic Discovery

```python
# Discover available packages without hardcoding:
packages = nix_select("legacyPackages.x86_64-linux.*.name", nixpkgs_flake)
```

#### 4. Conditional Access

```python
# Maybe operator for optional features:
optional_config = nix_select("config.?arda.optionalFeature", flake_data)
```

### arda-core Flake Queries

**For arda-core's flake operations**:

```nix
# Query all arda-related outputs:
arda_outputs = self.inputs.nix-select.lib.select "arda.*" flake_data

# Get all machine configurations:
machines = self.inputs.nix-select.lib.select "machines.*.config" self

# Select specific services:
services = self.inputs.nix-select.lib.select "nixosConfigurations.*.config.services.*{nginx,ssh}" self
```

### VM Testing (Future)

**arda-core will eventually need robust testing**:

```nix
# When implemented, will follow clan pattern:
sourceWithoutTests = ardaSource (filterWithoutTests ./.);
sourceWithTests = ardaSource ./.;

passthru.sourceWithTests = sourceWithTests;  # For test harnesses

# VM test would:
# cp -r ${sourceWithTests} ./test_src
# cd test_src
# run pytest, integration tests, etc.
```

---

## Use Cases and Examples

### Example 1: Package Discovery

```nix
# Find all arda-related packages in a flake:
let
  flake_data = builtins.getFlake "path:/my/flake?narHash=...";
  arda_pkgs = self.inputs.nix-select.lib.select "packages.*{arda,cli}.*" flake_data;
in
  arda_pkgs
```

**Result**: `{ arda-cli = {...}; arda-core = {...}; }`

### Example 2: NixOS Configuration Navigation

```nix
# Extract all machine configurations:
let
  machines = self.inputs.nix-select.lib.select "nixosConfigurations.*.config" self;
in
  machines
```

**Result**: `{ "machine-1" = { ...config... }; "machine-2" = { ...config... }; }`

### Example 3: Service Discovery

```nix
# Find all enabled services across all machines:
let
  enabled_services = self.inputs.nix-select.lib.select
    "nixosConfigurations.*.config.services.*{nginx,ssh,docker}.enable"
    self;
in
  enabled_services
```

**Result**: All services where enable = true

### Example 4: Template Path Resolution (clan pattern)

```nix
# clan-core uses this to find all templates:
template_paths = builtins.attrValues (
  self.inputs.nix-select.lib.select "clan.templates.clan.*.path" self
)
```

This dynamically discovers all clan templates without hardcoding!

---

## Best Practices

### 1. Always Use Hash Baking for Python-Nix Integration

**Pattern**: If Python code generates Nix flake references, use hash baking.

```nix
# ✅ Correct: Hash baked into Python
substituteInPlace $out/module.py \
  --replace-fail '@nix_select_hash@' "$(jq -r '.nodes."nix-select".locked.narHash' ${flake.lock})"

# ❌ Avoid: Runtime hash discovery
# (slow, error-prone, inconsistent)
```

### 2. Leverage Maybe Operator for Optional Fields

```nix
# ✅ Safe access with maybe
config.?optionalFeature.enabled

# ❌ Risky: Direct access
# config.optionalFeature.enabled  # Fails if optionalFeature doesn't exist
```

### 3. Use Wildcards for Dynamic Queries

```nix
# ✅ Flexible: Adapts to new items automatically
packages.*.name

# ❌ Brittle: Requires manual updates
# packages.foo.name + packages.bar.name + ...
```

### 4. Export Source Variants for Testing

```nix
# ✅ Supports testing
passthru.sourceWithTests = sourceWithTests;

# VM tests can access full source
```

### 5. Separate Symlink Creation from Package Build

```nix
# ✅ Clean: Symlinks in ardaSource/postInstall
ln -sf ${nix-select} $out/arda_cli/select

# ❌ Mixed: Don't embed in package source
```

### 6. Document Selector Patterns

```nix
# ✅ Clear: Comment explains what selector does
# Find all machine configurations
machines = self.inputs.nix-select.lib.select "nixosConfigurations.*.config" self;

# ❌ Unclear: No context
machines = select "nixosConfigurations.*.config" self;
```

---

## Comparison with Alternatives

### Direct Nix Attribute Access

**Traditional approach**:

```nix
# Manually walk attributes:
flake_data.packages.arda-cli.name
flake_data.packages.other.version
```

**Problems**:

- Hardcoded paths
- No wildcards
- No set selections
- No optional access
- Verbose for complex queries

**nix-select advantage**:

```nix
# Unified, expressive syntax:
select "packages.{arda-cli,other}.{name,version}" flake_data
```

### Custom Python Loops

**Python approach**:

```python
for pkg_name, pkg_data in flake_data['packages'].items():
    if pkg_name in ['arda-cli', 'other']:
        result[pkg_name] = {
            'name': pkg_data['name'],
            'version': pkg_data['version']
        }
```

**Problems**:

- Imperative logic
- Error-prone
- Type mismatches
- No Nix integration
- More code to maintain

**nix-select advantage**:

```nix
# Pure Nix, declarative:
select "packages.{arda-cli,other}.{name,version}" flake_data
```

### Nix Built-in Functions

**Nix has `getAttr`, `attrValues`, etc.**:

```nix
# Functional but limited:
attrValues flake_data.packages  # All values
```

**Problems**:

- No filtering
- No path traversal
- No set operations
- Limited composition

**nix-select advantage**: Comprehensive selector language with filtering, path traversal, optional access, and set operations.

---

## Technical Deep Dive

### How parseSelector Works

**Location**: `pkgs/clan-cli/clan_lib/select/select.nix` (lines 19-251)

The `parseSelector` function is a state machine that walks through the selector string character by character, building a list of selector objects.

**Selector types**:

- `{ type = "all"; }` - Wildcard (`*`)
- `{ type = "str"; value = "foo"; }` - String key
- `{ type = "set"; value = [ {...} ]; }` - Set selector (`{a,b}`)
- `{ type = "maybe"; value = "foo"; }` - Maybe (`?foo`)

**State machine states**:

- `start`: At beginning of selector
- `str`: Building string key
- `set`: Inside `{...}` set selector
- `maybe`: Building maybe key (`?`)
- `quote`: Inside `"..."` quoted string
- `escape`: After `\` escape character

### How applySelectors Works

**Location**: `pkgs/clan-cli/clan_lib/select/select.nix` (lines 261-352)

`applySelectors` takes the parsed selector list and recursively applies it to the data structure:

```nix
recurse = selectors: idx: obj:
  if builtins.length selectors == idx then
    obj  # Base case: no more selectors
  else
    let selector = builtins.elemAt selectors idx;
    in
      if builtins.isList obj then
        # Handle lists
        ...
      else if builtins.isAttrs obj then
        # Handle attribute sets
        ...
```

**Key logic**:

1. **Lists**:
   - `all`: Map over all items
   - `str`: Index into list (numeric string)
   - `set`: Select multiple indices
   - `maybe`: Safe access by index

2. **Attrsets**:
   - `all`: Map over all values
   - `str`: Get attribute
   - `set`: Select multiple attributes
   - `maybe`: Conditional attribute access

3. **Primitives**:
   - `maybe`: Return empty set if doesn't exist
   - `set`: Merge selected attributes

### Hash Baking Mechanics

**Why not just use the symlink path?**

Nix flake references MUST include the narHash for security and correctness:

```nix
# Without hash:
"path:/nix/store/abc123-source"

# Problem: Nix can't verify this is the correct version!
# Could be tampered with, or just wrong version.

# With hash:
"path:/nix/store/abc123-source?narHash=sha256-xyz..."

# ✅ Nix verifies the hash matches the fetched content
```

**Hash baking process**:

1. **fl.lock** contains pinned narHash:

```json
{
  "nodes": {
    "nix-select": {
      "locked": {
        "narHash": "sha256-yxcNOha7Cfv2nhVpz9ZXSNKk0R7wt4AiBklJ8D24rVg="  # pragma: allowlist secret
      }
    }
  }
}
```

1. **jq** extracts it:

```bash
jq -r '.nodes."nix-select".locked.narHash' flake.lock
# Output: sha256-yxcNOha7Cfv2nhVpz9ZXSNKk0R7wt4AiBklJ8D24rVg=
```

1. **substituteInPlace** replaces placeholder:

```python
# Before build:
nix_select_hash = "@nix_select_hash@"

# After build:
nix_select_hash = "sha256-yxcNOha7Cfv2nhVpz9ZXSNKk0R7wt4AiBklJ8D24rVg="  # pragma: allowlist secret
```

1. **Runtime**: Python uses baked hash to construct references

**Important**: The `--replace-fail` flag ensures the build fails if the placeholder isn't found, catching configuration errors early.

---

## Integration Checklist for Future Development

When implementing nix-select in arda-cli or arda-core:

### For Python-Nix Integration

- [ ] Add hash baking to package build (`substituteInPlace` with `@nix_select_hash@`)
- [ ] Extract hash using `jq` from `flake.lock`
- [ ] Pass `@nix_select_hash@` to Python via placeholder
- [ ] Create nix-select symlink in Python site-packages
- [ ] Test that Python can construct correct flake references
- [ ] Verify narHash is properly baked in

### For Nix Expression Usage

- [ ] Import nix-select: `let selectLib = import "${nix-select}/select.nix"; in ...`
- [ ] Use `selectLib.select` function
- [ ] Prefer wildcards over hardcoded paths
- [ ] Use maybe operator (`?`) for optional access
- [ ] Document selector patterns clearly

### For Testing

- [ ] Export `sourceWithTests` via `passthru` if VM tests planned
- [ ] Ensure symlinks available in test environment
- [ ] Verify hash baking works in test builds
- [ ] Test selectors against actual data structures

### For Future VM Testing

- [ ] Implement `sourceWithoutTests` for production
- [ ] Implement `sourceWithTests` for tests
- [ ] Use `nixFilter` to exclude test files from production
- [ ] Export `sourceWithTests` via `passthru.sourceWithTests`
- [ ] Document how tests should use the source

---

## References

### Source Code

- **nix-select repository**: <https://git.clan.lol/clan/nix-select>
- **clan-core integration**: `/pkgs/clan-cli/clan_lib/select/`
- **clan-cli hashing**: `/pkgs/clan-cli/default.nix` (lines 76-95)
- **arda-core integration**: `/pkgs/arda-cli/default.nix` (ardaSource function)

### Documentation Files

- **Previous research**: `bmad-docs/research-clan-nix-interactions.md`
- **Architecture**: `bmad-docs/architecture-clan-cli.md`

### Nix Documentation

- [Nix Flakes](https://nixos.org/manual/nix/stable/command-ref/new-cli/nix3-flake.html)
- [builtins.getFlake](https://nixos.org/manual/nix/stable/language/builtins.html#builtins.getFlake)
- [Nix langauge](https://nixos.org/manual/nix/stable/language/)

---

## Conclusion

nix-select is a critical building block for arda-core and arda-cli. It provides:

1. **Unified query interface** for complex Nix data structures
2. **Battle-tested patterns** from the clan project
3. **Hash baking** for Python-Nix integration
4. **Scalability** for dynamic, evolving systems
5. **Type safety** through Nix's attribute checking

**For arda-cli**: Essential for building an imperative CLI that can navigate and manipulate declarative NixOS configurations efficiently.

**For arda-core**: Enables sophisticated flake querying, configuration discovery, and dynamic system introspection.

**Future work**: Building the actual Nix helper library for arda-cli that leverages nix-select for all Nix operations.

---

*This document should be updated as nix-select integration evolves in the arda project.*
