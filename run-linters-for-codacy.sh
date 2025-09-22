#!/bin/bash
# Wrapper script for Codacy CLI to run Python linters

# Add local bin to PATH
export PATH="/home/omar/.local/bin:$PATH"

# Verify linters are accessible
echo "Checking linter availability..."
which ruff || echo "Warning: ruff not found"
which black || echo "Warning: black not found"
which flake8 || echo "Warning: flake8 not found"
which pylint || echo "Warning: pylint not found"
which mypy || echo "Warning: mypy not found"
which bandit || echo "Warning: bandit not found"

# Run the requested linter
LINTER=$1
shift

case "$LINTER" in
  ruff)
    /home/omar/.local/bin/ruff "$@"
    ;;
  black)
    /home/omar/.local/bin/black "$@"
    ;;
  flake8)
    /home/omar/.local/bin/flake8 "$@"
    ;;
  pylint)
    /home/omar/.local/bin/pylint "$@"
    ;;
  mypy)
    /home/omar/.local/bin/mypy "$@"
    ;;
  bandit)
    /home/omar/.local/bin/bandit "$@"
    ;;
  *)
    echo "Unknown linter: $LINTER"
    echo "Available linters: ruff, black, flake8, pylint, mypy, bandit"
    exit 1
    ;;
esac