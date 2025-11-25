{ lib
, python
, setuptools
, click
, pyyaml
, rich
, pydantic
, rich-click
, tomli-w
,
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

  meta = {
    description = "Arda - minimal infrastructure management for NixOS";
    homepage = "https://github.com/lorddevi/arda-core";
    license = lib.licenses.mit;
  };
}
