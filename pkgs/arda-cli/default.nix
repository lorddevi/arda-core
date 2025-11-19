{
  lib,
  buildPythonApplication,
  setuptools,
  click,
  pyyaml,
  rich,
  pydantic,
  rich-click,
}:

buildPythonApplication {
  pname = "arda-cli";
  version = "0.1.0";
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
