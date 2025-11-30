#!/usr/bin/env bash
# Verification script for rich-click overlay
# Run this in devShell to ensure the overlay is working correctly
#
# Usage:
#   just verify-overlay
#   OR
#   nix develop --command ./pkgs/testing/verify-overlay.sh

set -euo pipefail

echo "==================================================================="
echo "  Rich-Click Overlay Verification"
echo "==================================================================="
echo ""

# Check rich-click version
echo "Checking rich-click version..."
RICH_CLICK_VERSION=$(python3 -c "import rich_click; print(rich_click.__version__)" 2>&1 || echo "UNKNOWN")

echo "  rich-click version: $RICH_CLICK_VERSION"

if [ "$RICH_CLICK_VERSION" = "1.9.4" ]; then
    echo "  ✅ Version is correct (1.9.4 - overlay version)"
elif [ "$RICH_CLICK_VERSION" = "1.8.9" ]; then
    echo "  ❌ Version is WRONG (1.8.9 - nixpkgs version)"
    echo "     The overlay is NOT being applied correctly!"
    exit 1
else
    echo "  ⚠️  Version is unexpected: $RICH_CLICK_VERSION"
fi

echo ""

# Check if RichHelpConfiguration has theme parameter
echo "Checking RichHelpConfiguration API..."
python3 << 'PYTHON_SCRIPT'
import sys
try:
    from rich_click.rich_help_configuration import RichHelpConfiguration
    import inspect

    sig = inspect.signature(RichHelpConfiguration.__init__)
    params = sig.parameters

    if 'theme' in params:
        print("  ✅ RichHelpConfiguration has 'theme' parameter (1.9.4 API)")
        sys.exit(0)
    else:
        print("  ❌ RichHelpConfiguration missing 'theme' parameter (1.8.9 API)")
        sys.exit(1)
except Exception as e:
    print(f"  ⚠️  Error checking RichHelpConfiguration: {e}")
    sys.exit(1)
PYTHON_SCRIPT

RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo ""
    echo "==================================================================="
    echo "  ✅ Overlay verification PASSED"
    echo "==================================================================="
    echo ""
    echo "The custom rich-click overlay is working correctly."
    echo "DevShell has rich-click 1.9.4 with theming support."
else
    echo ""
    echo "==================================================================="
    echo "  ❌ Overlay verification FAILED"
    echo "==================================================================="
    echo ""
    echo "The custom rich-click overlay is NOT working!"
    echo ""
    echo "This means:"
    echo "  - arda --help will fail with TypeError"
    echo "  - DevShell is using nixpkgs version 1.8.9 instead of overlay 1.9.4"
    echo ""
    echo "To fix:"
    echo "  1. Check flake.nix applies overlays/default.nix"
    echo "  2. Check devShell.nix uses pkgs.python313Packages directly"
    echo "  3. Run 'direnv allow' to refresh devShell"
    exit 1
fi
