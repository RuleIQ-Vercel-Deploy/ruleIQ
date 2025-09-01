#!/usr/bin/env python3
"""
Add SUPERSEDES relationships based on regulation patterns.
This handles version updates and regulatory replacements.
"""

import asyncio
import logging
from neo4j import AsyncGraphDatabase
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupersedesRelationshipBuilder:
    """Build SUPERSEDES relationships between regulations."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
    
    async def close(self):
        await self.driver.close()
    
    async def create_supersedes_relationships(self):
        """Create SUPERSEDES relationships based on various patterns."""
        logger.info("Creating SUPERSEDES relationships...")
        
        async with self.driver.session() as session:
            created = 0
            
            # 1. GDPR supersession patterns
            created += await self._create_gdpr_supersessions(session)
            
            # 2. Version-based supersessions
            created += await self._create_version_supersessions(session)
            
            # 3. UK-specific post-Brexit supersessions
            created += await self._create_brexit_supersessions(session)
            
            # 4. Industry-specific updates
            created += await self._create_industry_supersessions(session)
            
            logger.info(f"✅ Total SUPERSEDES relationships created: {created}")
    
    async def _create_gdpr_supersessions(self, session):
        """Create GDPR-related supersession relationships."""
        count = 0
        
        # GDPR superseded Data Protection Directive
        result = await session.run("""
            MATCH (new:Regulation)
            WHERE new.id CONTAINS 'gdpr' AND new.id CONTAINS '2016'
            MATCH (old:Regulation)
            WHERE old.id CONTAINS 'directive' AND old.id CONTAINS '95'
            MERGE (new)-[s:SUPERSEDES]->(old)
            SET s.description = 'GDPR replaced Data Protection Directive 95/46/EC',
                s.effective_date = date('2018-05-25'),
                s.created_at = datetime()
            RETURN new.id as new_reg, old.id as old_reg
        """)
        
        async for record in result:
            count += 1
            logger.info(f"GDPR supersession: {record['new_reg']} -> {record['old_reg']}")
        
        return count
    
    async def _create_version_supersessions(self, session):
        """Create version-based supersession relationships."""
        count = 0
        
        # Find regulations with version numbers
        result = await session.run("""
            MATCH (r:Regulation)
            WHERE r.id =~ '.*v[0-9]+.*' OR r.id =~ '.*20[0-9]{2}.*'
            RETURN r.id as id, r.title as title
            ORDER BY r.id
        """)
        
        regulations = []
        async for record in result:
            regulations.append({
                'id': record['id'],
                'title': record['title']
            })
        
        # Group by base name and find version relationships
        version_groups = {}
        for reg in regulations:
            # Extract base name (without version)
            base_name = re.sub(r'[-_]?(v[0-9]+|20[0-9]{2})', '', reg['id'])
            base_name = re.sub(r'[-_]+$', '', base_name)  # Clean trailing separators
            
            if base_name not in version_groups:
                version_groups[base_name] = []
            version_groups[base_name].append(reg)
        
        # Create supersession relationships for version groups
        for base_name, regs in version_groups.items():
            if len(regs) > 1:
                # Sort by version/year
                sorted_regs = sorted(regs, key=lambda x: self._extract_version(x['id']))
                
                # Create supersession chain
                for i in range(len(sorted_regs) - 1):
                    older = sorted_regs[i]
                    newer = sorted_regs[i + 1]
                    
                    result = await session.run("""
                        MATCH (new:Regulation {id: $new_id})
                        MATCH (old:Regulation {id: $old_id})
                        MERGE (new)-[s:SUPERSEDES]->(old)
                        SET s.description = $description,
                            s.created_at = datetime()
                        RETURN new.id as new_reg, old.id as old_reg
                    """,
                    new_id=newer['id'],
                    old_id=older['id'],
                    description=f"Newer version supersedes older version")
                    
                    if await result.single():
                        count += 1
                        logger.info(f"Version supersession: {newer['id']} -> {older['id']}")
        
        return count
    
    def _extract_version(self, reg_id: str):
        """Extract version number or year for sorting."""
        # Try to extract version number (v1, v2, etc.)
        version_match = re.search(r'v([0-9]+)', reg_id)
        if version_match:
            return int(version_match.group(1))
        
        # Try to extract year
        year_match = re.search(r'(20[0-9]{2})', reg_id)
        if year_match:
            return int(year_match.group(1))
        
        return 0  # Default for no version found
    
    async def _create_brexit_supersessions(self, session):
        """Create UK-specific post-Brexit supersession relationships."""
        count = 0
        
        # UK GDPR supersedes EU GDPR for UK companies
        result = await session.run("""
            MATCH (uk:Regulation)
            WHERE uk.id CONTAINS 'uk' AND uk.id CONTAINS 'gdpr'
            MATCH (eu:Regulation)
            WHERE eu.id CONTAINS 'gdpr' AND NOT eu.id CONTAINS 'uk'
            MERGE (uk)-[s:SUPERSEDES {context: 'UK'}]->(eu)
            SET s.description = 'UK GDPR supersedes EU GDPR for UK entities post-Brexit',
                s.effective_date = date('2021-01-01'),
                s.created_at = datetime()
            RETURN uk.id as uk_reg, eu.id as eu_reg
        """)
        
        async for record in result:
            count += 1
            logger.info(f"Brexit supersession: {record['uk_reg']} -> {record['eu_reg']}")
        
        # UK Data Protection Act 2018 updates
        result = await session.run("""
            MATCH (new:Regulation)
            WHERE new.id CONTAINS 'data-protection' AND new.id CONTAINS '2018'
            MATCH (old:Regulation)
            WHERE old.id CONTAINS 'data-protection' AND old.id CONTAINS '1998'
            MERGE (new)-[s:SUPERSEDES]->(old)
            SET s.description = 'Data Protection Act 2018 replaced DPA 1998',
                s.effective_date = date('2018-05-25'),
                s.created_at = datetime()
            RETURN new.id as new_reg, old.id as old_reg
        """)
        
        async for record in result:
            count += 1
            logger.info(f"DPA supersession: {record['new_reg']} -> {record['old_reg']}")
        
        return count
    
    async def _create_industry_supersessions(self, session):
        """Create industry-specific supersession relationships."""
        count = 0
        
        # PCI DSS version updates
        result = await session.run("""
            MATCH (r:Regulation)
            WHERE r.id CONTAINS 'pci' AND r.id CONTAINS 'dss'
            RETURN r.id as id
            ORDER BY r.id
        """)
        
        pci_regs = []
        async for record in result:
            pci_regs.append(record['id'])
        
        # Create supersession chain for PCI DSS versions
        if len(pci_regs) > 1:
            for i in range(len(pci_regs) - 1):
                # Assume alphabetical order represents version progression
                result = await session.run("""
                    MATCH (new:Regulation {id: $new_id})
                    MATCH (old:Regulation {id: $old_id})
                    WHERE new.id > old.id  // Newer versions have higher IDs
                    MERGE (new)-[s:SUPERSEDES]->(old)
                    SET s.description = 'PCI DSS version update',
                        s.created_at = datetime()
                    RETURN new.id as new_reg, old.id as old_reg
                """,
                new_id=pci_regs[i+1],
                old_id=pci_regs[i])
                
                if await result.single():
                    count += 1
                    logger.info(f"PCI DSS supersession: {pci_regs[i+1]} -> {pci_regs[i]}")
        
        # ISO 27001 version updates
        result = await session.run("""
            MATCH (new:Regulation)
            WHERE new.id CONTAINS 'iso' AND new.id CONTAINS '27001' AND new.id CONTAINS '2022'
            MATCH (old:Regulation)
            WHERE old.id CONTAINS 'iso' AND old.id CONTAINS '27001' AND old.id CONTAINS '2013'
            MERGE (new)-[s:SUPERSEDES]->(old)
            SET s.description = 'ISO 27001:2022 supersedes ISO 27001:2013',
                s.effective_date = date('2022-10-25'),
                s.created_at = datetime()
            RETURN new.id as new_reg, old.id as old_reg
        """)
        
        async for record in result:
            count += 1
            logger.info(f"ISO supersession: {record['new_reg']} -> {record['old_reg']}")
        
        return count
    
    async def verify_supersedes_relationships(self):
        """Verify SUPERSEDES relationships have been created."""
        logger.info("\nVerifying SUPERSEDES relationships...")
        
        async with self.driver.session() as session:
            # Count SUPERSEDES relationships
            result = await session.run("""
                MATCH ()-[s:SUPERSEDES]->()
                RETURN count(s) as count
            """)
            count = await result.single()
            logger.info(f"Total SUPERSEDES relationships: {count['count']}")
            
            # Show sample SUPERSEDES relationships
            result = await session.run("""
                MATCH (new:Regulation)-[s:SUPERSEDES]->(old:Regulation)
                RETURN new.id as new_reg, old.id as old_reg, s.description as description
                LIMIT 5
            """)
            
            logger.info("\nSample SUPERSEDES relationships:")
            async for record in result:
                logger.info(f"  {record['new_reg']} -> {record['old_reg']}")
                logger.info(f"    Description: {record['description']}")


async def main():
    """Main execution function."""
    # Neo4j connection
    neo4j_uri = "bolt://localhost:7688"
    neo4j_user = "neo4j"
    neo4j_password = "ruleiq123"
    
    builder = SupersedesRelationshipBuilder(neo4j_uri, neo4j_user, neo4j_password)
    
    try:
        # Create SUPERSEDES relationships
        await builder.create_supersedes_relationships()
        
        # Verify results
        await builder.verify_supersedes_relationships()
        
        logger.info("\n✅ SUPERSEDES relationship creation completed!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await builder.close()


if __name__ == "__main__":
    asyncio.run(main())