# This function returns a list of `devenv` modules
# which are passed to `mkShell`.
#
# Search for package at:
# https://search.nixos.org/packages
{
  # These are `pkgs` from `input.nixpkgs`.
  pkgs,
  lib,
  namespace,
  ...
}: [
  {
    packages = [
      pkgs.stdenv.cc.cc.lib # fix: libstdc++ required by jupyter.
      pkgs.libz # fix: for numpy/pandas import
    ];

    # We use `devenv` language support since, its
    # pretty involved to setup a python environment.
    languages.python = {
      enable = true;
      venv.enable = true;
      uv = {
        enable = true;
        package = pkgs.uv;
        sync = {
          enable = true;
          allExtras = true;
        };
      };
    };

    enterShell = ''
      just setup
    '';

    env = {
      RUFF_CACHE_DIR = ".output/cache/ruff";
    };
  }
]
