# Custom Nix Namespace for arda-core Tests

## Yes! Custom Namespaces Are Fully Supported

Nix flake outputs support **completely custom namespaces**. You're not limited to standard outputs like `packages`, `checks`, etc.

### Your Proposed Namespace Structure

```nix
{
  # In flake.nix
  perSystem = { system, pkgs, lib, ... }: {
    # Custom namespace starting with "arda"
    # Full hierarchy: arda.tests.{category}.{test-name}
    arda = {
      # Main test namespace
      tests = {
        # By component
        "clan-cli.unit" = runTests ./pkgs/arda-cli/arda_cli/tests/unit/;
        "clan-cli.integration" = runTests ./pkgs/arda-cli/arda_cli/tests/integration/;
        "clan-cli.cli-commands" = runTests ./pkgs/arda-cli/arda_cli/tests/cli/;

        "clan_lib.unit" = runTests ./pkgs/arda-cli/arda_lib/tests/unit/;
        "clan_lib.nix" = runTests ./pkgs/arda-cli/arda_lib/tests/nix/;

        # By feature
        "themes.unit" = runThemeTests;
        "config.unit" = runConfigTests;
        "nix.helpers" = runNixTests;

        # Individual tests
        "test.config.parse-toml" = createTest ./pkgs/arda-cli/arda_cli/tests/unit/config/test-parse-toml.nix;
        "test.config.missing-file" = createTest ./pkgs/arda-cli/arda_cli/tests/unit/config/test-missing-file.nix;
        "test.themes.color-mapping" = createTest ./pkgs/arda-cli/arda_cli/tests/unit/themes/test-color-mapping.nix;
      };

      # Other custom outputs
      helpers = {
        run-tests = createRunner ./pkgs/testing/run-tests.nix;
      };

      # Metadata
      info = {
        totalTests = 42;
        categories = [ "clan-cli.unit" "clan_cli.unit" "themes.unit" ];
        byComponent = {
          clan-cli = [ "unit" "integration" "cli-commands" ];
          clan-lib = [ "unit" "nix" ];
        };
      };
    };
  };
}
```

### Discovery - This Is Where It Gets Good

```bash
# Show ALL outputs (including custom)
nix flake show

# Output will show:
# ├───arda
# │   ├───tests
# │   │   ├───clan-cli.unit
# │   │   ├───clan-cli.integration
# │   │   ├───clan_lib.unit
# │   │   ├───themes.unit
# │   │   └───test.config.parse-toml
# │   ├───helpers
# │   │   └───run-tests
# │   └───info

# Query the arda namespace
nix eval .#arda

# List all test categories
nix eval .#arda.info.categories

# See component breakdown
nix eval .#arda.info.byComponent

# Count tests
nix eval .#arda.info.totalTests

# List all test names under tests namespace
nix eval .#arda.tests | jq 'keys'

# Example output:
# [
#   "clan-cli.unit",
#   "clan-cli.integration",
#   "clan_cli.unit",
#   "themes.unit",
#   "test.config.parse-toml",
#   "test.config.missing-file"
# ]
```

### Running Tests - Multiple Ways

```bash
# Run all tests for a component
nix build .#arda.tests."clan-cli.unit"

# Run all tests for a feature
nix build .#arda.tests.themes.unit

# Run a specific test
nix build .#arda.tests."test.config.parse-toml"

# Run using helpers
nix run .#arda.helpers.run-tests -- themes

# Or combine with wildcard patterns (using jq)
nix eval .#arda.tests | jq -r 'keys[] | select(startswith("clan-cli"))' | while read test; do
  nix build .#arda.tests.$test
done
```

### Namespace Rules and Conventions

#### Valid Patterns

```nix
# Dots create hierarchy (nested attribute sets)
arda.tests.clan-cli.unit
arda.tests.clan_lib.unit
arda.info.totalTests

# Dashes and underscores are valid in names
arda.tests.clan-cli.unit       ✓ (dash in name)
arda.tests.clan_cli.unit       ✓ (underscore in name)
arda.tests.clan_cli_unit       ✓ (underscore in name)

# Numbers are fine
arda.tests.config-v2.unit

# Avoid spaces and special chars
arda.tests.config unit         ✗ (space)
arda.tests.config@unit         ✗ (@ symbol in name)
```

#### Recommended Convention

```nix
# Structure: arda.{category}.{subcategory}.{name}

arda.tests.component.category
  arda.tests.clan-cli.unit
  arda.tests.clan_lib.nix

arda.helpers.util-name
  arda.helpers.run-tests
  arda.helpers.test-fixtures

arda.info.metadata-name
  arda.info.totalTests
  arda.info.categories

arda.apps.app-name
  arda.apps.arda-cli
  arda.apps.run-tests
```

### Make It Discoverable via Tab Completion

```bash
# Enable flake completion in bash
# Add to ~/.bashrc or ~/.zshrc:
complete -F _nix nix

# Then tab-complete through the hierarchy
nix build .#arda.    # Tab shows: tests, helpers, info
nix build .#arda.tests.    # Tab shows: clan-cli.unit, clan_lib.unit, etc.

# Or use zsh with nix-zsh-completions plugin
```

### Example: Query Test Inventory

```bash
# How many tests do we have?
nix eval .#arda.info.totalTests
# Output: 42

# What components have tests?
nix eval .#arda.info.byComponent
# Output:
# {
#   "clan-cli": [ "unit", "integration", "cli-commands" ],
#   "clan-lib": [ "unit", "nix" ]
# }

# List all unit tests
nix eval .#arda.tests | jq -r 'keys[] | select(endswith(".unit"))'
# Output:
# clan-cli.unit
# clan_lib.unit
# themes.unit

# Run all unit tests
for test in $(nix eval .#arda.tests | jq -r 'keys[] | select(endswith(".unit"))'); do
  echo "Running $test..."
  nix build .#arda.tests.$test
done
```

### Integration with Justfile

```justfile
# Justfile can reference the namespace
test-unit:
    nix build .#arda.tests.clan-cli.unit

test-themes:
    nix build .#arda.tests.themes.unit

test-all-unit:
    nix eval .#arda.tests | jq -r 'keys[] | select(endswith(".unit"))' | while read test; do
        nix build .#arda.tests.$$test
    end

test-list:
    @nix eval .#arda.tests | jq -r 'keys[]'

test-count:
    @nix eval .#arda.info.totalTests
```

### Query Any Attribute

```bash
# List everything under arda
nix eval .#arda | jq 'keys'

# See all test names
nix eval .#arda.tests | jq 'keys'

# Get metadata for a specific test
nix eval .#arda.tests."clan-cli.unit".meta

# Filter tests by pattern
nix eval .#arda.tests | jq -r 'keys[] | select(startswith("clan-cli"))'

# Count tests by component
nix eval .#arda.info.byComponent | jq '.["clan-cli"] | length'
```

---

## Summary

**Yes! Your namespace idea is perfect and fully supported.**

✅ **Custom namespaces work**: `arda.tests.XXX` is valid
✅ **Discoverable**: `nix flake show` reveals everything
✅ **Queryable**: `nix eval .#arda.tests` shows all tests
✅ **Hierarchical**: Use dots for structure, dashes for names
✅ **No limits**: Create any custom outputs you want
✅ **Tab-completable**: Bash/zsh completion works
✅ **Scriptable**: Parse with `jq`, loop with bash

**Recommended structure for arda-core:**

- `arda.tests.{component}.{category}` - Test groups
- `arda.helpers.{name}` - Helper utilities
- `arda.info.{metadata}` - Information about tests
- `arda.apps.{name}` - CLI applications
