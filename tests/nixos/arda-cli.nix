{ pkgs }:
# Package the built arda-cli for use in VM tests
pkgs.callPackage ../../pkgs/arda-cli/default.nix { }
