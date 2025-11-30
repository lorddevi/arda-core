#!/usr/bin/env bash


# Source - https://stackoverflow.com/a
# Posted by Myrddin Emrys, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-29, License - CC BY-SA 4.0

# Pre Commit
while true; do
    read -r -p "Execute Test: pre-commit run --all-files? " yn
    case $yn in
        [Yy]* ) pre-commit run --all-files ; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# Build arda-cli
while true; do
    read -r -p "Execute Test: just build-arda-cli? " yn
    case $yn in
        [Yy]* ) just build-arda-cli; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-fast
while true; do
    read -r -p "Execute Test: just test-fast? " yn
    case $yn in
        [Yy]* ) just test-fast; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-with-core
while true; do
    read -r -p "Execute Test: just test-with-core? " yn
    case $yn in
        [Yy]* ) just test-with-core; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-without-core
while true; do
    read -r -p "Execute Test: just test-without-core? " yn
    case $yn in
        [Yy]* ) just test-without-core; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-two-phase
while true; do
    read -r -p "Execute Test: just test-two-phase? " yn
    case $yn in
        [Yy]* ) just test-two-phase; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-config
while true; do
    read -r -p "Execute Test: just test-config? " yn
    case $yn in
        [Yy]* ) just test-config; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-config-unit
while true; do
    read -r -p "Execute Test: just test-config-unit? " yn
    case $yn in
        [Yy]* ) just test-config-unit; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-config-integration
while true; do
    read -r -p "Execute Test: just test-config-integration? " yn
    case $yn in
        [Yy]* ) just test-config-integration; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-themes
while true; do
    read -r -p "Execute Test: just test-themes? " yn
    case $yn in
        [Yy]* ) just test-themes; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-cli
while true; do
    read -r -p "Execute Test: just test-cli? " yn
    case $yn in
        [Yy]* ) just test-cli; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-nix
while true; do
    read -r -p "Execute Test: just test-nix? " yn
    case $yn in
        [Yy]* ) just test-nix; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-vm
while true; do
    read -r -p "Execute Test: just test-vm? " yn
    case $yn in
        [Yy]* ) just test-vm; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-vm-nixos
while true; do
    read -r -p "Execute Test: just test-vm-nixos? " yn
    case $yn in
        [Yy]* ) just test-vm-nixos; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-vm-nixos-all
while true; do
    read -r -p "Execute Test: just test-vm-nixos-all? " yn
    case $yn in
        [Yy]* ) just test-vm-nixos-all; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# test-arda-cli
while true; do
    read -r -p "Execute Test: just test-arda-cli? " yn
    case $yn in
        [Yy]* ) just test-arda-cli; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# verify-overlay
while true; do
    read -r -p "Execute Test: just verify-overlay? " yn
    case $yn in
        [Yy]* ) just verify-overlay; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done
