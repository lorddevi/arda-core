{
  inputs,
  pkgs,
  lib,
}:

{
  # Arda world configuration
  # This defines your infrastructure: hosts, services, and roles

  # Meta information about this world
  world = {
    name = "arda-world";
    description = "An Arda-managed NixOS infrastructure";
  };

  # Define your NixOS hosts here
  # Each host can have roles, features, and custom settings
  inventory = {
    hosts = {
      # Example host configuration
      # Uncomment and customize as needed
      #
      # example-host = {
      #   role = "basic-workstation";
      #   settings = {
      #     # Custom settings for this host
      #     users.extraUsers.alice.shell = pkgs.zsh;
      #   };
      # };
    };
  };

  # Define service templates that can be used by hosts
  # This is where you'd define the Service/Feature/Role model
  services = {
    # Example service definitions
    # These will be expanded as Arda's service system is developed
  };

  features = {
    # Feature compositions
    # A feature can group multiple services together
    #
    # Example:
    # web-server = {
    #   services = [ "nginx" "certbot" "firewall" ];
    # };
  };

  roles = {
    # Role compositions
    # A role combines features to create a complete system type
    #
    # Example:
    # basic-workstation = {
    #   features = [ "desktop-environment" "development-tools" "security" ];
    # };
  };

  # Generate NixOS configurations from inventory
  # This creates the actual configurations for each host
  nixosConfigurations = lib.mapAttrs (
    hostName: hostConfig:
    let
      # Get role for this host
      role = hostConfig.role or "basic-host";

      # Get features for this role
      roleFeatures = lib.optionals (role != "basic-host") (
        lib.optionals (lib.hasAttr role roles) ((lib.attrByPath [ role "features" ] [ ] roles))
      );

      # Get services from features
      roleServices = lib.concatMap (
        feature:
        lib.optionals (lib.hasAttr feature features) (lib.attrByPath [ feature "services" ] [ ] features)
      ) roleFeatures;

      # Merge all services for this host
      allServices = lib.unique (roleServices ++ (hostConfig.services or [ ]));

      # Generate system configuration
      systemConfiguration = {
        # Basic system settings
        system.stateVersion = "24.11";

        # Use arda-core's base module (when available)
        # imports = [
        #   arda-core.nixosModules.base
        # ] ++ allServices;

        # Placeholder for now - just basic NixOS
        imports = [ ];

        # Apply host-specific settings
        networking.hostName = hostName;

        # Apply merged service configurations
        # services = lib.foldl' (acc: serviceName:
        #   lib.recursiveUpdate acc (lib.attrByPath [ serviceName ] { } services)
        # ) { } allServices;
      };
    in
    pkgs.nixosSystem {
      inherit systemConfiguration;
      modules = [
        systemConfiguration
      ];
    }
  ) inventory.hosts;
}
