{ lib
, python
, setuptools
, click
, pyyaml
, rich
, pydantic
, rich-click
, tomli-w
, nix-select
, jq
, runCommand
, pytest
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

  # Add pytest for build-time testing
  checkInputs = [ pytest ];

  propagatedBuildInputs = [
    click
    pyyaml
    rich
    pydantic
    rich-click
    tomli-w
  ];

  # Run tests during build (Phase 1.4)
  # Execute fast unit tests to verify code quality
  installCheckPhase = ''
    echo "Running Phase 1.4: Build-time test execution"
    echo "=============================================="
    echo ""

    # Run pytest with fast marker to execute only quick unit tests
    # Tests are in the source directory, not in the package
    # The build removes tests after packaging (pythonRemoveTestsDir)
    echo "Running fast unit tests..."
    python -m pytest -v -m "fast" \
      ./arda_cli/tests \
      ./arda_lib/tests \
      --tb=short

    echo ""
    echo "=============================================="
    echo "Build-time tests completed successfully"
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
