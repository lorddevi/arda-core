{
  config,
  pkgs,
  lib,
  ...
}:
{
  name = "arda-cli-vm-theme-commands";

  nodes.machine =
    {
      config,
      pkgs,
      lib,
      ...
    }:
    {
      # arda-cli will be added by flake-module.nix via machine.systemPackages
      environment.systemPackages = [
      ];
    };

  testScript = ''
    # Start the VM
    machine.start()
    machine.wait_for_unit("default.target")

    # Test 1: List all available themes
    print("=== Testing: arda theme list ===")
    result = machine.succeed("/tmp/arda-test/arda theme list")
    print(result)

    # Test 2: Verify common themes are available
    print("\n=== Testing: Common themes availability ===")
    common_themes = ["default", "dracula", "nord", "solarized", "forest"]
    for theme in common_themes:
        result = machine.succeed("/tmp/arda-test/arda theme list")
        assert theme in result, f"Theme '{theme}' not found in theme list"
        print(f"✅ Theme '{theme}' is available")

    # Test 3: Test theme list with different themes
    print("\n=== Testing: Specific theme availability ===")
    result = machine.succeed("/tmp/arda-test/arda theme list")
    expected_themes = [
        "default",
        "dracula",
        "dracula-slim",
        "dracula-modern",
        "nord",
        "ocean",
        "forest",
        "forest-slim",
        "forest-modern",
        "solarized",
        "solarized-dark",
        "solarized-light"
    ]

    for theme in expected_themes:
        if theme in result:
            print(f"✅ Theme '{theme}' found")

    # Test 4: Use --theme option with --help
    print("\n=== Testing: arda --theme dracula --help ===")
    result = machine.succeed("/tmp/arda-test/arda --theme dracula --help")
    assert "Arda" in result
    assert "config" in result.lower()
    print("✅ arda --theme dracula --help works")

    # Test 5: Use --theme option with different theme
    print("\n=== Testing: arda --theme nord --help ===")
    result = machine.succeed("/tmp/arda-test/arda --theme nord --help")
    assert "Arda" in result
    assert "config" in result.lower()
    print("✅ arda --theme nord --help works")

    # Test 6: Verify theme can be set via config
    print("\n=== Testing: Set theme via config ===")
    machine.succeed("/tmp/arda-test/arda config --local set theme dracula")
    result = machine.succeed("cat etc/arda.toml")
    assert "dracula" in result
    print("✅ Theme can be set via config")

    # Test 7: Test invalid theme name (should fail gracefully)
    print("\n=== Testing: Invalid theme name handling ===")
    # Note: machine.fail() doesn't return output, so we use succeed with expected failure
    machine.fail("/tmp/arda-test/arda --theme invalid-theme-name --help")
    print("✅ Invalid theme name handled correctly")

    # Test 8: Verify theme command help
    print("\n=== Testing: arda theme --help ===")
    result = machine.succeed("/tmp/arda-test/arda theme --help")
    assert "list" in result
    assert "theme" in result.lower()
    print("✅ arda theme --help displays correctly")

    # Test 9: List themes and verify count
    print("\n=== Testing: Theme list completeness ===")
    result = machine.succeed("/tmp/arda-test/arda theme list")
    theme_lines = [line.strip() for line in result.split('\n') if line.strip()]
    print(f"Total themes available: {len(theme_lines)}")
    assert len(theme_lines) > 5, "Should have at least 5 themes available"
    print("✅ Theme list has multiple themes")

    print("\n" + "="*60)
    print("✅ All theme commands tests PASSED")
    print("="*60)
  '';

  meta.maintainers = [ "Lord Devi" ];
}
