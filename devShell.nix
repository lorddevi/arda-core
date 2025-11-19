{ pkgs, ... }:
{
  perSystem =
    { ... }:
    {
      devShells.default = pkgs.mkShell {
        name = "arda";
        pure = true;
        packages = [
          pkgs.nix
          pkgs.git
          pkgs.gh
          pkgs.age
        ];
      };
    };
}
