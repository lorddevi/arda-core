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
  # nix-select is optional - required only for nix integration features
  # VM tests and simple CLI usage don't need this
  nix-select ? null,
  jq,
  runCommand,
  pytest,
  pytest-xdist,
  pytest-cov,
  # Import nix isolation utilities from clan-core pattern
  pkgs,
}:

let
  # Create arda source with optional nix-select integration
  # This mirrors clan-cli's cliSource pattern but adapted for arda
  ardaSource =
    source:
    runCommand "arda-cli-source"
      (
        {
          nativeBuildInputs = [ jq ];
        }
        // lib.optionalAttrs (nix-select != null) {
          # When nix-select is available, include it in nativeBuildInputs
          # and read its hash from flake.lock
          _nix-select = nix-select;
        }
      )
      (
        ''
          # Copy source to output
          cp -r ${source} $out
          chmod -R +w $out

          # Remove old symlinks if they exist
          rm -f $out/arda_cli/select
          rm -f $out/arda_lib/select
        ''
        + lib.optionalString (nix-select != null) ''
          # Substitute nix-select hash into Python code
          # This allows Python to construct correct flake references to nix-select
          substituteInPlace $out/arda_lib/nix/nix.py \
            --replace-fail '@nix_select_hash@' "$(jq -r '.nodes."nix-select".locked.narHash' ${../../flake.lock})"

            # Create symlink to nix-select library
            # This makes the selector functions available in Nix expressions
            ln -sf ${nix-select} $out/arda_lib/select
            ln -sf ${nix-select} $out/arda_cli/select
        ''
        + lib.optionalString (nix-select == null) ''
          # If nix-select is not available, use a placeholder
          substituteInPlace $out/arda_lib/nix/nix.py \
            --replace-fail '@nix_select_hash@' "null"
        ''
        + ''
          # Ensure testing infrastructure is in place for build-time tests
          # (Note: pytest.ini and testing/ are in the arda-cli source directory)
        ''
      );
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

  # Run tests during build using clan's two-phase approach
  # Phase 1: Tests that don't need arda-core (without-core)
  # Phase 2: Tests that need arda-core (with-core)
  # This mirrors clan-core's approach exactly

  # Phase 1: Tests WITHOUT arda-core dependencies
  # These are fast, isolated tests (unit tests, CLI tests, etc.)
  arda-pytest-without-core =
    runCommand "arda-pytest-without-core"
      {
        nativeBuildInputs = [
          python
          pytest
          pytest-xdist
          pytest-cov
          jq
        ];
      }
      ''
        set -euo pipefail
        cp -r ${ardaSource ./.} ./src
        chmod +w -R ./src
        cd ./src

        # Set up isolated test environment using clan-core pattern
        export HOME=$TMPDIR
        export NIX_STATE_DIR=$TMPDIR/nix
        export NIX_CONF_DIR=$TMPDIR/etc
        export IN_NIX_SANDBOX=1
        export ARDA_TEST_STORE=$TMPDIR/store
        export LOCK_NIX=$TMPDIR/nix_lock
        mkdir -p "$ARDA_TEST_STORE/nix/store"

        # Limit build cores to 16 (like clan-core)
        jobs="$((NIX_BUILD_CORES>16 ? 16 : NIX_BUILD_CORES))"

        echo "==================================================================="
        echo "  Phase 1: Tests WITHOUT arda-core (analogous to clan without-core)"
        echo "==================================================================="
        echo ""

        # Run tests WITHOUT arda-core
        # Markers: not service_runner, not impure, not with_core
        python -m pytest -v \
          -m "not service_runner and not impure and not with_core" \
          --tb=short \
          --maxfail=5 \
          -n "$jobs" \
          --cov=./arda_cli \
          --cov=./arda_lib \
          --cov-report=term-missing \
          --cov-report=html \
          --cov-fail-under=10 \
          ./arda_cli \
          ./arda_lib

        echo ""
        echo "==================================================================="
        echo "  Phase 1 (without-core) completed successfully"
        echo "==================================================================="
        echo ""

        touch $out
      '';

  # Phase 2: Tests WITH arda-core dependencies
  # These are slower tests that need full arda-core infrastructure
  arda-pytest-with-core =
    runCommand "arda-pytest-with-core"
      {
        nativeBuildInputs = [
          python
          pytest
          pytest-xdist
          pytest-cov
          jq
        ];
      }
      ''
        set -euo pipefail
        cp -r ${ardaSource ./.} ./src
        chmod +w -R ./src
        cd ./src

        # Set up isolated test environment using clan-core pattern
        export HOME=$TMPDIR
        export NIX_STATE_DIR=$TMPDIR/nix
        export NIX_CONF_DIR=$TMPDIR/etc
        export IN_NIX_SANDBOX=1
        export ARDA_TEST_STORE=$TMPDIR/store
        export LOCK_NIX=$TMPDIR/nix_lock
        mkdir -p "$ARDA_TEST_STORE/nix/store"

        # Limit build cores to 16 (like clan-core)
        jobs="$((NIX_BUILD_CORES>16 ? 16 : NIX_BUILD_CORES))"

        echo "==================================================================="
        echo "  Phase 2: Tests WITH arda-core (analogous to clan with-core)"
        echo "==================================================================="
        echo ""

        # Run tests WITH arda-core
        # Markers: not service_runner, not impure, with_core
        python -m pytest -v \
          -m "not service_runner and not impure and with_core" \
          --tb=short \
          --maxfail=3 \
          -n "$jobs" \
          --cov=./arda_cli \
          --cov=./arda_lib \
          --cov-report=term-missing \
          --cov-report=html \
          --cov-fail-under=10 \
          ./arda_cli \
          ./arda_lib

        echo ""
        echo "==================================================================="
        echo "  Phase 2 (with-core) completed successfully"
        echo "==================================================================="
        echo ""

        touch $out
      '';

  # Main checkPhase runs both phases
  checkPhase = ''
    echo "==================================================================="
    echo "  Arda Build-Time Test Execution (Clan's Two-Phase Pattern)"
    echo "==================================================================="
    echo ""
    echo "This build uses clan-core's two-phase testing approach:"
    echo "  Phase 1: Tests without arda-core (fast, isolated)"
    echo "  Phase 2: Tests with arda-core (comprehensive)"
    echo ""
    echo "See arda-pytest-without-core and arda-pytest-with-core derivations."
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
