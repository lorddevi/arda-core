{ lib, python, ... }:
let
  # Python dependencies for arda-cli
  pythonRuntime = python;
  pyDeps =
    ps: with ps; [
      click
      pyyaml
      rich
      pydantic
      rich-click
    ];
  pythonRuntimeWithDeps = pythonRuntime.withPackages pyDeps;
in
pythonRuntime.pkgs.buildPythonApplication {
  name = "arda-cli";
  src = ./.;
  pyproject = true;
  build-system = [ pythonRuntime.pkgs.setuptools ];

  nativeBuildInputs = [
    (pythonRuntime.withPackages (ps: [ ps.setuptools ]))
  ];

  propagatedBuildInputs = [ pythonRuntimeWithDeps ];

  meta = {
    description = "Arda - minimal infrastructure management for NixOS";
    homepage = "https://github.com/lorddevi/arda-core";
    license = lib.licenses.mit;
  };
}
