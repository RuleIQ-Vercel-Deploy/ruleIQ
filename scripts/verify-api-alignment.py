#!/usr/bin/env python3
"""Verify API alignment after fixes."""

import re
from pathlib import Path
from collections import defaultdict

issues = defaultdict(list)

# Check all routers
for router_file in Path("api").rglob("*.py"):
    with open(router_file, "r") as f:
        content = f.read()

    if "APIRouter" not in content:
        continue

    router_name = router_file.stem

    # Check for non-standard parameters
    params = re.findall(r"\{([^}]+)\}", content)
    for param in params:
        if param not in ["id", "token", "model", "stage"]:
            issues["non_standard_params"].append(f"{router_name}: {param}")

    # Check for missing /api/v1/ prefix
    if "prefix=" in content:
        prefix_match = re.search(r'prefix=[\'"`]([^\'"`]+)[\'"`]', content)
        if prefix_match:
            prefix = prefix_match.group(1)
            if not prefix.startswith("/api/v1"):
                issues["bad_prefix"].append(f"{router_name}: {prefix}")

# Report issues
if issues:
    print("⚠️  Issues found:")
    for issue_type, items in issues.items():
        print(f"\n{issue_type}:")
        for item in items:
            print(f"  - {item}")
else:
    print("✅ All API endpoints properly aligned!")
