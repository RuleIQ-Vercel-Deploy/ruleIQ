#!/bin/bash
# Script to ensure conda is disabled and .venv is activated for ruleIQ project

# Deactivate conda if it's active
if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
    echo "Deactivating conda environment: $CONDA_DEFAULT_ENV"
    conda deactivate
fi

# Make sure conda doesn't auto-activate
export CONDA_AUTO_ACTIVATE_BASE=false

# Check if we're in the ruleIQ directory
if [[ "$PWD" == *"/ruleIQ"* ]]; then
    # Activate the project's virtual environment
    if [[ -f "/home/omar/Documents/ruleIQ/.venv/bin/activate" ]]; then
        echo "Activating ruleIQ virtual environment..."
        source /home/omar/Documents/ruleIQ/.venv/bin/activate
        echo "Virtual environment activated: $VIRTUAL_ENV"
    else
        echo "WARNING: .venv not found in /home/omar/Documents/ruleIQ/"
        echo "Create it with: python3 -m venv /home/omar/Documents/ruleIQ/.venv"
    fi
fi

# Show current Python location
echo "Current Python: $(which python)"
echo "Python version: $(python --version 2>&1)"
