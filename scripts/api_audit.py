#!/usr/bin/env python3
"""
Comprehensive API Audit Script for ruleIQ
Analyzes all FastAPI endpoints and their authentication requirements
"""

import re
from pathlib import Path
from typing import Dict, List
import json


class APIEndpointAnalyzer:
    def __init__(self, api_dir: str = "api/routers") -> None:
        self.api_dir = Path(api_dir)
        self.endpoints = []
        self.auth_patterns = {
            "jwt": ["get_current_active_user", "get_current_user"],
            "stack_auth": ["get_current_stack_user"],
            "rbac": ["require_permissions", "require_permission"],
            "rate_limit": ["rate_limit", "auth_rate_limit"],
        }

    def analyze_file(self, file_path: Path) -> List[Dict]:
        """Analyze a single router file for endpoints"""
        endpoints = []

        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Find all route decorators and their functions
            route_pattern = r'@router\.(get|post|put|patch|delete)\s*\(\s*["\']([^"\']+)["\']'
            function_pattern = r"async def (\w+)\s*\([^)]*\):"

            routes = re.finditer(route_pattern, content)
            functions = re.finditer(function_pattern, content)

            route_list = [(m.group(1), m.group(2), m.start()) for m in routes]
            function_list = [(m.group(1), m.start()) for m in functions]

            # Match routes with functions
            for method, path, route_pos in route_list:
                # Find the next function after this route
                next_func = None
                for func_name, func_pos in function_list:
                    if func_pos > route_pos:
                        next_func = func_name
                        break

                if next_func:
                    # Analyze authentication requirements
                    auth_info = self.analyze_auth_requirements(content, route_pos, func_pos)

                    endpoint = {
                        "file": str(file_path.relative_to(Path("."))),
                        "method": method.upper(),
                        "path": path,
                        "function": next_func,
                        "authentication": auth_info,
                        "full_path": f"/api/v1{path}" if not path.startswith("/api") else path,
                    }
                    endpoints.append(endpoint)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return endpoints

    def analyze_auth_requirements(self, content: str, route_pos: int, func_pos: int) -> Dict:
        """Analyze authentication requirements for an endpoint"""
        # Extract the function definition and decorators
        func_section = content[route_pos : func_pos + 200]  # Get some context

        auth_info = {
            "required": False,
            "type": "none",
            "dependencies": [],
            "rate_limited": False,
            "rbac_permissions": [],
        }

        # Check for authentication dependencies
        for auth_type, patterns in self.auth_patterns.items():
            for pattern in patterns:
                if pattern in func_section:
                    auth_info["required"] = True
                    if auth_type in ["jwt", "stack_auth"]:
                        auth_info["type"] = auth_type
                    auth_info["dependencies"].append(pattern)

                    if auth_type == "rate_limit":
                        auth_info["rate_limited"] = True
                    elif auth_type == "rbac":
                        # Try to extract permission requirements
                        perm_match = re.search(
                            r'require_permissions?\(["\']([^"\']+)["\']', func_section
                        )
                        if perm_match:
                            auth_info["rbac_permissions"].append(perm_match.group(1))

        return auth_info

    def audit_all_endpoints(self) -> List[Dict]:
        """Audit all API endpoints"""
        all_endpoints = []

        for py_file in self.api_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            endpoints = self.analyze_file(py_file)
            all_endpoints.extend(endpoints)

        return sorted(all_endpoints, key=lambda x: (x["file"], x["path"]))

    def generate_report(self, endpoints: List[Dict]) -> Dict:
        """Generate a comprehensive audit report"""
        report = {
            "summary": {
                "total_endpoints": len(endpoints),
                "authenticated_endpoints": len(
                    [e for e in endpoints if e["authentication"]["required"]]
                ),
                "public_endpoints": len(
                    [e for e in endpoints if not e["authentication"]["required"]]
                ),
                "jwt_endpoints": len(
                    [e for e in endpoints if e["authentication"]["type"] == "jwt"]
                ),
                "stack_auth_endpoints": len(
                    [e for e in endpoints if e["authentication"]["type"] == "stack_auth"]
                ),
                "rate_limited_endpoints": len(
                    [e for e in endpoints if e["authentication"]["rate_limited"]]
                ),
                "rbac_protected_endpoints": len(
                    [e for e in endpoints if e["authentication"]["rbac_permissions"]]
                ),
            },
            "endpoints_by_file": {},
            "authentication_issues": [],
            "endpoints": endpoints,
        }

        # Group by file
        for endpoint in endpoints:
            file_name = endpoint["file"]
            if file_name not in report["endpoints_by_file"]:
                report["endpoints_by_file"][file_name] = []
            report["endpoints_by_file"][file_name].append(endpoint)

        # Identify potential issues
        for endpoint in endpoints:
            auth = endpoint["authentication"]

            # Check for Stack Auth usage (should be migrated)
            if auth["type"] == "stack_auth":
                report["authentication_issues"].append(
                    {
                        "type": "stack_auth_usage",
                        "endpoint": f"{endpoint['method']} {endpoint['full_path']}",
                        "file": endpoint["file"],
                        "message": "Endpoint still uses Stack Auth - needs migration to JWT",
                    }
                )

            # Check for missing authentication on sensitive endpoints
            if not auth["required"] and any(
                sensitive in endpoint["path"].lower()
                for sensitive in ["admin", "user", "profile", "assessment", "evidence"]
            ):
                report["authentication_issues"].append(
                    {
                        "type": "missing_auth",
                        "endpoint": f"{endpoint['method']} {endpoint['full_path']}",
                        "file": endpoint["file"],
                        "message": "Potentially sensitive endpoint without authentication",
                    }
                )

        return report


def main() -> None:
    """Main function to run the API audit"""
    print("🔍 Starting Comprehensive API Audit...")

    analyzer = APIEndpointAnalyzer()
    endpoints = analyzer.audit_all_endpoints()
    report = analyzer.generate_report(endpoints)

    # Save detailed report
    with open("api_audit_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n📊 API Audit Summary:")
    print(f"   Total Endpoints: {report['summary']['total_endpoints']}")
    print(f"   Authenticated: {report['summary']['authenticated_endpoints']}")
    print(f"   Public: {report['summary']['public_endpoints']}")
    print(f"   JWT Protected: {report['summary']['jwt_endpoints']}")
    print(f"   Stack Auth (NEEDS MIGRATION): {report['summary']['stack_auth_endpoints']}")
    print(f"   Rate Limited: {report['summary']['rate_limited_endpoints']}")
    print(f"   RBAC Protected: {report['summary']['rbac_protected_endpoints']}")

    if report["authentication_issues"]:
        print(f"\n⚠️  Authentication Issues Found: {len(report['authentication_issues'])}")
        for issue in report["authentication_issues"][:5]:  # Show first 5
            print(f"   - {issue['type']}: {issue['endpoint']} ({issue['file']})")
        if len(report["authentication_issues"]) > 5:
            print(f"   ... and {len(report['authentication_issues']) - 5} more")

    print("\n📄 Detailed report saved to: api_audit_report.json")

    # Generate markdown documentation
    generate_markdown_docs(report)
    print("📄 API documentation saved to: API_ENDPOINTS_DOCUMENTATION.md")


def generate_markdown_docs(report: Dict) -> None:
    """Generate markdown documentation for all endpoints"""

    md_content = f"""# ruleIQ API Endpoints Documentation

**Generated**: {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Endpoints**: {report["summary"]["total_endpoints"]}
**Authentication Status**: {report["summary"]["authenticated_endpoints"]} authenticated, {report["summary"]["public_endpoints"]} public

## Summary

| Metric | Count |
|--------|-------|
| Total Endpoints | {report["summary"]["total_endpoints"]} |
| Authenticated Endpoints | {report["summary"]["authenticated_endpoints"]} |
| Public Endpoints | {report["summary"]["public_endpoints"]} |
| JWT Protected | {report["summary"]["jwt_endpoints"]} |
| Stack Auth (MIGRATION NEEDED) | {report["summary"]["stack_auth_endpoints"]} |
| Rate Limited | {report["summary"]["rate_limited_endpoints"]} |
| RBAC Protected | {report["summary"]["rbac_protected_endpoints"]} |

## Authentication Issues

"""

    if report["authentication_issues"]:
        for issue in report["authentication_issues"]:
            md_content += f"- **{issue['type']}**: `{issue['endpoint']}` in `{issue['file']}` - {issue['message']}\n"
    else:
        md_content += "✅ No authentication issues found!\n"

    md_content += "\n## Endpoints by File\n\n"

    for file_name, endpoints in report["endpoints_by_file"].items():
        md_content += f"### {file_name}\n\n"

        for endpoint in endpoints:
            auth = endpoint["authentication"]
            auth_badge = "🔒" if auth["required"] else "🌐"
            auth_type = auth["type"].upper() if auth["type"] != "none" else "PUBLIC"

            md_content += f"#### {auth_badge} `{endpoint['method']} {endpoint['full_path']}`\n\n"
            md_content += f"- **Function**: `{endpoint['function']}`\n"
            md_content += f"- **Authentication**: {auth_type}\n"

            if auth["dependencies"]:
                md_content += f"- **Dependencies**: {', '.join(auth['dependencies'])}\n"

            if auth["rate_limited"]:
                md_content += "- **Rate Limited**: ✅\n"

            if auth["rbac_permissions"]:
                md_content += f"- **RBAC Permissions**: {', '.join(auth['rbac_permissions'])}\n"

            md_content += "\n"

        md_content += "\n"

    # Save markdown documentation
    with open("API_ENDPOINTS_DOCUMENTATION.md", "w") as f:
        f.write(md_content)


if __name__ == "__main__":
    main()
