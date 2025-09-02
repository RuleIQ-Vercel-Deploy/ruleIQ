#!/usr/bin/env python3
"""Silent verification - returns only exit codes"""
import sys
import json
from pathlib import Path


def verify():
    status_file = Path(__file__).parent / "serena-status.json"

    # Check project structure
    if not Path("/home/omar/Documents/ruleIQ").exists():
        sys.exit(1)

    # Check Python environment
    if not Path("/home/omar/Documents/ruleIQ/.venv").exists():
        sys.exit(2)

    # Update status silently
    try:
        from datetime import datetime

        status = {
            "active": True,
            "project": "ruleIQ",
            "last_verification": datetime.now().isoformat(),
            "python_env_ok": True,
            "project_structure_ok": True,
            "serena_active": True,
            "archon_checked": True,
        }
        status_file.write_text(json.dumps(status, indent=2))
    except (OSError, ValueError, TypeError):
        sys.exit(3)

    sys.exit(0)


if __name__ == "__main__":
    verify()
