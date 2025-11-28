{ pkgs }:

# Simple VM smoke test for arda-core
# This test verifies that VM testing infrastructure works

{
  arda-vm-smoke-test = pkgs.vmTest.makeTest {
    name = "arda-vm-smoke-test";

    # Simple single-machine test
    machine = { config, pkgs, ... }: {
      # Enable testing tools
      environment.systemPackages = [
        pkgs.bash
        pkgs.coreutils
      ];

      # Simple test script
      testScript = ''
        print("VM started successfully!")

        # Test basic commands work
        machine.succeed("echo 'Testing VM' > /tmp/test.txt")
        machine.succeed("test -f /tmp/test.txt")

        # Verify bash is available
        machine.succeed("which bash")

        # Test file operations
        machine.succeed("mkdir -p /tmp/arda-test")
        machine.succeed("echo 'VM Test OK' > /tmp/arda-test/status")

        # Read back and verify
        result = machine.succeed("cat /tmp/arda-test/status")
        assert "VM Test OK" in result

        print("✓ All VM tests passed!")
      '';
    };
  };

  # Alternative: Container-based test (more reliable in some environments)
  arda-container-test = pkgs.runCommand "arda-container-test"
    {
      buildInputs = [
        pkgs.bash
        pkgs.coreutils
      ];
    }
    ''
      echo "Testing container-based test environment..."

      # Test bash
      bash --version | head -1

      # Test file operations
      echo "Container Test OK" > /tmp/arda-status
      cat /tmp/arda-status

      # Verify
      if [ -f /tmp/arda-status ]; then
        echo "✓ Container test passed!"
        touch $out
      else
        echo "✗ Container test failed!"
        exit 1
      fi
    '';
}
