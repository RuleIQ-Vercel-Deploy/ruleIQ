#!/bin/bash
# Setup script for Python linters used by Codacy and CI/CD

set -e

echo "Setting up Python linters..."

# Define virtual environment path
VENV_PATH="/home/omar/Documents/ruleIQ/.venv"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install Python linters in venv
echo "Installing Python linters in virtual environment..."
pip install -q \
    ruff==0.12.8 \
    black==25.1.0 \
    flake8==7.3.0 \
    pylint==3.3.8 \
    mypy==1.17.1 \
    isort==6.0.1 \
    bandit==1.8.6 \
    safety

# Export paths for Codacy CLI
export PATH="$VENV_PATH/bin:$PATH"
export PYTHONPATH="$VENV_PATH/lib/python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages:$PYTHONPATH"

# Verify installations
echo -e "
Verifying linter installations:"
echo "-----------------------------------"
command -v ruff >/dev/null 2>&1 && echo "✅ ruff: $(ruff --version)" || echo "❌ ruff not found"
command -v black >/dev/null 2>&1 && echo "✅ black: $(black --version | head -1)" || echo "❌ black not found"
command -v flake8 >/dev/null 2>&1 && echo "✅ flake8: $(flake8 --version | head -1)" || echo "❌ flake8 not found"
command -v pylint >/dev/null 2>&1 && echo "✅ pylint: $(pylint --version | head -1)" || echo "❌ pylint not found"
command -v mypy >/dev/null 2>&1 && echo "✅ mypy: $(mypy --version)" || echo "❌ mypy not found"
command -v isort >/dev/null 2>&1 && echo "✅ isort: $(isort --version | grep VERSION)" || echo "❌ isort not found"
command -v bandit >/dev/null 2>&1 && echo "✅ bandit: $(bandit --version 2>&1 | grep version)" || echo "❌ bandit not found"

echo -e "
Setup complete!"
echo -e "
For Codacy CLI, use the following paths:"
echo "  Python linters: $VENV_PATH/bin/"
echo "  Add to PATH: export PATH=\"$VENV_PATH/bin:\$PATH\""