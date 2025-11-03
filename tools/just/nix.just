set positional-arguments
set dotenv-load
set shell := ["bash", "-cue"]
root_dir := `git rev-parse --show-toplevel`
flake_dir := root_dir / "tools/nix"

## Nix Stuff ==================================================================
# Show all packages configured in the Nix `flake.nix`.
list *args:
    cd {{flake_dir}} && nix flake --no-pure-eval show

# Enter the Nix `devShell` with name `$1` and execute the command `${@:2}` (default command is '$SHELL')
[private]
develop *args:
    #!/usr/bin/env bash
    set -eu
    shell="$1"; shift 1;
    args=("$@") && [ "${#args[@]}" != 0 ] || args="$SHELL"
    cd {{root_dir}}
    nix develop --no-pure-eval --accept-flake-config \
        "{{flake_dir}}#$shell" --command "${args[@]}"
## ============================================================================
