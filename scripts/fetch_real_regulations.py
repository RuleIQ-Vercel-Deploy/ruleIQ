#!/usr/bin/env python3
"""
Fetch real regulation data from official APIs and update Neo4j with actual requirements and penalties.
This replaces our guessed/generated data with real compliance requirements.
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from services.api.regulation_api_client import RegulationAPIClient
from neo4j import AsyncGraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegulationDataFetcher:
    """Fetches real regulation data and updates Neo4j."""

    def __init__(self):
        self.neo4j_uri = "bolt://localhost:7688"
        self.neo4j_user = "neo4j"
        self.neo4j_password = "ruleiq123"
        self.driver = AsyncGraphDatabase.driver(
            self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
        )

    async def close(self):
        """Close connections."""
        await self.driver.close()

    async def get_uk_legislation_urls(self) -> List[Dict[str, str]]:
        """Get all UK legislation URLs from manifests."""
        urls = []
        manifest_dir = Path("data/manifests")

        # Find all manifest files
        for manifest_file in manifest_dir.glob("*.json"):
            with open(manifest_file, "r") as f:
                data = json.load(f)

                if "items" in data:
                    for item in data["items"]:
                        if "url" in item and item["url"]:
                            url = item["url"]
                            # Check if it's a legislation.gov.uk URL
                            if "legislation.gov.uk" in url:
                                urls.append(
                                    {
                                        "id": item["id"],
                                        "url": url,
                                        "title": item.get("title", "Unknown"),
                                        "manifest": manifest_file.name,
                                    }
                                )

        logger.info(f"Found {len(urls)} UK legislation URLs")
        return urls

    async def fetch_and_update_regulation(
        self, reg_info: Dict[str, str], client: RegulationAPIClient
    ) -> Dict[str, Any]:
        """Fetch regulation data and update Neo4j."""
        logger.info(f"Processing {reg_info['id']}: {reg_info['url']}")

        # Fetch regulation data
        result = await client.fetch_uk_legislation(reg_info["url"])

        if not result["success"]:
            logger.error(f"Failed to fetch {reg_info['id']}: {result.get('error')}")
            return {
                "id": reg_info["id"],
                "success": False,
                "error": result.get("error"),
            }

        # Update Neo4j with real data
        async with self.driver.session() as session:
            # Update regulation node with real data
            await session.run(
                """
                MATCH (r:Regulation {id: $id})
                SET r.has_real_data = true,
                    r.real_requirements_count = $req_count,
                    r.real_penalties_count = $penalty_count,
                    r.real_controls = $controls,
                    r.data_fetched_at = $fetched_at,
                    r.real_title = $title,
                    r.real_description = $description
                RETURN r.id
            """,
                id=reg_info["id"],
                req_count=len(result["requirements"]),
                penalty_count=len(result["penalties"]),
                controls=result["controls"],
                fetched_at=result["fetched_at"],
                title=result["metadata"]["title"],
                description=result["metadata"]["description"],
            )

            # Create real requirement nodes
            for req in result["requirements"][:10]:  # Limit to 10 per regulation
                await session.run(
                    """
                    MATCH (r:Regulation {id: $reg_id})
                    MERGE (req:RealRequirement {
                        text: $text,
                        regulation_id: $reg_id
                    })
                    MERGE (r)-[:HAS_REAL_REQUIREMENT]->(req)
                    SET req.type = $type,
                        req.keywords = $keywords,
                        req.provision_id = $provision_id
                """,
                    reg_id=reg_info["id"],
                    text=req["text"][:500],  # Truncate long text
                    type=req["type"],
                    keywords=req.get("keywords", []),
                    provision_id=req.get("id", ""),
                )

            # Create real penalty nodes
            for penalty in result["penalties"][:5]:  # Limit to 5 per regulation
                penalty_text = json.dumps(penalty)
                await session.run(
                    """
                    MATCH (r:Regulation {id: $reg_id})
                    MERGE (p:RealPenalty {
                        description: $description,
                        regulation_id: $reg_id
                    })
                    MERGE (r)-[:HAS_REAL_PENALTY]->(p)
                    SET p.type = $type,
                        p.amount = $amount
                """,
                    reg_id=reg_info["id"],
                    description=penalty_text[:500],
                    type=penalty["type"],
                    amount=penalty.get("amount", "Not specified"),
                )

            # Update enforcement info if available
            if result.get("enforcement"):
                await session.run(
                    """
                    MATCH (r:Regulation {id: $id})
                    SET r.enforcement_authorities = $authorities,
                        r.enforcement_powers = $powers
                """,
                    id=reg_info["id"],
                    authorities=result["enforcement"].get("authority", []),
                    powers=result["enforcement"].get("powers", [])[:3],
                )  # Limit to 3

        logger.info(
            f"✅ Updated {reg_info['id']} with {len(result['requirements'])} requirements, {len(result['penalties'])} penalties"
        )

        return {
            "id": reg_info["id"],
            "success": True,
            "requirements": len(result["requirements"]),
            "penalties": len(result["penalties"]),
            "controls": len(result["controls"]),
        }

    async def process_all_regulations(self, batch_size: int = 5, resume_from: int = 0):
        """Process all UK legislation URLs with checkpoint support."""
        urls = await self.get_uk_legislation_urls()

        if not urls:
            logger.warning("No UK legislation URLs found")
            return

        # Load checkpoint if exists
        checkpoint_file = Path("data/regulation_fetch_checkpoint.json")
        if checkpoint_file.exists() and resume_from == 0:
            with open(checkpoint_file, "r") as f:
                checkpoint = json.load(f)
                resume_from = checkpoint.get("last_batch_index", 0)
                logger.info(f"Resuming from batch {resume_from//batch_size + 1}")

        results = []
        async with RegulationAPIClient() as client:
            # Process in batches starting from resume point
            for i in range(resume_from, len(urls), batch_size):
                batch = urls[i : i + batch_size]
                logger.info(
                    f"\nProcessing batch {i//batch_size + 1}/{(len(urls)-1)//batch_size + 1}"
                )

                # Process batch concurrently
                tasks = [self.fetch_and_update_regulation(reg, client) for reg in batch]
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)

                # Save checkpoint after each batch
                with open(checkpoint_file, "w") as f:
                    json.dump(
                        {
                            "last_batch_index": i + batch_size,
                            "total_processed": i + len(batch),
                            "total_urls": len(urls),
                        },
                        f,
                    )

                # Small delay between batches
                if i + batch_size < len(urls):
                    await asyncio.sleep(2)

        # Generate report
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_processed": len(results),
            "successful": successful,
            "failed": failed,
            "results": results,
        }

        # Save report
        with open("data/real_regulation_fetch_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"\n{'='*60}")
        logger.info(f"Fetching complete: {successful}/{len(results)} successful")
        logger.info(f"Report saved to data/real_regulation_fetch_report.json")

        return report


async def main():
    """Main execution."""
    fetcher = RegulationDataFetcher()

    try:
        logger.info("Starting real regulation data fetch...")
        logger.info("This will replace generated data with actual legal requirements")

        report = await fetcher.process_all_regulations(batch_size=3)

        if report:
            logger.info(
                f"\n✅ Successfully fetched real data for {report['successful']} regulations"
            )
            logger.info("The ruleIQ platform now has REAL compliance requirements!")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await fetcher.close()


if __name__ == "__main__":
    asyncio.run(main())
