#!/bin/bash

echo "Installing dead code detection tools..."

# Python tools
pip install --quiet autoflake vulture

# Verify installation
echo ""
echo "Verifying installations:"
echo -n "autoflake: "
autoflake --version 2>/dev/null || echo "NOT INSTALLED"
echo -n "vulture: "
vulture --version 2>/dev/null || echo "NOT INSTALLED"

echo ""
echo "Tools ready for dead code analysis!"