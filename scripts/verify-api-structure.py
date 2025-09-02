#!/usr/bin/env python3
"""
Verify API structure and naming conventions
"""

import re
from pathlib import Path
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).parent.parent
ROUTERS_DIR = PROJECT_ROOT / "api" / "routers"
MAIN_PY = PROJECT_ROOT / "api" / "main.py"


def extract_endpoints() -> Dict[str, List[str]]:
    """Extract all API endpoints from routers"""
    endpoints = {}

    for router_file in ROUTERS_DIR.glob("*.py"):
        if router_file.name == "__init__.py":
            continue

        with open(router_file, "r") as f:
            content = f.read()

        # Find all endpoint decorators
        pattern = r'@router\.(get|post|put|patch|delete)\("([^"]+)"'
        matches = re.findall(pattern, content)

        endpoints[router_file.stem] = [
            f"{method.upper()} {path}" for method, path in matches
        ]

    return endpoints


def check_naming_conventions(endpoints: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Check for naming convention issues"""
    issues = {
        "trailing_slashes": [],
        "underscores_in_paths": [],
        "inconsistent_params": [],
        "camelCase_in_paths": [],
    }

    for router, paths in endpoints.items():
        for endpoint in paths:
            method, path = endpoint.split(" ", 1)

            # Check for trailing slashes
            if path.endswith("/") and path != "/":
                issues["trailing_slashes"].append(f"{router}: {endpoint}")

            # Check for underscores (except in path parameters)
            path_without_params = re.sub(r"\{[^}]+\}", "", path)
            if "_" in path_without_params:
                issues["underscores_in_paths"].append(f"{router}: {endpoint}")

            # Check for camelCase
            if re.search(r"[a-z][A-Z]", path_without_params):
                issues["camelCase_in_paths"].append(f"{router}: {endpoint}")

            # Check parameter naming consistency
            params = re.findall(r"\{([^}]+)\}", path)
            for param in params:
                if param not in ["id", "user_id", "framework_id", "assessment_id"]:
                    issues["inconsistent_params"].append(
                        f"{router}: {endpoint} - param: {{{param}}}"
                    )

    return issues


def find_duplicates(endpoints: Dict[str, List[str]]) -> List[str]:
    """Find potentially duplicate endpoints"""
    duplicates = []
    all_paths = []

    # Collect all paths
    for router, paths in endpoints.items():
        for endpoint in paths:
            all_paths.append((router, endpoint))

    # Check for similar endpoints
    for i, (router1, endpoint1) in enumerate(all_paths):
        for router2, endpoint2 in all_paths[i + 1 :]:
            method1, path1 = endpoint1.split(" ", 1)
            method2, path2 = endpoint2.split(" ", 1)

            # Check if they're semantically similar
            if method1 == method2:
                # Normalize paths for comparison
                norm_path1 = re.sub(r"\{[^}]+\}", "{id}", path1)
                norm_path2 = re.sub(r"\{[^}]+\}", "{id}", path2)

                # Check for duplicates with different naming
                if (
                    "generate" in norm_path1
                    and "generate" in norm_path2
                    and router1 != router2
                ):
                    duplicates.append(
                        f"{router1}: {endpoint1} <-> {router2}: {endpoint2}"
                    )
                elif norm_path1 == norm_path2 and router1 != router2:
                    duplicates.append(
                        f"{router1}: {endpoint1} <-> {router2}: {endpoint2}"
                    )

    return duplicates


def main():
    print("🔍 API Structure Verification")
    print("=" * 80)

    # Extract endpoints
    endpoints = extract_endpoints()

    # Statistics
    total_endpoints = sum(len(paths) for paths in endpoints.values())
    print(f"\n📊 Statistics:")
    print(f"   Total Routers: {len(endpoints)}")
    print(f"   Total Endpoints: {total_endpoints}")

    # Check naming conventions
    issues = check_naming_conventions(endpoints)

    print(f"\n✅ Naming Convention Check:")
    for issue_type, issue_list in issues.items():
        if issue_list:
            print(f"\n   ⚠️  {issue_type.replace('_', ' ').title()}:")
            for issue in issue_list[:5]:
                print(f"      - {issue}")
            if len(issue_list) > 5:
                print(f"      ... and {len(issue_list) - 5} more")
        else:
            print(f"   ✅ No {issue_type.replace('_', ' ')} found")

    # Check for duplicates
    duplicates = find_duplicates(endpoints)
    if duplicates:
        print(f"\n⚠️  Potential Duplicate Endpoints:")
        for dup in duplicates[:10]:
            print(f"   - {dup}")
    else:
        print(f"\n✅ No duplicate endpoints found")

    # Summary
    print("\n" + "=" * 80)
    print("📋 Summary:")

    total_issues = sum(len(v) for v in issues.values()) + len(duplicates)
    if total_issues == 0:
        print("   ✅ All API endpoints follow naming conventions!")
    else:
        print(f"   ⚠️  Found {total_issues} total issues to review")
        print("\n   Recommendations:")
        print("   1. Use kebab-case for all URL paths")
        print("   2. Standardize path parameters to use {id}")
        print("   3. Remove trailing slashes except for root paths")
        print("   4. Consolidate duplicate functionality")

    # Check specific policy endpoints issue
    print("\n" + "=" * 80)
    print("🔍 Policy Endpoints Analysis:")

    policy_endpoints = {}
    for router, paths in endpoints.items():
        if "polic" in router.lower() or "ai" in router.lower():
            policy_related = [
                p for p in paths if "polic" in p.lower() or "generate" in p.lower()
            ]
            if policy_related:
                policy_endpoints[router] = policy_related

    if policy_endpoints:
        print("\n   Policy-related endpoints found in:")
        for router, paths in policy_endpoints.items():
            print(f"\n   📁 {router}:")
            for path in paths:
                print(f"      - {path}")

    return total_issues == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
