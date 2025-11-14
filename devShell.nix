{ ... }:
{
  perSystem =
    { pkgs, config, ... }:
    {
      devShells.default = pkgs.mkShell {
        name = "arda";
        packages = [
          pkgs.nix
          pkgs.git
          pkgs.gh
          pkgs.age
          config.treefmt.build.wrapper
        ];
        shellHook = ''
          echo "Welcome to Arda development environment"
          echo "Type 'nix fmt' to format code"
          echo "Type 'nix build' to build packages"
          echo "See README.md for more information"
        '';
      };
    };
}
