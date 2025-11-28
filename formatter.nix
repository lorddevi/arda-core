{ inputs, ... }:
{
  imports = [ inputs.treefmt-nix.flakeModule ];
  perSystem =
    { self', pkgs, ... }:
    {
      treefmt.programs.nixfmt.enable = true;
      treefmt.programs.ruff.enable = true;
      treefmt.programs.shellcheck.enable = true;

      treefmt.settings.global.excludes = [
        "*.png"
        "*.svg"
        "package-lock.json"
        "*.jpeg"
        "*.gitignore"
        ".vscode/*"
        "*.toml"
        "*.code-workspace"
        "*.pub"
        "*.priv"
        "*.typed"
        "*.age"
        "*.desktop"
        "*.md"
        "**/node_modules/*"
        "**/.mypy_cache/*"
        ".direnv/*"
        ".envrc"
        "result"
        "result-*"
        "vm-tests/*"
      ];
    };
}
