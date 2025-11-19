{ inputs }:

# Modular Python 3 overlays - Central Import Hub
# This file aggregates all Python 3 package overlays

let
  # Import all individual overlays
  rich-click = import ./rich-click.nix { inherit inputs; };
in
# Merge all overlays together using the self: super: pattern
self: super:
  rich-click self super
