#!/usr/bin/env python3
"""
Get detailed information about blocker issues from SonarCloud
"""

import os
import requests
from typing import Dict, List, Any
import json

# Configuration
SONAR_TOKEN = "78c39861ad8fa298fc7b3184cfe6573012b9af49"
PROJECT_KEY = "ruliq-compliance-platform"
ORGANIZATION = "omara1-bakri"
BASE_URL = "https://sonarcloud.io/api"

def get_blocker_issues_with_details() -> List[Dict[str, Any]]:
    """Get all blocker issues with detailed information including file paths"""
    
    headers = {
        "Authorization": f"Bearer {SONAR_TOKEN}"
    }
    
    all_issues = []
    page = 1
    
    while True:
        params = {
            "componentKeys": PROJECT_KEY,
            "severities": "BLOCKER",
            "ps": 100,  # page size
            "p": page,
            "organization": ORGANIZATION,
            "resolved": "false"
        }
        
        response = requests.get(f"{BASE_URL}/issues/search", params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            break
            
        data = response.json()
        issues = data.get("issues", [])
        
        if not issues:
            break
            
        all_issues.extend(issues)
        
        # Check if there are more pages
        total = data.get("total", 0)
        if len(all_issues) >= total:
            break
            
        page += 1
    
    return all_issues

def categorize_issues(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize issues by rule"""
    categorized = {}
    
    for issue in issues:
        rule = issue.get("rule", "unknown")
        if rule not in categorized:
            categorized[rule] = []
        categorized[rule].append(issue)
    
    return categorized

def main():
    print("\n" + "="*60)
    print("DETAILED BLOCKER ISSUES FROM SONARCLOUD")
    print("="*60)
    
    issues = get_blocker_issues_with_details()
    
    if not issues:
        print("✅ No blocker issues found!")
        return
    
    print(f"\n📊 Total blocker issues: {len(issues)}")
    
    categorized = categorize_issues(issues)
    
    # Sort by count
    sorted_rules = sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True)
    
    print("\n🔍 Issues by Rule:")
    print("-" * 40)
    
    for rule, rule_issues in sorted_rules:
        print(f"\n📌 {rule}: {len(rule_issues)} issues")
        
        # Show first 5 files for each rule
        for i, issue in enumerate(rule_issues[:5]):
            component = issue.get("component", "").replace(PROJECT_KEY + ":", "")
            line = issue.get("line", "?")
            message = issue.get("message", "")[:80]
            print(f"   {i+1}. {component}:{line}")
            print(f"      {message}")
        
        if len(rule_issues) > 5:
            print(f"   ... and {len(rule_issues) - 5} more")
    
    # Save full details to JSON
    output_file = "sonarcloud/blocker_issues_detailed.json"
    with open(output_file, "w") as f:
        json.dump({
            "total": len(issues),
            "issues": issues,
            "categorized": {rule: [
                {
                    "file": issue.get("component", "").replace(PROJECT_KEY + ":", ""),
                    "line": issue.get("line", "?"),
                    "message": issue.get("message", ""),
                    "key": issue.get("key", "")
                } for issue in rule_issues
            ] for rule, rule_issues in categorized.items()}
        }, f, indent=2)
    
    print(f"\n💾 Full details saved to: {output_file}")

if __name__ == "__main__":
    main()