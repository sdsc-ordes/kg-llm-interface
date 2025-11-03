set positional-arguments
set dotenv-load
set shell := ["bash", "-cue"]
root_dir := `git rev-parse --show-toplevel`
flake_dir := root_dir / "tools/nix"

# Manage nix flakes
mod nix 'tools/just/nix.just'

[private]
default:
  just --unsorted --list --no-aliases

alias dev := develop

# Enter a development shell.
develop:
  just nix::develop default

# Set up python environment.
setup:
  @echo "🔧 Setting up python environment"
  uv sync --all-extras --group dev
  uv run pre-commit install


# Run all quality checks.
check: setup
  @echo "🚀 Validating lock file"
  uv lock --check
  @echo "🚀 Running all pre-commit hooks"
  uv run pre-commit run -a

alias fmt := format
# Format code.
format *args: setup
  @echo "🚀 Formatting python code"
  uv run ruff format {{args}}

# Run unit tests.
test *args: setup
  @echo "🚀 Testing code: Running pytest"
  @uv run pytest {{args}}
