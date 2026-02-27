{
  self,
  nixpkgs,
  system,
  hostPkgs,
  lib,
  name,
  main_config,
  ...
}:
nixpkgs.lib.nixosSystem {
  inherit system;

  specialArgs = {
    inherit lib;

    inputs = self.inputs;
    mode = "NixOS";

    # dummy values!
    secretsModule = { };
    secrets = { };
  };

  modules = [
    {
      imports = [
        ./base-vm.nix
      ];
      config = {
        isWSL = false;
        isDarwin = false;
        system-arch-name = system;
        device = "${name}-test-machine";
        microvm.vmHostPackages = hostPkgs;
      };
    }
    main_config
  ];
}
