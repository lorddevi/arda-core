{ pkgs, lib, ... }:
{
  # Bash utility for setting up isolated Nix store in test environment
  # Based on clan-core's setupNixInNix pattern
  setupNixInNix = ''
    set -xeu -o pipefail
    export HOME=$TMPDIR
    export NIX_STATE_DIR=$TMPDIR/nix
    export NIX_CONF_DIR=$TMPDIR/etc
    export IN_NIX_SANDBOX=1
    export ARDA_TEST_STORE=$TMPDIR/store
    # Required to prevent concurrent 'nix flake lock' operations
    export LOCK_NIX=$TMPDIR/nix_lock
    mkdir -p "$ARDA_TEST_STORE/nix/store"
    mkdir -p "$ARDA_TEST_STORE/nix/var/nix/gcroots"

    # Copy pre-built closures if closureInfo is provided
    if [[ -n "''${closureInfo-}" ]]; then
      ${pkgs.findutils}/bin/xargs -r -P"$(nproc)" ${pkgs.coreutils}/bin/cp \
        --recursive --no-dereference --reflink=auto \
        --target-directory "$ARDA_TEST_STORE/nix/store" \
        < "$closureInfo/store-paths"
      ${pkgs.nix}/bin/nix-store --load-db --store "$ARDA_TEST_STORE" \
        < "$closureInfo/registration"
    fi
  '';

  # NixOS test library for Python integration
  # Provides setup_nix_in_nix() function for test scripts
  nixosTestLib = pkgs.python313Packages.buildPythonPackage {
    pname = "nixos-test-lib";
    version = "1.0.0";
    format = "pyproject";
    src = lib.fileset.toSource {
      root = ./.;
      fileset = lib.fileset.unions [
        ./pyproject.toml
        ./nixos_test_lib
      ];
    };
    nativeBuildInputs = with pkgs.python313Packages; [
      setuptools
      wheel
    ];
    postPatch = ''
      substituteInPlace nixos_test_lib/nix_setup.py \
        --replace '@cp@' '${pkgs.coreutils}/bin/cp' \
        --replace '@nix-store@' '${pkgs.nix}/bin/nix-store' \
        --replace '@xargs@' '${pkgs.findutils}/bin/xargs'
    '';
    doCheck = false;
  };
}
