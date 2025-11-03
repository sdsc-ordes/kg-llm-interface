{
  description = "AI KG LLM interface";

  inputs = {
    # Nixpkgs
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    # You can access packages and modules from different nixpkgs revs
    # at the same time. Here's an working example:
    nixpkgsStable.url = "github:nixos/nixpkgs/nixos-25.05";
    # Also see the 'stable-packages' overlay at 'overlays/default.nix'.

    flake-utils.url = "github:numtide/flake-utils";

    devenv.url = "github:cachix/devenv";
  };

  outputs = {
    nixpkgs,
    flake-utils,
    devenv,
    ...
  } @ inputs:
  # Creates an attribute map `{ devShells.<system>.default = ...}`
    flake-utils.lib.eachDefaultSystem (
      system: let
        # Import nixpkgs and load it into pkgs.
        pkgs = import nixpkgs {
          inherit system;
        };

        # python environment defined separately
        pythonFile = import ./python-uv.nix {
          inherit pkgs;
          lib = pkgs.lib;
          namespace = "python";
        };

        tools = with pkgs; [
          bash
          coreutils
          curl
          findutils
          git
          git-cliff
          just
          pyright # Language Server.
          ruff # Formatter and linter.
          zsh
        ];
      in {
        devShells = {
          default = devenv.lib.mkShell {
            inherit inputs pkgs;
            modules =
              pythonFile
              ++ [
                {packages = tools;}
              ];
          };
        };
      }
    );
}
