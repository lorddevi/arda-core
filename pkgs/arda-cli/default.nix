{ lib
, python
, setuptools
, click
, pyyaml
, rich
, pydantic
, rich-click
}:

python.pkgs.buildPythonApplication {
  pname = "arda_cli";
  version = "0.1.3";
  src = ./.;
  format = "pyproject";


  nativeBuildInputs = [ setuptools ];

  propagatedBuildInputs = [
    click
    pyyaml
    rich
    pydantic
    rich-click
  ];

  meta = {
    description = "Arda - minimal infrastructure management for NixOS";
    homepage = "https://github.com/lorddevi/arda-core";
    license = lib.licenses.mit;
  };
}
