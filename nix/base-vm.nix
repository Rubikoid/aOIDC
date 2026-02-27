{ config, lib, pkgs, ... }:
{
  imports = lib.lists.flatten (
    with lib.r.modules;
    [
      (with base; [
        generic
        linux
        vm
      ])

      (with default; [
        nix
        options
      ])

      (with system; [
        compact
        zsh
        security.openssh
      ])
    ]
  );

  microvm = {
    # virtiofsd.package = pkgs.hello;

    hypervisor = "qemu";
    qemu.machine = "virt";

    graphics.enable = false;

    vcpu = 2;
    mem = 1024;
    balloon = false;

    storeDiskType = "squashfs";

    # shares = [
    #   {
    #     source = "/nix/store";
    #     mountPoint = "/nix/.ro-store";
    #     tag = "ro-store";
    #     proto = "9p";
    #   }
    # ];

    interfaces = [
      {
        type = "user";
        id = "usernet";
        mac = "02:00:00:00:00:01";
      }
    ];

    # forwardPorts =
    #   let
    #     mkForward = port: {
    #       from = "host";
    #       proto = "tcp";
    #       host = {
    #         address = "0.0.0.0";
    #         port = 15000 + port;
    #       };
    #       guest.port = port;
    #     };
    #   in
    #   [
    #     (mkForward 80)
    #     (mkForward 443)
    #   ];

  };

  environment.systemPackages = with pkgs; [
    htop
    tcpdump
  ];

  # networking.firewall.allowedTCPPortRanges = [
  #   {
  #     from = 1;
  #     to = 50000;
  #   }
  # ];
  networking.firewall.enable = lib.mkForce false;

  system.stateVersion = "26.05";
  services.getty.autologinUser = "root";
}
