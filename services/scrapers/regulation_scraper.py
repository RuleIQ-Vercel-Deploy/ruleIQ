#!/usr/bin/env python3
"""
Regulation content scraper using Crawl4AI (borrowed from Archon).
Scrapes actual regulation content from URLs in our manifests.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generator import DefaultMarkdownGenerator
from neo4j import AsyncGraphDatabase
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegulationScraper:
    """Scrapes regulation content from official URLs."""
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.driver = AsyncGraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.markdown_generator = DefaultMarkdownGenerator()
        self.crawler = None
        self.scraped_dir = Path("data/scraped_regulations")
        self.scraped_dir.mkdir(parents=True, exist_ok=True)
        
    async def initialize(self):
        """Initialize the crawler."""
        self.crawler = AsyncWebCrawler(verbose=False)
        await self.crawler.start()
        
    async def close(self):
        """Close connections."""
        if self.crawler:
            await self.crawler.close()
        await self.driver.close()
    
    def _get_wait_selector(self, url: str) -> str:
        """Get appropriate wait selector based on site type."""
        url_lower = url.lower()
        
        # UK Legislation sites
        if 'legislation.gov.uk' in url_lower:
            return '.LegSnippet, .LegClearFix, #viewLegContents'
        # ICO (UK Information Commissioner)
        elif 'ico.org.uk' in url_lower:
            return '.main-content, .content, article'
        # EUR-Lex (EU legislation)
        elif 'eur-lex.europa.eu' in url_lower:
            return '#TexteOnly, .eli-main-title, #document1'
        # FCA Handbook
        elif 'handbook.fca.org.uk' in url_lower:
            return '.handbook-content, .rule-content, #content'
        # US regulations
        elif 'ecfr.gov' in url_lower or 'govinfo.gov' in url_lower:
            return '.content, .generated-content, #main-content'
        # NIST
        elif 'nist.gov' in url_lower:
            return '.page-content, #main-content, .text-content'
        # Generic fallback
        else:
            return 'body'
    
    async def scrape_regulation(self, regulation_id: str, url: str, retry_count: int = 3) -> Dict[str, Any]:
        """
        Scrape a single regulation's content.
        
        Returns:
            Dict with success status, content, and extracted data
        """
        logger.info(f"Scraping {regulation_id}: {url}")
        
        # Check if already scraped
        cache_file = self.scraped_dir / f"{regulation_id}.json"
        if cache_file.exists():
            logger.info(f"Using cached content for {regulation_id}")
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        last_error = None
        
        for attempt in range(retry_count):
            try:
                if not self.crawler:
                    await self.initialize()
                
                # Configure crawler for regulation sites
                wait_selector = self._get_wait_selector(url)
                crawl_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS if attempt > 0 else CacheMode.ENABLED,
                    markdown_generator=self.markdown_generator,
                    wait_for=wait_selector,
                    wait_until='domcontentloaded',
                    page_timeout=45000,  # 45 seconds
                    delay_before_return_html=1.0,
                    scan_full_page=True,
                    remove_overlay_elements=True,
                    process_iframes=True
                )
                
                logger.info(f"Attempt {attempt + 1}/{retry_count} for {url}")
                result = await self.crawler.arun(url=url, config=crawl_config)
                
                if not result.success:
                    last_error = f"Failed to crawl: {result.error_message}"
                    logger.warning(last_error)
                    if attempt < retry_count - 1:
                        await asyncio.sleep(2 ** attempt)
                    continue
                
                # Extract content and requirements
                scraped_data = {
                    "success": True,
                    "regulation_id": regulation_id,
                    "url": url,
                    "scraped_at": datetime.now().isoformat(),
                    "title": result.metadata.get('title', ''),
                    "description": result.metadata.get('description', ''),
                    "content_length": len(result.markdown),
                    "content_hash": hashlib.md5(result.markdown.encode()).hexdigest(),
                    "extracted_requirements": self._extract_requirements(result.markdown),
                    "extracted_controls": self._extract_controls(result.markdown),
                    "extracted_penalties": self._extract_penalties(result.markdown),
                    "extracted_deadlines": self._extract_deadlines(result.markdown),
                    "raw_markdown": result.markdown[:5000]  # Store first 5000 chars for analysis
                }
                
                # Cache the result
                with open(cache_file, 'w') as f:
                    json.dump(scraped_data, f, indent=2)
                
                logger.info(f"Successfully scraped {regulation_id}: {scraped_data['content_length']} chars")
                return scraped_data
                
            except Exception as e:
                last_error = f"Exception: {str(e)}"
                logger.error(f"Error scraping {url}: {last_error}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2 ** attempt)
        
        # All attempts failed
        return {
            "success": False,
            "regulation_id": regulation_id,
            "url": url,
            "error": last_error
        }
    
    def _extract_requirements(self, content: str) -> List[Dict[str, str]]:
        """Extract requirements from regulation content."""
        requirements = []
        
        # Common requirement patterns
        patterns = [
            r'(?:shall|must|required to|obligated to)\s+([^.]+)',
            r'(?:Article|Section|Clause)\s+\d+[:\s]+([^.]+(?:shall|must)[^.]+)',
            r'(?:The\s+(?:controller|processor|organization|entity))\s+(?:shall|must)\s+([^.]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:10]:  # Limit to first 10 per pattern
                requirements.append({
                    "text": match.strip()[:500],  # Truncate long requirements
                    "type": "mandatory"
                })
        
        return requirements
    
    def _extract_controls(self, content: str) -> List[str]:
        """Extract suggested controls from regulation content."""
        controls = []
        
        # Control keywords
        control_keywords = [
            'access control', 'encryption', 'audit', 'monitoring', 'logging',
            'authentication', 'authorization', 'backup', 'recovery', 'incident response',
            'risk assessment', 'security policy', 'training', 'awareness',
            'data minimization', 'retention', 'disposal', 'consent', 'privacy'
        ]
        
        content_lower = content.lower()
        for keyword in control_keywords:
            if keyword in content_lower:
                controls.append(keyword.replace(' ', '_'))
        
        return list(set(controls))  # Unique controls
    
    def _extract_penalties(self, content: str) -> List[Dict[str, Any]]:
        """Extract penalty information from regulation content."""
        penalties = []
        
        # Penalty patterns
        penalty_patterns = [
            r'(?:fine[sd]?|penalt(?:y|ies))\s+(?:of\s+)?(?:up\s+to\s+)?([£€$]\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|[MmBb]))?)',
            r'([£€$]\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|[MmBb]))?)\s+(?:fine|penalty)',
            r'(?:maximum|max)\s+(?:fine|penalty)\s+(?:of\s+)?([£€$]\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|[MmBb]))?)',
            r'(\d+(?:\.\d+)?%)\s+of\s+(?:annual\s+)?(?:global\s+)?(?:turnover|revenue)',
        ]
        
        for pattern in penalty_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:5]:  # Limit to first 5
                penalties.append({
                    "amount": match,
                    "type": "financial"
                })
        
        # Criminal penalties
        if re.search(r'imprison(?:ment|ed)', content, re.IGNORECASE):
            penalties.append({
                "type": "criminal",
                "description": "Potential imprisonment"
            })
        
        return penalties
    
    def _extract_deadlines(self, content: str) -> List[Dict[str, str]]:
        """Extract compliance deadlines from regulation content."""
        deadlines = []
        
        # Date patterns
        date_patterns = [
            r'(?:by|before|effective|from|starting)\s+(\d{1,2}\s+\w+\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(?:within\s+)?(\d+)\s+(?:days|months|years)',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:5]:  # Limit to first 5
                deadlines.append({
                    "date_text": match,
                    "type": "compliance_deadline"
                })
        
        return deadlines
    
    async def scrape_all_regulations(self, batch_size: int = 5):
        """Scrape all regulations from manifests."""
        # Load all manifest files
        manifest_dir = Path("data/manifests")
        all_regulations = []
        
        for manifest_file in manifest_dir.glob("*.json"):
            with open(manifest_file, 'r') as f:
                data = json.load(f)
                if 'items' in data:
                    for item in data['items']:
                        if 'url' in item and item['url']:
                            all_regulations.append({
                                'id': item['id'],
                                'url': item['url'],
                                'title': item.get('title', 'Unknown')
                            })
        
        logger.info(f"Found {len(all_regulations)} regulations to scrape")
        
        # Scrape in batches
        results = []
        for i in range(0, len(all_regulations), batch_size):
            batch = all_regulations[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(all_regulations)-1)//batch_size + 1}")
            
            tasks = []
            for reg in batch:
                tasks.append(self.scrape_regulation(reg['id'], reg['url']))
            
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
            # Update Neo4j with scraped data
            await self._update_neo4j_with_scraped_data(batch_results)
            
            # Small delay between batches
            if i + batch_size < len(all_regulations):
                await asyncio.sleep(2)
        
        # Generate summary report
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        report = {
            "total_regulations": len(all_regulations),
            "successful_scrapes": successful,
            "failed_scrapes": failed,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        with open("data/scraping_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Scraping complete: {successful}/{len(all_regulations)} successful")
        return report
    
    async def _update_neo4j_with_scraped_data(self, scraped_results: List[Dict[str, Any]]):
        """Update Neo4j with scraped regulation data."""
        async with self.driver.session() as session:
            for result in scraped_results:
                if not result['success']:
                    continue
                
                # Update regulation with scraped data
                await session.run("""
                    MATCH (r:Regulation {id: $id})
                    SET r.content_scraped = true,
                        r.content_length = $content_length,
                        r.content_hash = $content_hash,
                        r.scraped_at = $scraped_at,
                        r.has_requirements = $has_requirements,
                        r.has_penalties = $has_penalties,
                        r.requirement_count = $requirement_count,
                        r.control_count = $control_count
                    RETURN r.id
                """,
                id=result['regulation_id'],
                content_length=result['content_length'],
                content_hash=result['content_hash'],
                scraped_at=result['scraped_at'],
                has_requirements=len(result['extracted_requirements']) > 0,
                has_penalties=len(result['extracted_penalties']) > 0,
                requirement_count=len(result['extracted_requirements']),
                control_count=len(result['extracted_controls']))
                
                # Create requirement nodes
                for req in result['extracted_requirements'][:10]:  # Limit to 10 requirements
                    await session.run("""
                        MATCH (r:Regulation {id: $reg_id})
                        MERGE (req:Requirement {
                            text: $text,
                            regulation_id: $reg_id
                        })
                        MERGE (r)-[:HAS_REQUIREMENT]->(req)
                        SET req.type = $type
                    """,
                    reg_id=result['regulation_id'],
                    text=req['text'],
                    type=req['type'])
                
                # Update control relationships
                for control in result['extracted_controls']:
                    await session.run("""
                        MATCH (r:Regulation {id: $reg_id})
                        MERGE (c:Control {name: $control})
                        MERGE (r)-[:SUGGESTS_CONTROL]->(c)
                    """,
                    reg_id=result['regulation_id'],
                    control=control)
                
                logger.info(f"Updated Neo4j for {result['regulation_id']}")


async def test_single_regulation():
    """Test scraping a single regulation."""
    # Neo4j connection
    neo4j_uri = "bolt://localhost:7688"
    neo4j_user = "neo4j"
    neo4j_password = "ruleiq123"
    
    scraper = RegulationScraper(neo4j_uri, neo4j_user, neo4j_password)
    
    try:
        await scraper.initialize()
        
        # Test with a single UK regulation
        test_urls = [
            ("uk-gdpr", "https://www.legislation.gov.uk/ukpga/2018/12/contents"),
            ("uk-human-rights", "https://www.legislation.gov.uk/ukpga/2000/8/contents"),
            ("uk-money-laundering", "https://www.legislation.gov.uk/uksi/2017/692/contents"),
        ]
        
        for reg_id, url in test_urls[:1]:  # Test first one
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing scraper with: {url}")
            result = await scraper.scrape_regulation(reg_id, url, retry_count=2)
            
            if result['success']:
                logger.info(f"✅ Successfully scraped {reg_id}")
                logger.info(f"  Content length: {result['content_length']}")
                logger.info(f"  Requirements found: {len(result['extracted_requirements'])}")
                logger.info(f"  Penalties found: {len(result['extracted_penalties'])}")
                logger.info(f"  Controls identified: {len(result['extracted_controls'])}")
                logger.info(f"  Deadlines found: {len(result['extracted_deadlines'])}")
                
                # Show sample requirements
                if result['extracted_requirements']:
                    logger.info("\n  Sample requirements:")
                    for req in result['extracted_requirements'][:3]:
                        logger.info(f"    - {req['text'][:100]}...")
                        
                # Show penalties
                if result['extracted_penalties']:
                    logger.info("\n  Penalties found:")
                    for penalty in result['extracted_penalties'][:3]:
                        logger.info(f"    - {penalty}")
            else:
                logger.error(f"❌ Failed to scrape {reg_id}: {result.get('error')}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await scraper.close()


async def main():
    """Main execution function."""
    # For testing, just run the single test
    await test_single_regulation()


if __name__ == "__main__":
    asyncio.run(main())