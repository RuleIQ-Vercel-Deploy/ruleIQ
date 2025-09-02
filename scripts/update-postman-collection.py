#!/usr/bin/env python3
"""
Update Postman collection to reflect the new consolidated API structure.
Based on the API alignment cleanup we performed.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# API endpoint mappings after consolidation
ENDPOINT_UPDATES = {
    # Removed endpoints (should be deleted from collection)
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
        # AI Assessments namespace update
        "/api/v1/ai-assessments": "/api/v1/ai/assessments",
        "/api/ai/assessments": "/api/v1/ai/assessments",
    },
}


def update_request_url(request: Dict[str, Any]) -> bool:
    """Update a single request URL if needed."""
    if "url" not in request:
        return False

    url = request["url"]
    if isinstance(url, dict) and "raw" in url:
        raw_url = url["raw"]
        updated = False

        # Check each update mapping
        for old_path, new_path in ENDPOINT_UPDATES["updated"].items():
            if old_path in raw_url:
                url["raw"] = raw_url.replace(old_path, new_path)

                # Update path array if present
                if "path" in url and isinstance(url["path"], list):
                    new_path_parts = new_path.strip("/").split("/")
                    url["path"] = new_path_parts

                print(f"  Updated: {old_path} -> {new_path}")
                updated = True
                break

        return updated

    return False


def should_remove_request(request: Dict[str, Any]) -> bool:
    """Check if a request should be removed."""
    if "url" not in request:
        return False

    url = request["url"]
    if isinstance(url, dict) and "raw" in url:
        raw_url = url["raw"]

        # Check if this endpoint should be removed
        for removed_path in ENDPOINT_UPDATES["removed"]:
            if (
                removed_path in raw_url
                and removed_path not in ENDPOINT_UPDATES["updated"]
            ):
                print(f"  Removing deprecated endpoint: {removed_path}")
                return True

    return False


def process_items(
    items: List[Dict[str, Any]], stats: Dict[str, int]
) -> List[Dict[str, Any]]:
    """Process collection items recursively."""
    updated_items = []

    for item in items:
        # Handle folders
        if "item" in item and isinstance(item["item"], list):
            print(f"\nProcessing folder: {item.get('name', 'Unnamed')}")
            item["item"] = process_items(item["item"], stats)
            if item["item"]:  # Only keep folders with items
                updated_items.append(item)

        # Handle requests
        elif "request" in item:
            if should_remove_request(item):
                stats["removed"] += 1
            else:
                if update_request_url(item):
                    stats["updated"] += 1
                else:
                    stats["unchanged"] += 1
                updated_items.append(item)

    return updated_items


def update_collection(input_file: str, output_file: str):
    """Update the Postman collection with new API structure."""
    print(f"Loading collection from: {input_file}")

    with open(input_file, "r") as f:
        collection = json.load(f)

    print(f"Collection: {collection['info']['name']}")
    print(f"Original schema: {collection['info'].get('schema', 'unknown')}")

    # Update collection info
    collection["info"][
        "name"
    ] = f"RuleIQ API Collection - Consolidated ({datetime.now().strftime('%Y-%m-%d')})"
    collection["info"]["description"] = (
        "Updated RuleIQ API collection after endpoint consolidation and cleanup.\n\n"
        "Changes:\n"
        "- Removed duplicate endpoints\n"
        "- Consolidated AI optimization endpoints\n"
        "- Updated namespace from /api/v1/ai-assessments to /api/v1/ai/assessments\n"
        "- Moved user/me to auth/me\n"
        "- Consolidated cache and circuit breaker endpoints under /api/v1/ai/optimization"
    )

    # Process all items
    stats = {"updated": 0, "removed": 0, "unchanged": 0}

    if "item" in collection:
        print("\nProcessing collection items...")
        collection["item"] = process_items(collection["item"], stats)

    # Save updated collection
    print(f"\nSaving updated collection to: {output_file}")
    with open(output_file, "w") as f:
        json.dump(collection, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("UPDATE SUMMARY")
    print("=" * 60)
    print(f"Updated endpoints: {stats['updated']}")
    print(f"Removed endpoints: {stats['removed']}")
    print(f"Unchanged endpoints: {stats['unchanged']}")
    print(f"Total processed: {sum(stats.values())}")

    return stats


def main():
    """Main entry point."""
    # Find the most suitable input collection (prioritize larger comprehensive collections)
    collections = [
        "ruleiq_postman_collection.json",  # 41K - standard collection
        "ruleiq_complete_collection.json",  # 76K
        "ruleiq_postman_collection_with_doppler.json",  # 11K
        "ruleiq_comprehensive_postman_collection_fixed.json",  # 141K - has JSON issues
        "ruleiq_comprehensive_postman_collection.json",  # 157K - has JSON issues
    ]

    input_file = None
    for collection in collections:
        if Path(collection).exists():
            input_file = collection
            break

    if not input_file:
        print("No Postman collection found!")
        return

    output_file = "ruleiq_postman_collection_consolidated.json"

    stats = update_collection(input_file, output_file)

    print(f"\n✅ Collection updated successfully!")
    print(f"📁 Output file: {output_file}")


if __name__ == "__main__":
    main()
