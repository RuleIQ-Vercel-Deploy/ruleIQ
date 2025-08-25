#!/usr/bin/env python3
"""
Update the API connection map HTML file to reflect the new consolidated API structure.
Based on the API alignment cleanup we performed.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# API endpoint mappings after consolidation (same as Postman)
ENDPOINT_UPDATES = {
    # Removed endpoints (should be deleted from visualization)
    "removed": [
        "/api/v1/users/me",  # Use /api/v1/auth/me instead
        "/api/v1/ai-assessments/circuit-breaker/status",
        "/api/v1/ai-assessments/circuit-breaker/reset",
        "/api/v1/ai-assessments/cache/metrics",
        "/api/v1/chat/cache/metrics",
        "/api/v1/chat/quality/trends",
        "/api/ai/assessments",  # Legacy namespace
        "/api/v1/ai-assessments",  # Deprecated hyphenated namespace
    ],
    
    # Updated endpoints (new paths after consolidation)
    "updated": {
        # Auth consolidation
        "/api/v1/users/me": "/api/v1/auth/me",
        
        # AI Optimization consolidation
        "/api/v1/ai-assessments/circuit-breaker/status": "/api/v1/ai/optimization/circuit-breaker/status",
        "/api/v1/ai-assessments/circuit-breaker/reset": "/api/v1/ai/optimization/circuit-breaker/reset",
        "/api/v1/ai-assessments/cache/metrics": "/api/v1/ai/optimization/cache/metrics",
        "/api/v1/chat/cache/metrics": "/api/v1/ai/optimization/cache/metrics",
        
        # Evidence consolidation
        "/api/v1/chat/quality/trends": "/api/v1/evidence/quality/trends",
        
        # AI Assessments namespace update (hyphenated to slash-separated)
        "/api/v1/ai-assessments": "/api/v1/ai/assessments",
        "/api/ai/assessments": "/api/v1/ai/assessments",
    }
}

def update_connection_path(path: str) -> Optional[str]:
    """Update a single path if needed."""
    # Check for exact matches first
    if path in ENDPOINT_UPDATES["updated"]:
        return ENDPOINT_UPDATES["updated"][path]
    
    # Check for partial matches (handle paths with trailing parts)
    for old_path, new_path in ENDPOINT_UPDATES["updated"].items():
        if path.startswith(old_path):
            # Replace the base path while preserving any trailing parts
            trailing = path[len(old_path):]
            return new_path + trailing
    
    return None

def should_remove_connection(path: str) -> bool:
    """Check if a connection should be removed."""
    # Check if this endpoint should be removed
    for removed_path in ENDPOINT_UPDATES["removed"]:
        # Don't remove if it has an update mapping
        if removed_path in ENDPOINT_UPDATES["updated"]:
            continue
        if path == removed_path or path.startswith(removed_path + "/"):
            return True
    
    return False

def process_connections(connections: List[Dict[str, Any]], stats: Dict[str, int]) -> List[Dict[str, Any]]:
    """Process connections array and update paths."""
    updated_connections = []
    
    for conn in connections:
        # Check frontend path
        if conn.get("frontendDetails") and conn["frontendDetails"].get("path"):
            frontend_path = conn["frontendDetails"]["path"]
            
            if should_remove_connection(frontend_path):
                stats["removed"] += 1
                continue
            
            new_path = update_connection_path(frontend_path)
            if new_path:
                conn["frontendDetails"]["path"] = new_path
                # Update the frontend string as well
                if conn.get("frontend"):
                    parts = conn["frontend"].split(":")
                    if len(parts) >= 3:
                        parts[-1] = new_path
                        conn["frontend"] = ":".join(parts)
                stats["frontend_updated"] += 1
        
        # Check backend path
        if conn.get("backend") and conn["backend"].get("path"):
            backend_path = conn["backend"]["path"]
            
            if should_remove_connection(backend_path):
                # If backend is removed but frontend exists, mark as missing
                if conn.get("frontendDetails"):
                    conn["backend"] = None
                    conn["status"] = "missing"
                else:
                    # If both would be removed, skip the connection entirely
                    stats["removed"] += 1
                    continue
            else:
                new_path = update_connection_path(backend_path)
                if new_path:
                    conn["backend"]["path"] = new_path
                    stats["backend_updated"] += 1
        
        # Re-evaluate connection status after updates
        if conn.get("frontendDetails") and conn.get("backend"):
            # Check if paths now match
            frontend_path = conn["frontendDetails"]["path"]
            backend_path = conn["backend"]["path"]
            
            # Simple matching logic (could be improved)
            if frontend_path == backend_path:
                conn["status"] = "connected"
            elif frontend_path.replace("/api/v1", "") == backend_path.replace("/api/v1", ""):
                conn["status"] = "connected"
        
        updated_connections.append(conn)
    
    return updated_connections

def update_html_file(input_file: str, output_file: str):
    """Update the HTML file with new API structure."""
    print(f"Loading HTML from: {input_file}")
    
    with open(input_file, 'r') as f:
        html_content = f.read()
    
    # Extract the connections array from the JavaScript
    connections_match = re.search(r'const connections = (\[[\s\S]*?\]);', html_content)
    
    if not connections_match:
        print("ERROR: Could not find connections array in HTML")
        return None
    
    try:
        connections_str = connections_match.group(1)
        # Parse the JSON array
        connections = json.loads(connections_str)
        print(f"Found {len(connections)} connections")
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse connections JSON: {e}")
        return None
    
    # Process connections
    stats = {
        "frontend_updated": 0,
        "backend_updated": 0,
        "removed": 0,
        "unchanged": 0
    }
    
    updated_connections = process_connections(connections, stats)
    
    # Count unchanged
    stats["unchanged"] = len(updated_connections) - stats["frontend_updated"] - stats["backend_updated"]
    
    # Update the HTML with new connections
    updated_connections_str = json.dumps(updated_connections, indent=2)
    
    # Add update notice to the header
    update_notice = f"""
      <div style="background: #fef3c7; color: #92400e; padding: 10px; text-align: center; margin-top: 10px; border-radius: 6px;">
        <strong>Updated: {datetime.now().strftime('%Y-%m-%d')}</strong> - API structure consolidated with {stats['frontend_updated'] + stats['backend_updated']} endpoint updates
      </div>"""
    
    # Replace the connections array
    # Find the position of the connections array
    start_match = re.search(r'const connections = \[', html_content)
    end_match = re.search(r'\];\s*let currentFilter', html_content)
    
    if start_match and end_match:
        # Replace the connections array content
        updated_html = (
            html_content[:start_match.start()] +
            f'const connections = {updated_connections_str};\n    ' +
            html_content[end_match.start() + 2:]  # Skip the '];' part
        )
    else:
        print("WARNING: Could not find exact positions for replacement, using original HTML")
        updated_html = html_content
    
    # Add update notice after the header h1
    updated_html = re.sub(
        r'(<h1>.*?</h1>\s*<p>.*?</p>)',
        r'\1' + update_notice,
        updated_html
    )
    
    # Update the title to reflect consolidation
    updated_html = re.sub(
        r'<title>.*?</title>',
        f'<title>RuleIQ API Connection Map - Consolidated ({datetime.now().strftime("%Y-%m-%d")})</title>',
        updated_html
    )
    
    # Save updated HTML
    print(f"\nSaving updated HTML to: {output_file}")
    with open(output_file, 'w') as f:
        f.write(updated_html)
    
    return stats

def main():
    """Main entry point."""
    input_file = "api-connection-map.html"
    output_file = "api-connection-map-consolidated.html"
    
    if not Path(input_file).exists():
        print(f"ERROR: {input_file} not found!")
        return
    
    stats = update_html_file(input_file, output_file)
    
    if stats:
        print("\n" + "=" * 60)
        print("UPDATE SUMMARY")
        print("=" * 60)
        print(f"Frontend paths updated: {stats['frontend_updated']}")
        print(f"Backend paths updated: {stats['backend_updated']}")
        print(f"Connections removed: {stats['removed']}")
        print(f"Unchanged connections: {stats['unchanged']}")
        print(f"Total processed: {sum(stats.values()) - stats['unchanged']}")
        
        print(f"\n✅ HTML visualization updated successfully!")
        print(f"📁 Output file: {output_file}")

if __name__ == "__main__":
    main()