{ inputs, ... }:

final: prev: {
  # Override Python packages
  python313Packages = prev.python313Packages.override {
    # Import all Python 3 overlays via the central hub
    # python3/default.nix merges all overlays into one function
    overrides = (import ./python3/default.nix { inherit inputs; });
  };
}
