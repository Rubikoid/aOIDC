{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

    base = {
      url = "github:rubikoid/nix-base"; # "base"; # github:rubikoid/nix-base
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    microvm = {
      url = "github:microvm-nix/microvm.nix/68c9f9c6ca91841f04f726a298c385411b7bfcd5";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.spectrum.follows = "nixpkgs";
    };
  };

  outputs =
    { self, nixpkgs, base, ... }@inputs:
    let
      lib = base.lib.r.extender base.lib ({ lib, prev, r, prevr }: { });
    in
    lib.r.mkFlake nixpkgs (
      { system, pkgs, ... }:
      let
        vmToApp =
          name:
          let
            importedConfig = import ./nix/vm.nix {
              inherit self nixpkgs lib;
              system = "aarch64-linux";
              hostPkgs = pkgs;
              name = name;
              main_config = ./nix/vms + "/${name}.nix";
            };
          in
          {
            type = "app";
            program = "${importedConfig.config.microvm.declaredRunner}/bin/microvm-run";
          };

        pythonOptions = {
          name = "aoidc";
          source = ./.;

          sourcePreference = "wheel";

          overrides = _: _: { };

          inherit inputs pkgs;
        };

        pythonSetup = lib.r.helpers.python.setupPythonEnvs pythonOptions;
      in
      {
        apps = {
          kanidm = vmToApp "kanidm";
        };

        packages = {
          default = pythonSetup.simple.pyEnv;
        };

        devShells = {
          default = pkgs.mkShell {
            packages = (with pkgs; [ ]) ++ pythonSetup.editable.packages;
            env = pythonSetup.editable.env;
            shellHook = ''
              ${pythonSetup.editable.shellHook}
            '';

            nativeBuildInputs = with pkgs; [ ];
          };

          # It is of course perfectly OK to keep using an impure virtualenv workflow and only use uv2nix to build packages.
          # This devShell simply adds Python and undoes the dependency leakage done by Nixpkgs Python infrastructure.
          impure = pkgs.mkShell {
            packages = [
              pkgs.python312
              pkgs.uv
            ];
            shellHook = ''
              unset PYTHONPATH
            '';
          };

        };
      }
    );
}
