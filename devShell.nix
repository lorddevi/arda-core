{ pkgs, ... }:
{
  perSystem =
    { ... }:
    {
      devShells.default = let
        # Create a Python environment with libvirt-python for VM testing
        python-with-vm-support = pkgs.python313.withPackages (ps: [
          ps.pip
          ps.setuptools
          ps.wheel
          ps.click
          ps.pyyaml
          ps.rich
          ps.pydantic
          ps.rich-click
          ps.tomli-w
          ps.pytest
          ps.pytest-cov
          ps.ruff
          ps.mypy
          ps.bandit
          ps.detect-secrets

          # libvirt-python for VM testing (build from source since it's not in nixpkgs)
          # Users can install it with: pip install libvirt-python
        ]);
      in
      pkgs.mkShell {
        name = "arda";
        packages = [
          pkgs.nix
          pkgs.git
          pkgs.gh
          pkgs.age
          pkgs.direnv
          pkgs.coreutils
          pkgs.which
          pkgs.just

          # VM testing infrastructure
          pkgs.libvirt
          pkgs.qemu

          # Python with VM testing support
          python-with-vm-support

          # Development tools
          pkgs.pre-commit # Git hooks framework
        ];

        # PostShellHook to install libvirt-python if not already present
        # This enables VM tests when libvirt is available
        postShellHook = ''
          if ! python3 -c "import libvirt" 2>/dev/null; then
            echo "=============================================="
            echo "  Installing libvirt-python for VM tests..."
            echo "=============================================="
            python3 -m venv /tmp/arda-vm-env
            source /tmp/arda-vm-env/bin/activate
            pip install --quiet libvirt-python
            echo ""
            echo "✓ libvirt-python installed in /tmp/arda-vm-env"
            echo "  To use it, run: source /tmp/arda-vm-env/bin/activate"
            echo "=============================================="
          fi
        '';
      };
    };
}
