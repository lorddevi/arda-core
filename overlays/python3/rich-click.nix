{ inputs }:

self: super: {
  # Override rich-click to version 1.9.4 (has theming support)
  # Theming was added in 1.9.0, but Nixpkgs has 1.8.9
  rich-click = super.rich-click.overrideAttrs (old: {
    version = "1.9.4";
    src = inputs.rich-click;
  });
}
