{ config, lib, ... }:

{
  # Common module - shared settings for all hosts
  # You can customize this or create new modules

  # Enable flake module
  nix.settings.experimental-features = [ "flakes" "nix-command" ];

  # Basic system configuration
  environment.systemPackages = with pkgs; [
    # Add common packages here
    git
    curl
    wget
  ];

  # Enable common services
  services = {
    # Enable SSH server
    openssh.enable = true;

    # Enable automatic updates
    autoUpgrade = {
      enable = true;
      channel = "stable";
    };
  };

  # Security settings
  security = {
    # Enable auditd
    auditd.enable = true;

    # Harden the system
    harden = true;
  };

  # Time zone
  time.timeZone = "UTC";

  # Locale
  i18n.defaultLocale = "en_US.UTF-8";
  i18n.extraLocaleSettings = {
    LC_ADDRESS = "en_US.UTF-8";
    LC_IDENTIFICATION = "en_US.UTF-8";
    LC_MEASUREMENT = "en_US.UTF-8";
    LC_MONETARY = "en_US.UTF-8";
    LC_NAME = "en_US.UTF-8";
    LC_NUMERIC = "en_US.UTF-8";
    LC_PAPER = "en_US.UTF-8";
    LC_TELEPHONE = "en_US.UTF-8";
    LC_TIME = "en_US.UTF-8";
  };
}
