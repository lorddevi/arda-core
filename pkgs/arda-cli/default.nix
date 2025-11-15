{ lib, python3, ... }:
let
  # Python dependencies for arda-cli
  pythonRuntime = python3;
  pyDeps =
    ps: with ps; [
      click
      pyyaml
      rich
      pydantic
    ];
  pythonRuntimeWithDeps = pythonRuntime.withPackages pyDeps;
in
pythonRuntime.pkgs.buildPythonApplication {
  name = "arda-cli";
  src = ./.;
  format = "pyproject";

  nativeBuildInputs = [
    (pythonRuntime.withPackages (ps: [ ps.hatchling ]))
  ];

  propagatedBuildInputs = [ pythonRuntimeWithDeps ];

  meta = {
    description = "Arda - minimal infrastructure management for NixOS";
    homepage = "https://github.com/lorddevi/arda-core";
    license = lib.licenses.mit;
  };
}
