{
  lib,
  python,
  setuptools,
  click,
  pyyaml,
  rich,
  pydantic,
  rich-click,
  tomli-w,
  nix-select,
  jq,
  runCommand,
  pytest,
  pytest-xdist,
  pytest-cov,
}:

let
  # Create arda source with nix-select integration
  # This mirrors clan-cli's cliSource pattern but adapted for arda
  ardaSource =
    source:
    runCommand "arda-cli-source"
      {
        nativeBuildInputs = [ jq ];
      }
      ''
        # Copy source to output
        cp -r ${source} $out
        chmod -R +w $out

        # Remove old symlinks if they exist
        rm -f $out/arda_cli/select
        rm -f $out/arda_lib/select

        # Substitute nix-select hash into Python code
        # This allows Python to construct correct flake references to nix-select
        substituteInPlace $out/arda_lib/nix/nix.py \
          --replace-fail '@nix_select_hash@' "$(jq -r '.nodes."nix-select".locked.narHash' ${../../flake.lock})"

        # Create symlink to nix-select library
        # This makes the selector functions available in Nix expressions
        ln -sf ${nix-select} $out/arda_lib/select
        ln -sf ${nix-select} $out/arda_cli/select

        # Ensure testing infrastructure is in place for build-time tests
        # (Note: pytest.ini and testing/ are in the arda-cli source directory)
      '';
in
python.pkgs.buildPythonApplication {
  pname = "arda_cli";
  version = "0.1.5";
  src = ardaSource ./.;
  format = "pyproject";

  nativeBuildInputs = [ setuptools ];

  # Add pytest and testing tools for build-time testing
  checkInputs = [
    pytest
    pytest-xdist # Parallel test execution (like clan)
    pytest-cov # Coverage reporting
  ];

  propagatedBuildInputs = [
    click
    pyyaml
    rich
    pydantic
    rich-click
    tomli-w
  ];

  # Run tests during build following clan's pattern
  # Tests are executed as part of nix build with proper isolation
  checkPhase = ''
    echo "==================================================================="
    echo "  Arda Build-Time Test Execution (Following Clan Pattern)"
    echo "==================================================================="
    echo ""

    # Set up isolated test environment
    export HOME=$TMPDIR
    export NIX_STATE_DIR=$TMPDIR/nix
    export IN_NIX_SANDBOX=1

    # Create test directories
    mkdir -p test-reports

    echo "Phase 1: Fast Unit Tests (without dependencies)"
    echo "------------------------------------------------"
    # Run fast unit tests (analogous to clan's "without_core")
    # These are quick tests that don't need heavy dependencies
    # Parallel execution with pytest-xdist
    jobs="$((NIX_BUILD_CORES>16 ? 16 : NIX_BUILD_CORES))"
    python -m pytest -v \
      -m "fast and not slow" \
      --tb=short \
      --maxfail=5 \
      -n "$jobs" \
      --cov=./arda_cli \
      --cov=./arda_lib \
      --cov-report=term-missing \
      --cov-report=html:test-reports/coverage-unit \
      --cov-report=xml:test-reports/coverage-unit.xml \
      --cov-fail-under=15 \
      --junitxml=test-reports/unit-tests.xml \
      ./arda_cli/tests/unit \
      ./arda_lib/tests

    echo ""
    echo "Phase 2: Integration Tests"
    echo "--------------------------"
    # Run integration tests (excluding VM tests which require libvirt)
    python -m pytest -v \
      -m "integration and not vm" \
      --tb=short \
      --maxfail=3 \
      -n "$jobs" \
      --cov=./arda_cli \
      --cov=./arda_lib \
      --cov-report=term-missing \
      --cov-report=html:test-reports/coverage-integration \
      --cov-report=xml:test-reports/coverage-integration.xml \
      --cov-fail-under=30 \
      --junitxml=test-reports/integration-tests.xml \
      ./arda_cli/tests/integration

    echo ""
    echo "==================================================================="
    echo "  Build-time tests completed successfully"
    echo "==================================================================="
    echo ""
    echo "Test Reports:"
    echo "  Unit tests:           test-reports/unit-tests.xml"
    echo "  Integration tests:    test-reports/integration-tests.xml"
    echo "  Coverage (unit):      test-reports/coverage-unit/index.html"
    echo "  Coverage (unit XML):  test-reports/coverage-unit.xml"
    echo "  Coverage (integration): test-reports/coverage-integration/index.html"
    echo "  Coverage (integration XML): test-reports/coverage-integration.xml"
    echo ""
    echo "Coverage thresholds: Phase 1=15% (unit), Phase 2=30% (integration) - Goal: 70%"
    echo ""
  '';

  # Export ardaSource for testing (passthru)
  # This allows tests to access the full source if needed
  passthru = {
    ardaSource = ardaSource ./.;
  };

  meta = {
    description = "Arda - minimal infrastructure management for NixOS";
    homepage = "https://github.com/lorddevi/arda-core";
    license = lib.licenses.mit;
  };
}
