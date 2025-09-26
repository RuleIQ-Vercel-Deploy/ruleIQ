#!/bin/bash
# Setup script for ruleIQ Python environment

PROJECT_DIR="/home/omar/Documents/ruleIQ"
VENV_DIR="$PROJECT_DIR/.venv"

echo "==================================="
echo "RuleIQ Environment Setup"
echo "==================================="

# Check if .venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    cd "$PROJECT_DIR"
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate the environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements if they exist
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "Installing requirements.txt..."
    pip install -r "$PROJECT_DIR/requirements.txt"
elif [ -f "$PROJECT_DIR/requirements-cloudrun.txt" ]; then
    echo "Installing requirements-cloudrun.txt..."
    pip install -r "$PROJECT_DIR/requirements-cloudrun.txt"
fi

echo ""
echo "==================================="
echo "✅ Environment Ready!"
echo "==================================="
echo "Python: $(which python)"
echo "Version: $(python --version)"
echo "Virtual Env: $VIRTUAL_ENV"
