{ pkgs, lib }:

let
  # Function to run tests for a specific directory
  runTests = dir: pkgs.runCommand "run-tests-${lib.strings.replaceStrings ["/"] ["_"] (toString dir)}"
    {
      nativeBuildInputs = [ pkgs.python313Packages.pytest ];
    } ''
      cd ${dir}
      pytest -m "fast" -n auto --tb=short -v
      touch $out
    '';

  # Function to create a test group runner
  runTestGroup = name: testPaths:
    let
      pathList = lib.concatStringsSep " " testPaths;
    in
    pkgs.runCommand "run-test-group-${name}"
      {
        nativeBuildInputs = [ pkgs.python313Packages.pytest ];
      }
      ''
        pytest ${pathList} -m "fast" -n auto --tb=short -v
        touch $out
      '';

  # Function to run a specific test category
  runCategory = category: pkgs.runCommand "run-category-${category}"
    {
      nativeBuildInputs = [ pkgs.python313Packages.pytest ];
    }
    ''
      pytest -m "${category}" -n auto --tb=short -v
      touch $out
    '';
in
{
  runTests = runTests;
  runTestGroup = runTestGroup;
  runCategory = runCategory;
  runAllFast = runCategory "fast";
  runAllUnit = runCategory "unit";
  runAllIntegration = runCategory "integration";
}
