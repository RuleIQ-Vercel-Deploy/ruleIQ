#!/usr/bin/env python3
"""
Check SonarCloud analysis results for the ruleIQ project
"""

import requests
import json
from datetime import datetime

# SonarCloud API configuration
SONAR_TOKEN = "78c39861ad8fa298fc7b3184cfe6573012b9af49"
SONAR_URL = "https://sonarcloud.io/api"
PROJECT_KEY = "ruliq-compliance-platform"
ORGANIZATION = "omara1-bakri"


def get_project_status():
    """Get overall project quality gate status"""
    url = f"{SONAR_URL}/qualitygates/project_status"
    params = {"projectKey": PROJECT_KEY}
    headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


def get_project_measures():
    """Get detailed project metrics"""
    url = f"{SONAR_URL}/measures/component"
    metrics = [
        "bugs",
        "vulnerabilities",
        "code_smells",
        "security_hotspots",
        "coverage",
        "duplicated_lines_density",
        "ncloc",
        "sqale_index",
        "reliability_rating",
        "security_rating",
        "sqale_rating",
    ]
    params = {"component": PROJECT_KEY, "metricKeys": ",".join(metrics)}
    headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


def get_issues_summary():
    """Get summary of issues by type and severity"""
    url = f"{SONAR_URL}/issues/search"
    params = {
        "componentKeys": PROJECT_KEY,
        "facets": "types,severities,rules",
        "ps": 1,  # Page size 1 to just get counts
    }
    headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


def format_rating(rating):
    """Convert numeric rating to letter grade"""
    rating_map = {"1.0": "A", "2.0": "B", "3.0": "C", "4.0": "D", "5.0": "E"}
    return rating_map.get(rating, rating)


def main():
    print("\n" + "=" * 60)
    print("SONARCLOUD ANALYSIS REPORT - ruleIQ Compliance Platform")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: {PROJECT_KEY}")
    print(f"Organization: {ORGANIZATION}")

    # Get quality gate status
    print("\n📊 QUALITY GATE STATUS")
    print("-" * 40)
    status = get_project_status()
    if status:
        gate_status = status.get("projectStatus", {}).get("status", "UNKNOWN")
        emoji = "✅" if gate_status == "OK" else "❌"
        print(f"{emoji} Quality Gate: {gate_status}")

        conditions = status.get("projectStatus", {}).get("conditions", [])
        if conditions:
            print("\nFailed Conditions:")
            for condition in conditions:
                if condition.get("status") != "OK":
                    metric = condition.get("metricKey", "")
                    actual = condition.get("actualValue", "")
                    error = condition.get("errorThreshold", "")
                    print(f"  • {metric}: {actual} (threshold: {error})")

    # Get detailed metrics
    print("\n📈 PROJECT METRICS")
    print("-" * 40)
    measures = get_project_measures()
    if measures:
        metrics = {}
        for measure in measures.get("component", {}).get("measures", []):
            metrics[measure["metric"]] = measure.get("value", "0")

        print(f"Lines of Code: {metrics.get('ncloc', '0')}")
        print(f"Code Coverage: {metrics.get('coverage', '0')}%")
        print(f"Duplicated Lines: {metrics.get('duplicated_lines_density', '0')}%")
        print(f"Technical Debt: {metrics.get('sqale_index', '0')} minutes")

        print("\nRatings:")
        print(
            f"  • Reliability: {format_rating(metrics.get('reliability_rating', '0'))}"
        )
        print(f"  • Security: {format_rating(metrics.get('security_rating', '0'))}")
        print(f"  • Maintainability: {format_rating(metrics.get('sqale_rating', '0'))}")

    # Get issues summary
    print("\n🐛 ISSUES SUMMARY")
    print("-" * 40)
    issues = get_issues_summary()
    if issues:
        total = issues.get("total", 0)
        print(f"Total Issues: {total}")

        # By type
        print("\nBy Type:")
        type_facets = next(
            (f for f in issues.get("facets", []) if f["property"] == "types"), None
        )
        if type_facets:
            for value in type_facets.get("values", []):
                issue_type = value["val"]
                count = value["count"]
                emoji_map = {
                    "BUG": "🐛",
                    "VULNERABILITY": "🔒",
                    "CODE_SMELL": "💨",
                    "SECURITY_HOTSPOT": "🔥",
                }
                emoji = emoji_map.get(issue_type, "📌")
                print(f"  {emoji} {issue_type}: {count}")

        # By severity
        print("\nBy Severity:")
        severity_facets = next(
            (f for f in issues.get("facets", []) if f["property"] == "severities"), None
        )
        if severity_facets:
            for value in severity_facets.get("values", []):
                severity = value["val"]
                count = value["count"]
                emoji_map = {
                    "BLOCKER": "🚫",
                    "CRITICAL": "🔴",
                    "MAJOR": "🟠",
                    "MINOR": "🟡",
                    "INFO": "ℹ️",
                }
                emoji = emoji_map.get(severity, "•")
                print(f"  {emoji} {severity}: {count}")

        # Top rules
        print("\nTop 5 Rule Violations:")
        rule_facets = next(
            (f for f in issues.get("facets", []) if f["property"] == "rules"), None
        )
        if rule_facets:
            for i, value in enumerate(rule_facets.get("values", [])[:5], 1):
                rule = value["val"]
                count = value["count"]
                # Extract language and rule name
                if ":" in rule:
                    lang, rule_id = rule.split(":", 1)
                    print(f"  {i}. [{lang}] {rule_id}: {count} violations")
                else:
                    print(f"  {i}. {rule}: {count} violations")

    print("\n" + "=" * 60)
    print(
        "🔗 View full report: https://sonarcloud.io/summary/overall?id=ruliq-compliance-platform"
    )
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
