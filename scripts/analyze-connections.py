#!/usr/bin/env python3
"""
Analyze the actual connection status between frontend and backend.
"""

import json
import re
from pathlib import Path
from collections import Counter

def analyze_connections():
    """Analyze the connections in the HTML file."""
    
    # Read the HTML file
    with open('api-connection-map.html', 'r') as f:
        html_content = f.read()
    
    # Extract the connections array
    connections_match = re.search(r'const connections = (\[[\s\S]*?\]);', html_content)
    
    if not connections_match:
        print("ERROR: Could not find connections array")
        return
    
    connections = json.loads(connections_match.group(1))
    
    # Analyze connection statuses
    stats = Counter()
    connected_endpoints = []
    missing_endpoints = []
    unused_endpoints = []
    
    for conn in connections:
        status = conn.get('status', 'unknown')
        stats[status] += 1
        
        if status == 'connected':
            if conn.get('frontendDetails') and conn.get('backend'):
                connected_endpoints.append({
                    'frontend': f"{conn['frontendDetails'].get('method', 'N/A')} {conn['frontendDetails'].get('path', 'N/A')}",
                    'backend': f"{conn['backend'].get('method', 'N/A')} {conn['backend'].get('path', 'N/A')}",
                    'file': conn['frontendDetails'].get('file', 'N/A')
                })
        elif status == 'missing':
            if conn.get('frontendDetails'):
                missing_endpoints.append({
                    'frontend': f"{conn['frontendDetails'].get('method', 'N/A')} {conn['frontendDetails'].get('path', 'N/A')}",
                    'file': conn['frontendDetails'].get('file', 'N/A')
                })
        elif status == 'unused':
            if conn.get('backend'):
                unused_endpoints.append({
                    'backend': f"{conn['backend'].get('method', 'N/A')} {conn['backend'].get('path', 'N/A')}",
                    'summary': conn['backend'].get('summary', 'N/A')
                })
    
    # Print analysis
    print("=" * 80)
    print("API CONNECTION ANALYSIS")
    print("=" * 80)
    print(f"\nTotal connections mapped: {len(connections)}")
    print("\nConnection Status Breakdown:")
    print("-" * 40)
    for status, count in sorted(stats.items()):
        percentage = (count / len(connections)) * 100
        print(f"  {status:15} : {count:4} ({percentage:5.1f}%)")
    
    print("\n" + "=" * 80)
    print("CONNECTED ENDPOINTS (Frontend ↔ Backend)")
    print("=" * 80)
    if connected_endpoints:
        print(f"\nTotal connected: {len(connected_endpoints)}")
        print("\nFirst 20 connected endpoints:")
        for i, endpoint in enumerate(connected_endpoints[:20], 1):
            print(f"\n{i}. {endpoint['file']}")
            print(f"   Frontend: {endpoint['frontend']}")
            print(f"   Backend:  {endpoint['backend']}")
    else:
        print("\n❌ No connected endpoints found!")
    
    print("\n" + "=" * 80)
    print("MISSING BACKEND ENDPOINTS (Frontend → ???)")
    print("=" * 80)
    if missing_endpoints:
        print(f"\nTotal missing: {len(missing_endpoints)}")
        print("\nFirst 20 missing endpoints:")
        for i, endpoint in enumerate(missing_endpoints[:20], 1):
            print(f"\n{i}. {endpoint['file']}")
            print(f"   Frontend: {endpoint['frontend']}")
    
    print("\n" + "=" * 80)
    print("UNUSED BACKEND ENDPOINTS (??? ← Backend)")
    print("=" * 80)
    if unused_endpoints:
        print(f"\nTotal unused: {len(unused_endpoints)}")
        print("\nFirst 20 unused endpoints:")
        for i, endpoint in enumerate(unused_endpoints[:20], 1):
            print(f"\n{i}. {endpoint['backend']}")
            print(f"   Summary: {endpoint['summary']}")
    
    # Analyze why connections might not be working
    print("\n" + "=" * 80)
    print("CONNECTION ISSUES ANALYSIS")
    print("=" * 80)
    
    # Check for common path mismatches
    frontend_paths = set()
    backend_paths = set()
    
    for conn in connections:
        if conn.get('frontendDetails') and conn['frontendDetails'].get('path'):
            frontend_paths.add(conn['frontendDetails']['path'])
        if conn.get('backend') and conn['backend'].get('path'):
            backend_paths.add(conn['backend']['path'])
    
    print(f"\nUnique frontend paths: {len(frontend_paths)}")
    print(f"Unique backend paths: {len(backend_paths)}")
    
    # Find potential matches
    potential_matches = 0
    for f_path in frontend_paths:
        # Simple matching: remove /api/v1 prefix and compare
        f_normalized = f_path.replace('/api/v1/', '').replace('/api/', '')
        for b_path in backend_paths:
            b_normalized = b_path.replace('/api/v1/', '').replace('/api/', '')
            if f_normalized == b_normalized or f_normalized in b_normalized or b_normalized in f_normalized:
                potential_matches += 1
                break
    
    print(f"Potential matches (with normalization): {potential_matches}")
    
    return stats, connected_endpoints, missing_endpoints, unused_endpoints

if __name__ == "__main__":
    analyze_connections()