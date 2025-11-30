{
  pkgs,
  vmPrebuild,
  lib,
  ...
}:

pkgs.runCommand "run-vm-tests-with-cache"
  {
    nativeBuildInputs = [
      pkgs.python313
      pkgs.nix
      pkgs.qemu_x86_64
    ];
    TEST_VM_DIR = "/tmp/vm-cache";
  }
  ''
    echo "=== Starting VM Tests with Pre-Built Cache ==="

    # Pre-built VMs available at TEST_VM_DIR
    mkdir -p $TEST_VM_DIR

    # Run each VM test using pre-built images
    for test in help config-operations config-priority themes; do
      echo ""
      echo "=== Running VM test: $test ==="
      ${lib.getAttr test vmPrebuild.prebuiltVMs}/bin/test 2>&1 | tee /tmp/vm-test-$test.log

      if [ ${PIPESTATUS [ 0 ]} -eq 0 ]; then
        echo "✅ VM test $test PASSED"
      else
        echo "❌ VM test $test FAILED"
        exit 1
      fi
    done

    echo ""
    echo "=== All VM tests PASSED with pre-built cache ==="
    touch $out
  ''
