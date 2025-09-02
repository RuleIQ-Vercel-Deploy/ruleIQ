#!/usr/bin/env python3
"""
Enforcement Data Collector - Fetches real enforcement actions from regulatory bodies.
This provides REAL penalty data, not guesses.
"""

import asyncio
import aiohttp
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging
import re
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnforcementAPIClient:
    """Fetches real enforcement data from FCA, ICO, and other regulators."""

    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "ruleIQ Compliance Platform - Enforcement Monitor",
            "Accept": "application/json, application/xml, text/html",
            "Accept-Language": "en-GB,en;q=0.9",
        }

        # API endpoints for enforcement data
        self.endpoints = {
            "fca": {
                "base": "https://www.fca.org.uk",
                "enforcement": "/news/news-stories/enforcement-action",
                "api": "https://www.fca.org.uk/data/enforcement-data-api",
                "rss": "https://www.fca.org.uk/news/rss.xml",
            },
            "ico": {
                "base": "https://ico.org.uk",
                "enforcement": "/action-weve-taken/enforcement",
                "tracker": "https://ico.org.uk/about-the-ico/our-information/complaints-and-concerns-data-sets/gdpr-and-data-protection-complaints-and-concerns-data/",
                "api": "https://ico.org.uk/umbraco/api/Enforcement/GetEnforcementNotices",
            },
            "ofsi": {
                "base": "https://www.gov.uk",
                "list": "/government/publications/financial-sanctions-consolidated-list-of-targets",
                "penalties": "/government/collections/enforcement-of-financial-sanctions",
            },
            "pra": {
                "base": "https://www.bankofengland.co.uk",
                "enforcement": "/prudential-regulation/enforcement",
            },
        }

        # Cache directory for enforcement data
        self.cache_dir = Path("data/enforcement_actions")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def fetch_fca_enforcement(self, limit: int = 50) -> Dict[str, Any]:
        """
        Fetch FCA enforcement actions.

        Returns:
            Dict containing enforcement actions with real penalties
        """
        logger.info("Fetching FCA enforcement actions...")

        try:
            # Try the enforcement data API first
            async with self.session.get(
                self.endpoints["fca"]["api"],
                params={"limit": limit, "type": "enforcement"},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_fca_enforcement(data)
        except Exception as e:
            logger.warning(f"FCA API failed, trying web scraping: {e}")

        # Fallback to web scraping
        return await self._scrape_fca_enforcement()

    def _parse_fca_enforcement(self, data: Dict) -> Dict[str, Any]:
        """Parse FCA enforcement data."""
        actions = []

        for item in data.get("items", []):
            action = {
                "id": hashlib.md5(
                    f"fca_{item.get('reference', '')}".encode()
                ).hexdigest()[:16],
                "regulator": "FCA",
                "type": item.get("type", "enforcement"),
                "entity": item.get("firm_name", "Unknown"),
                "date": item.get("date_published", ""),
                "penalty_amount": self._extract_amount(item.get("penalty", "")),
                "violation": item.get("breach_description", ""),
                "regulation": item.get("regulation", ""),
                "action_taken": item.get("action", ""),
                "reference": item.get("reference", ""),
                "url": item.get("url", ""),
                "status": item.get("status", "final"),
            }

            # Extract specific regulation references
            action["regulations_violated"] = self._extract_regulation_refs(
                action["violation"] + " " + action["regulation"]
            )

            actions.append(action)

        return {
            "success": True,
            "source": "FCA",
            "count": len(actions),
            "actions": actions,
            "fetched_at": datetime.now().isoformat(),
        }

    async def _scrape_fca_enforcement(self) -> Dict[str, Any]:
        """Scrape FCA enforcement page if API fails."""
        actions = []

        try:
            url = self.endpoints["fca"]["base"] + self.endpoints["fca"]["enforcement"]
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Find enforcement notices
                    notices = soup.find_all("div", class_="news-item")

                    for notice in notices[:50]:  # Limit to 50 most recent
                        title = notice.find("h3")
                        link = notice.find("a", href=True)
                        date = notice.find("time")
                        summary = notice.find("p")

                        if title and link:
                            # Extract penalty amount from title/summary
                            text = title.text + " " + (summary.text if summary else "")
                            amount = self._extract_amount(text)

                            action = {
                                "id": hashlib.md5(link["href"].encode()).hexdigest()[
                                    :16
                                ],
                                "regulator": "FCA",
                                "type": "enforcement",
                                "entity": self._extract_entity_name(title.text),
                                "date": date.get("datetime", "") if date else "",
                                "penalty_amount": amount,
                                "violation": summary.text if summary else "",
                                "url": self.endpoints["fca"]["base"] + link["href"],
                                "status": "published",
                            }

                            actions.append(action)

        except Exception as e:
            logger.error(f"FCA scraping failed: {e}")

        return {
            "success": len(actions) > 0,
            "source": "FCA",
            "count": len(actions),
            "actions": actions,
            "fetched_at": datetime.now().isoformat(),
        }

    async def fetch_ico_enforcement(self, limit: int = 50) -> Dict[str, Any]:
        """
        Fetch ICO enforcement actions including GDPR penalties.

        Returns:
            Dict containing ICO enforcement actions
        """
        logger.info("Fetching ICO enforcement actions...")

        try:
            # Try ICO enforcement API
            async with self.session.get(
                self.endpoints["ico"]["api"], params={"pageSize": limit}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_ico_enforcement(data)
        except Exception as e:
            logger.warning(f"ICO API failed, trying alternative: {e}")

        # Fallback to scraping
        return await self._scrape_ico_enforcement()

    def _parse_ico_enforcement(self, data: Any) -> Dict[str, Any]:
        """Parse ICO enforcement data."""
        actions = []

        items = data if isinstance(data, list) else data.get("items", [])

        for item in items:
            action = {
                "id": hashlib.md5(f"ico_{item.get('id', '')}".encode()).hexdigest()[
                    :16
                ],
                "regulator": "ICO",
                "type": item.get("action_type", "monetary_penalty"),
                "entity": item.get("organisation_name", "Unknown"),
                "date": item.get("date_issued", ""),
                "penalty_amount": self._extract_amount(
                    str(item.get("penalty_amount", ""))
                ),
                "violation": item.get("breach_description", ""),
                "regulation": "GDPR" if "gdpr" in str(item).lower() else "DPA 2018",
                "articles_violated": item.get("articles", []),
                "sector": item.get("sector", ""),
                "reference": item.get("reference", ""),
                "url": item.get("url", ""),
                "status": item.get("status", "final"),
            }

            actions.append(action)

        return {
            "success": True,
            "source": "ICO",
            "count": len(actions),
            "actions": actions,
            "fetched_at": datetime.now().isoformat(),
        }

    async def _scrape_ico_enforcement(self) -> Dict[str, Any]:
        """Scrape ICO enforcement page."""
        actions = []

        try:
            url = self.endpoints["ico"]["base"] + self.endpoints["ico"]["enforcement"]
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Find enforcement entries
                    entries = soup.find_all(
                        ["article", "div"], class_=["enforcement-item", "search-result"]
                    )

                    for entry in entries[:50]:
                        title = entry.find(["h2", "h3"])
                        link = entry.find("a", href=True)

                        if title:
                            text = entry.get_text()
                            amount = self._extract_amount(text)

                            action = {
                                "id": hashlib.md5(
                                    f"ico_{title.text}".encode()
                                ).hexdigest()[:16],
                                "regulator": "ICO",
                                "type": (
                                    "monetary_penalty"
                                    if amount
                                    else "enforcement_notice"
                                ),
                                "entity": self._extract_entity_name(title.text),
                                "penalty_amount": amount,
                                "violation": self._extract_violation_type(text),
                                "regulation": "GDPR/DPA 2018",
                                "url": (
                                    self.endpoints["ico"]["base"] + link["href"]
                                    if link
                                    else ""
                                ),
                                "status": "published",
                            }

                            actions.append(action)

        except Exception as e:
            logger.error(f"ICO scraping failed: {e}")

        return {
            "success": len(actions) > 0,
            "source": "ICO",
            "count": len(actions),
            "actions": actions,
            "fetched_at": datetime.now().isoformat(),
        }

    async def fetch_all_enforcement(self) -> Dict[str, Any]:
        """
        Fetch enforcement data from all configured sources.

        Returns:
            Consolidated enforcement data from all regulators
        """
        all_actions = []
        sources = []

        # Fetch from each regulator
        tasks = [self.fetch_fca_enforcement(), self.fetch_ico_enforcement()]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, dict) and result.get("success"):
                all_actions.extend(result.get("actions", []))
                sources.append(result.get("source"))
                logger.info(
                    f"✅ Fetched {result.get('count')} actions from {result.get('source')}"
                )
            else:
                logger.error(f"❌ Failed to fetch from source: {result}")

        # Sort by date (most recent first)
        all_actions.sort(key=lambda x: x.get("date", ""), reverse=True)

        # Calculate statistics
        total_penalties = sum(
            action.get("penalty_amount", 0)
            for action in all_actions
            if isinstance(action.get("penalty_amount"), (int, float))
        )

        return {
            "success": True,
            "sources": sources,
            "total_actions": len(all_actions),
            "total_penalties": total_penalties,
            "actions": all_actions,
            "statistics": self._calculate_statistics(all_actions),
            "fetched_at": datetime.now().isoformat(),
        }

    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract monetary amount from text."""
        if not text:
            return None

        # Patterns for different currency formats
        patterns = [
            r"£([\d,]+(?:\.\d+)?)\s*(?:million|m)",  # £1.5 million
            r"£([\d,]+(?:\.\d+)?)\s*(?:billion|b)",  # £1.5 billion
            r"£([\d,]+(?:\.\d+)?)",  # £150,000
            r"€([\d,]+(?:\.\d+)?)",  # Euros
            r"\$([\d,]+(?:\.\d+)?)",  # Dollars
            r"([\d,]+(?:\.\d+)?)\s*(?:GBP|EUR|USD)",  # With currency code
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(",", "")
                try:
                    amount = float(amount_str)

                    # Handle millions/billions
                    if "million" in text.lower() or " m" in text.lower():
                        amount *= 1_000_000
                    elif "billion" in text.lower() or " b" in text.lower():
                        amount *= 1_000_000_000

                    return amount
                except ValueError:
                    continue

        return None

    def _extract_entity_name(self, text: str) -> str:
        """Extract entity name from enforcement text."""
        # Common patterns
        patterns = [
            r"(?:against|fined?|penalt\w+)\s+([A-Z][A-Za-z\s&]+(?:Ltd|Limited|LLP|plc|Bank|Insurance|Services))",
            r"^([A-Z][A-Za-z\s&]+(?:Ltd|Limited|LLP|plc))",
            r"([A-Z][A-Za-z\s&]+)\s+(?:fined|penalised)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        # Fallback: return first part before common separators
        return text.split(" - ")[0].split(" fined ")[0].strip()

    def _extract_violation_type(self, text: str) -> str:
        """Extract violation type from text."""
        violations = []

        # Common violation patterns
        violation_keywords = [
            "data breach",
            "security breach",
            "unauthorised access",
            "failure to report",
            "misleading",
            "market abuse",
            "money laundering",
            "terrorist financing",
            "sanctions breach",
            "unfair treatment",
            "systems and controls",
            "governance",
            "GDPR violation",
            "consent",
            "transparency",
            "accountability",
        ]

        text_lower = text.lower()
        for keyword in violation_keywords:
            if keyword in text_lower:
                violations.append(keyword)

        return ", ".join(violations) if violations else "Regulatory breach"

    def _extract_regulation_refs(self, text: str) -> List[str]:
        """Extract regulation references from text."""
        refs = []

        # Patterns for regulation references
        patterns = [
            r"(?:Article|Art\.?)\s+(\d+)",  # GDPR Articles
            r"(?:Section|Sec\.?|s\.)\s+(\d+)",  # Section references
            r"(?:Regulation|Reg\.?)\s+(\d+)",  # Regulation numbers
            r"(?:SYSC)\s+([\d.]+)",  # FCA SYSC rules
            r"(?:PRIN)\s+([\d.]+)",  # FCA Principles
            r"(?:SUP)\s+([\d.]+)",  # FCA SUP rules
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            refs.extend(matches)

        # Also check for named regulations
        if "GDPR" in text:
            refs.append("GDPR")
        if "MiFID" in text:
            refs.append("MiFID II")
        if "DPA" in text or "Data Protection Act" in text:
            refs.append("DPA 2018")

        return list(set(refs))  # Unique references

    def _calculate_statistics(self, actions: List[Dict]) -> Dict[str, Any]:
        """Calculate enforcement statistics."""
        stats = {
            "by_regulator": {},
            "by_type": {},
            "by_year": {},
            "top_penalties": [],
            "average_penalty": 0,
            "median_penalty": 0,
        }

        # Group by regulator
        for action in actions:
            regulator = action.get("regulator", "Unknown")
            stats["by_regulator"][regulator] = (
                stats["by_regulator"].get(regulator, 0) + 1
            )

            # Group by type
            action_type = action.get("type", "unknown")
            stats["by_type"][action_type] = stats["by_type"].get(action_type, 0) + 1

            # Group by year
            date = action.get("date", "")
            if date:
                year = date[:4]
                stats["by_year"][year] = stats["by_year"].get(year, 0) + 1

        # Calculate penalty statistics
        penalties = [
            action.get("penalty_amount", 0)
            for action in actions
            if isinstance(action.get("penalty_amount"), (int, float))
            and action.get("penalty_amount", 0) > 0
        ]

        if penalties:
            stats["average_penalty"] = sum(penalties) / len(penalties)
            sorted_penalties = sorted(penalties)
            mid = len(sorted_penalties) // 2
            stats["median_penalty"] = (
                sorted_penalties[mid]
                if len(sorted_penalties) % 2
                else (sorted_penalties[mid - 1] + sorted_penalties[mid]) / 2
            )

            # Top penalties
            stats["top_penalties"] = sorted(
                [
                    {
                        "entity": action.get("entity"),
                        "amount": action.get("penalty_amount"),
                        "regulator": action.get("regulator"),
                        "date": action.get("date"),
                    }
                    for action in actions
                    if isinstance(action.get("penalty_amount"), (int, float))
                    and action.get("penalty_amount", 0) > 0
                ],
                key=lambda x: x["amount"],
                reverse=True,
            )[:10]

        return stats

    async def save_to_cache(self, data: Dict[str, Any], filename: str = None):
        """Save enforcement data to cache."""
        if not filename:
            filename = f"enforcement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.cache_dir / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved enforcement data to {filepath}")
        return filepath


async def test_enforcement_collector():
    """Test the enforcement data collector."""
    async with EnforcementAPIClient() as client:
        logger.info("Testing enforcement data collection...")

        # Test individual sources
        logger.info("\n1. Testing FCA enforcement data...")
        fca_data = await client.fetch_fca_enforcement(limit=10)
        if fca_data["success"]:
            logger.info(f"✅ FCA: {fca_data['count']} actions fetched")
            if fca_data["actions"]:
                sample = fca_data["actions"][0]
                logger.info(
                    f"  Sample: {sample.get('entity')} - £{sample.get('penalty_amount', 0):,.0f}"
                )

        logger.info("\n2. Testing ICO enforcement data...")
        ico_data = await client.fetch_ico_enforcement(limit=10)
        if ico_data["success"]:
            logger.info(f"✅ ICO: {ico_data['count']} actions fetched")
            if ico_data["actions"]:
                sample = ico_data["actions"][0]
                logger.info(
                    f"  Sample: {sample.get('entity')} - £{sample.get('penalty_amount', 0):,.0f}"
                )

        # Test consolidated fetch
        logger.info("\n3. Testing consolidated enforcement fetch...")
        all_data = await client.fetch_all_enforcement()

        if all_data["success"]:
            logger.info(f"✅ Total actions: {all_data['total_actions']}")
            logger.info(f"✅ Total penalties: £{all_data['total_penalties']:,.0f}")
            logger.info(f"✅ Sources: {', '.join(all_data['sources'])}")

            # Show statistics
            stats = all_data["statistics"]
            logger.info("\nStatistics:")
            logger.info(f"  By regulator: {stats['by_regulator']}")
            logger.info(f"  Average penalty: £{stats['average_penalty']:,.0f}")

            if stats["top_penalties"]:
                logger.info("\n  Top 3 penalties:")
                for p in stats["top_penalties"][:3]:
                    logger.info(
                        f"    - {p['entity']}: £{p['amount']:,.0f} ({p['regulator']})"
                    )

            # Save to cache
            await client.save_to_cache(all_data)

            return all_data

        return None


if __name__ == "__main__":
    asyncio.run(test_enforcement_collector())
