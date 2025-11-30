{
  pkgs,
  python313Packages,
  ...
}:

# Simple wrapper for arda-cli package for VM tests
# VM tests need the CLI binary but don't need nix-select or pytest infrastructure
python313Packages.callPackage ../../pkgs/arda-cli/default.nix {
  inherit (pkgs) jq runCommand;
  inherit (python313Packages)
    python
    setuptools
    click
    pyyaml
    rich
    pydantic
    rich-click
    tomli-w
    ;
  # VM tests don't need nix-select or pytest
  nix-select = null;
}
