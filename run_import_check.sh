#!/bin/bash
cd /home/omar/Documents/ruleIQ
python3 find_import_errors.py
echo ""
echo "=== Running pytest collection check ==="
pytest --collect-only -q 2>&1 | tail -20