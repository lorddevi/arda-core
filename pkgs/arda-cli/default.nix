{ lib
, python
, setuptools
, click
, pyyaml
, rich
, pydantic
, rich-click
, tomli-w
, nix-select
}:

python.pkgs.buildPythonApplication {
  pname = "arda_cli";
  version = "0.1.5";
  src = ./.;
  format = "pyproject";

  nativeBuildInputs = [ setuptools ];

  propagatedBuildInputs = [
    click
    pyyaml
    rich
    pydantic
    rich-click
    tomli-w
  ];

  postInstall = ''
    # Create symlink to nix-select library (like clan-cli does)
    # This makes the selector functions available to Python via import
    mkdir -p $out/${python.sitePackages}/arda_cli
    ln -sf ${nix-select} $out/${python.sitePackages}/arda_cli/select
  '';

  meta = {
    description = "Arda - minimal infrastructure management for NixOS";
    homepage = "https://github.com/lorddevi/arda-core";
    license = lib.licenses.mit;
  };
}
