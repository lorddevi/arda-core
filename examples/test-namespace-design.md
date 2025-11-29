# Test Discovery via Nix Namespace - Design Examples

## Option 1: Tests as Individual Flake Outputs (Recommended)

### Structure in flake.nix

```nix
{
  # In our project flake.nix
  {
    perSystem = { system, pkgs, ... }: {
      # Each test is a separate flake output!
      # List with: nix flake show --allow-string-ids
      checks."test-unit-config-parse-toml" = import ./pkgs/arda-cli/arda_cli/tests/unit/config/test-parse-toml.nix { inherit pkgs; };
      checks."test-unit-config-missing-file" = import ./pkgs/arda-cli/arda_cli/tests/unit/config/test-missing-file.nix { inherit pkgs; };
      checks."test-unit-theme-color-mapping" = import ./pkgs/arda-cli/arda_cli/tests/unit/themes/test-color-mapping.nix { inherit pkgs; };
      checks."test-unit-nix-helpers" = import ./pkgs/arda-cli/arda_lib/tests/unit/test-nix-helpers.nix { inherit pkgs; };
      checks."test-integration-config-workflow" = import ./pkgs/arda-cli/arda_cli/tests/integration/test-config-workflow.nix { inherit pkgs; };

      # Test runners (for convenience)
      tests.run-unit = pkgs.runCommand "run-unit-tests" { } ''
        pytest pkgs/arda-cli/arda_cli/tests/unit/ -m unit
        touch $out
      '';

      tests.run-themes = pkgs.runCommand "run-theme-tests" { } ''
        pytest pkgs/arda-cli/arda_cli/tests/ -m theme
        touch $out
      '';

      tests.run-all-fast = pkgs.runCommand "run-all-fast-tests" { } ''
        pytest pkgs/arda-cli/arda_cli/tests/ pkgs/arda-cli/arda_lib/tests/ -m "fast"
        touch $out
      '';
    };
  }
}
```

### Usage Examples

```bash
# List all tests
nix flake show --allow-string-ids | grep "checks/"

# Run a specific test
nix build .#checks.x86_64-linux.test-unit-config-parse-toml

# Run all unit tests
nix build .#tests.x86_64-linux.run-unit

# Run theme tests
nix build .#tests.x86_64-linux.run-themes

# Run all fast tests
nix build .#tests.x86_64-linux.run-all-fast

# Query test info
nix eval .#checks.x86_64-linux.test-unit-config-parse-toml.meta
```

---

## Option 2: Organized Test Namespace

### Flake Output Structure

```nix
{
  perSystem = { system, pkgs, lib, ... }: let
    # Define test categories
    testCategories = {
      unit = {
        config = [
          "test-unit-config-parse-toml"
          "test-unit-config-missing-file"
          "test-unit-config-env-vars"
        ];
        themes = [
          "test-unit-theme-color-mapping"
          "test-unit-theme-validation"
        ];
        nix = [
          "test-unit-nix-eval"
          "test-unit-nix-build"
        ];
      };
      integration = [
        "test-integration-config-workflow"
        "test-integration-theme-preview"
      ];
      vm = [
        "test-vm-user-workflow"
        "test-vm-nix-integration"
      ];
    };

    # Create derivations for each test
    createTestDerivation = name: import ./pkgs/arda-cli/arda_cli/tests/unit/config/${name}.nix { inherit pkgs; };

    # Flatten to one namespace
    allTests = lib.flatten (lib.mapAttrsToList (category: tests:
      lib.mapAttrsToList (subcategory: testNames:
        lib.listToAttrs (map (name: lib.nameValuePair name (createTestDerivation name)) testNames)
      ) tests
    ) testCategories);

    # Convert to attrs for flake output
    checks = lib.listToAttrs allTests;

    # Convenience runners
    testRunners = {
      unit = pkgs.runCommand "run-unit" { } ''pytest -m unit; touch $out'';
      integration = pkgs.runCommand "run-integration" { } ''pytest -m integration; touch $out'';
      themes = pkgs.runCommand "run-themes" { } ''pytest -m theme; touch $out'';
      all-fast = pkgs.runCommand "run-all-fast" { } ''pytest -m fast; touch $out'';
    };
  in
  {
    # Exports
    inherit checks testRunners;

    # Test registry for discovery
    testRegistry = {
      categories = lib.attrNames testCategories;
      totalTests = lib.length allTests;
      byCategory = testCategories;
    };
  };
}
```

### Usage

```bash
# See test registry
nix eval .#testRegistry

# List all unit tests
nix eval .#testRegistry.byCategory.unit

# Run specific category
nix build .#testRunners.themes

# Run all integration tests
nix build .#testRunners.integration
```

---

## Option 3: Auto-Discovery Pattern

### Central Test Registry

```nix
# In flake.nix
let
  # Auto-discover all test files
  findTests = dir: lib.filterAttrs (name: _: lib.hasPrefix "test-" name) (
    lib.mapAttrs' (name: value:
      lib.nameValuePair name (import (dir + "/${name}.nix"))
    ) (builtins.readDir dir)
  );
in
{
  perSystem = { system, pkgs, ... }: {
    # Auto-discover and import all tests
    checks = lib.mergeAttrsList [
      (findTests ./pkgs/arda-cli/arda_cli/tests/unit/config/)
      (findTests ./pkgs/arda-cli/arda_cli/tests/unit/themes/)
      (findTests ./pkgs/arda-cli/arda_lib/tests/unit/)
    ];
  };
}
```

### Usage (Auto-Discovery)

```bash
# Discover all tests automatically
nix flake show --allow-string-ids | grep "checks/"

# Run all discovered tests
nix build .#

# Add new test file, it's automatically discovered!
```

---

## Recommended Approach: Hybrid (Option 2 + Convenience)

### Final Design

```nix
{
  perSystem = { system, pkgs, lib, ... }: let
    # 1. Individual test derivations (discoverable)
    individualTests = {
      # CLI tests
      "test-unit-config-parse-toml" = runTest ./pkgs/arda-cli/arda_cli/tests/unit/config/test-parse-toml.nix;
      "test-unit-theme-colors" = runTest ./pkgs/arda-cli/arda_cli/tests/unit/themes/test-colors.nix;
      "test-integration-config-workflow" = runTest ./pkgs/arda-cli/arda_cli/tests/integration/test-workflow.nix;

      # Library tests
      "test-unit-nix-eval" = runTest ./pkgs/arda-cli/arda_lib/tests/test-nix-eval.nix;
    };

    # 2. Test runners (convenience)
    testRunners = {
      unit = runTestGroup "unit" [
        "test-unit-config-parse-toml"
        "test-unit-theme-colors"
        "test-unit-nix-eval"
      ];

      integration = runTestGroup "integration" [
        "test-integration-config-workflow"
      ];

      themes = runTestGroup "themes" [
        "test-unit-theme-colors"
      ];

      # Default: fast tests
      fast = runTestGroup "fast" [
        "test-unit-config-parse-toml"
        "test-unit-theme-colors"
        "test-unit-nix-eval"
      ];

      # All tests
      all = runTestGroup "all" (lib.attrNames individualTests);
    };

    # 3. Test metadata
    testInfo = {
      total = lib.length individualTests;
      categories = [ "unit" "integration" "vm" "theme" "config" "nix" ];
      byName = individualTests;
      runners = lib.mapAttrs (name: test: test.meta) testRunners;
    };
  in
  {
    # Export for discovery
    inherit individualTests testRunners testInfo;

    # Also export as checks (standard pattern)
    checks = individualTests // testRunners;
  };
}
```

### Usage Examples

```bash
# Discover what's available
nix flake show

# Run specific test
nix build .#individualTests.x86_64-linux.test-unit-config-parse-toml

# Run test category
nix build .#testRunners.x86_64-linux.themes

# Query test info
nix eval .#testInfo

# See test categories
nix eval .#testInfo.categories

# Count tests
nix eval .#testInfo.total

# List all test names
nix eval .#testInfo.byName | jq 'keys'

# Run all tests in a category
nix build .#testRunners.x86_64-linux.unit

# CI: Run fast tests
nix build .#testRunners.x86_64-linux.fast
```

---

## Benefits of This Approach

1. **Discoverable**: `nix flake show` lists all tests
2. **Selectable**: Run individual tests or groups
3. **Composable**: Tests are Nix derivations (can be used anywhere)
4. **Queryable**: Get test metadata via `nix eval`
5. **Organized**: Categories make it easy to find tests
6. **Scalable**: Auto-discovery possible
7. **Standard**: Uses Nix flake patterns (familiar to Nix users)

---

## Integration with Orchestration

```bash
# Direct Nix commands (powerful)
nix build .#testRunners.x86_64-linux.themes

# Or with our script wrapper
nix run .#run-arda-tests themes

# Both work! Choose your preference.
```
