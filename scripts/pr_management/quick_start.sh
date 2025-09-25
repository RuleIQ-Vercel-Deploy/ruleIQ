#!/bin/bash

# PR Management System - Quick Start Script

echo "============================================"
echo "PR Management System - Quick Start"
echo "============================================"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check for GitHub CLI (optional but recommended)
if command -v gh &> /dev/null; then
    echo "✓ GitHub CLI detected"
    gh auth status
else
    echo "⚠ GitHub CLI not found (optional but recommended)"
    echo "  Install with: brew install gh (macOS) or see https://cli.github.com"
fi

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠ GITHUB_TOKEN environment variable not set"
    echo "  The system will attempt to use GitHub CLI authentication"
else
    echo "✓ GITHUB_TOKEN environment variable is set"
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Available commands:"
echo ""
echo "1. Analyze all PRs:"
echo "   python3 pr_analyzer.py"
echo ""
echo "2. Run complete cleanup (dry-run):"
echo "   python3 pr_cleanup_orchestrator.py"
echo ""
echo "3. Run complete cleanup (live mode):"
echo "   python3 pr_cleanup_orchestrator.py --live"
echo ""
echo "4. Process Dependabot PRs only:"
echo "   python3 dependabot_handler.py"
echo ""
echo "5. Review security PRs:"
echo "   python3 security_pr_reviewer.py"
echo ""
echo "6. Check CI status:"
echo "   python3 ci_status_checker.py"
echo ""
echo "============================================"
echo "IMPORTANT: Always start with dry-run mode!"
echo "============================================"

# Make all Python scripts executable
chmod +x *.py

echo ""
echo "All scripts are now executable. You can run them directly: ./pr_analyzer.py"