{ makeTest }:
makeTest {
  nodes.machine =
    {
      config,
      pkgs,
      lib,
      ...
    }:
    {
      environment.systemPackages = [
        # Built arda-cli binary
        (pkgs.callPackage ../../../arda-cli.nix { })
      ];

      # Create test project directory
      test-project = lib.mkDefault {
        name = "test-project";
        owner = "test-user";
        group = "test-group";
      };
    };

  testScript = ''
    # Test 1: Main arda --help command
    print("=== Testing: arda --help ===")
    result = machine.succeed("arda --help")
    assert "Arda - minimal infrastructure management" in result
    assert "config" in result
    assert "host" in result
    assert "roles" in result
    assert "secrets" in result
    assert "templates" in result
    assert "theme" in result
    print("✅ arda --help displays correctly")

    # Test 2: arda config --help
    print("\n=== Testing: arda config --help ===")
    result = machine.succeed("arda config --help")
    assert "View and modify Arda configuration" in result
    assert "init" in result
    assert "set" in result
    assert "get" in result
    assert "--global" in result
    assert "--local" in result
    print("✅ arda config --help displays correctly")

    # Test 3: arda theme --help
    print("\n=== Testing: arda theme --help ===")
    result = machine.succeed("arda theme --help")
    assert "Theme management and preview" in result
    assert "list" in result
    print("✅ arda theme --help displays correctly")

    # Test 4: arda host --help
    print("\n=== Testing: arda host --help ===")
    result = machine.succeed("arda host --help")
    assert "Host management commands" in result
    print("✅ arda host --help displays correctly")

    # Test 5: arda roles --help
    print("\n=== Testing: arda roles --help ===")
    result = machine.succeed("arda roles --help")
    assert "Role management commands" in result
    print("✅ arda roles --help displays correctly")

    # Test 6: arda secrets --help
    print("\n=== Testing: arda secrets --help ===")
    result = machine.succeed("arda secrets --help")
    assert "Secret management commands" in result
    print("✅ arda secrets --help displays correctly")

    # Test 7: arda templates --help
    print("\n=== Testing: arda templates --help ===")
    result = machine.succeed("arda templates --help")
    assert "Template management commands" in result
    print("✅ arda templates --help displays correctly")

    # Test 8: Verify Active configuration line appears
    print("\n=== Testing: Active configuration line ===")
    result = machine.succeed("arda --help")
    assert "Active configuration:" in result
    print("✅ Active configuration line appears in help")

    # Test 9: Help with theme option
    print("\n=== Testing: arda --help with theme option ===")
    result = machine.succeed("arda --theme dracula --help")
    assert "Arda - minimal infrastructure management" in result
    print("✅ arda --theme dracula --help works")

    # Test 10: Help with verbose option
    print("\n=== Testing: arda --help with verbose option ===")
    result = machine.succeed("arda --verbose --help")
    assert "Arda - minimal infrastructure management" in result
    print("✅ arda --verbose --help works")

    print("\n" + "="*60)
    print("✅ All help output tests PASSED")
    print("="*60)
  '';

  meta.maintainers = [ "Lord Devi" ];
}
