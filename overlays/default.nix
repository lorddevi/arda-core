# Custom Nix Overlay for Arda CLI
# This overlay overrides packages from nixpkgs with newer versions

final: prev:
{
  # Override Python packages
  python313Packages = prev.python313Packages.overrideScope' (selfOverlay:
    { super, ... }:
    {
      # Override rich-click to version 1.9.4 (has theming support)
      # Theming was added in 1.9.0, but Nixpkgs has 1.8.9
      rich-click = super.rich-click.overrideAttrs (old: {
        version = "1.9.4";
        src = final.fetchFromGitHub {
          owner = "hamstergene";
          repo = "rich-click";
          rev = "v1.9.4";
          # Hash will be provided by Nix during first build
          hash = "sha256-0000000000000000000000000000000000000000000000000000=";
        };
      });
    }
  );
}
