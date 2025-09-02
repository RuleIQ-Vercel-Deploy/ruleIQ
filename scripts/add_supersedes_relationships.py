import os
"""
from __future__ import annotations

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

    async def close(self) ->None:
        await self.driver.close()

    async def create_supersedes_relationships(self) ->None:
        """Create SUPERSEDES relationships based on various patterns."""
        logger.info('Creating SUPERSEDES relationships...')
        async with self.driver.session() as session:
            created = 0
            created += await self._create_gdpr_supersessions(session)
            created += await self._create_version_supersessions(session)
            created += await self._create_brexit_supersessions(session)
            created += await self._create_industry_supersessions(session)
            logger.info('✅ Total SUPERSEDES relationships created: %s' %
                created)

    async def _create_gdpr_supersessions(self, session):
        """Create GDPR-related supersession relationships."""
        count = 0
        result = await session.run(
            """
            MATCH (new:Regulation)
            WHERE new.id CONTAINS 'gdpr' AND new.id CONTAINS '2016'
            MATCH (old:Regulation)
            WHERE old.id CONTAINS 'directive' AND old.id CONTAINS '95'
            MERGE (new)-[s:SUPERSEDES]->(old)
            SET s.description = 'GDPR replaced Data Protection Directive 95/46/EC',
                s.effective_date = date('2018-05-25'),
                s.created_at = datetime()
            RETURN new.id as new_reg, old.id as old_reg
        """,
            )
        async for record in result:
            count += 1
            logger.info('GDPR supersession: %s -> %s' % (record['new_reg'],
                record['old_reg']))
        return count

    async def _create_version_supersessions(self, session):
        """Create version-based supersession relationships."""
        count = 0
        result = await session.run(
            """
            MATCH (r:Regulation)
            WHERE r.id =~ '.*v[0-9]+.*' OR r.id =~ '.*20[0-9]{2}.*'
            RETURN r.id as id, r.title as title
            ORDER BY r.id
        """,
            )
        regulations = []
        async for record in result:
            regulations.append({'id': record['id'], 'title': record['title']})
        version_groups = {}
        for reg in regulations:
            base_name = re.sub('[-_]?(v[0-9]+|20[0-9]{2})', '', reg['id'])
            base_name = re.sub('[-_]+$', '', base_name)
            if base_name not in version_groups:
                version_groups[base_name] = []
            version_groups[base_name].append(reg)
        for base_name, regs in version_groups.items():
            if len(regs) > 1:
                sorted_regs = sorted(regs, key=lambda x: self.
                    _extract_version(x['id']))
                for i in range(len(sorted_regs) - 1):
                    older = sorted_regs[i]
                    newer = sorted_regs[i + 1]
                    result = await session.run(
                        """
                        MATCH (new:Regulation {id: $new_id})
                        MATCH (old:Regulation {id: $old_id})
                        MERGE (new)-[s:SUPERSEDES]->(old)
                        SET s.description = $description,
                            s.created_at = datetime()
                        RETURN new.id as new_reg, old.id as old_reg
                    """
                        , new_id=newer['id'], old_id=older['id'],
                        description=f'Newer version supersedes older version')
                    if await result.single():
                        count += 1
                        logger.info('Version supersession: %s -> %s' % (
                            newer['id'], older['id']))
        return count

    def _extract_version(self, reg_id: str):
        """Extract version number or year for sorting."""
        version_match = re.search('v([0-9]+)', reg_id)
        if version_match:
            return int(version_match.group(1))
        year_match = re.search('(20[0-9]{2})', reg_id)
        if year_match:
            return int(year_match.group(1))
        return 0

    async def _create_brexit_supersessions(self, session):
        """Create UK-specific post-Brexit supersession relationships."""
        count = 0
        result = await session.run(
            """
            MATCH (uk:Regulation)
            WHERE uk.id CONTAINS 'uk' AND uk.id CONTAINS 'gdpr'
            MATCH (eu:Regulation)
            WHERE eu.id CONTAINS 'gdpr' AND NOT eu.id CONTAINS 'uk'
            MERGE (uk)-[s:SUPERSEDES {context: 'UK'}]->(eu)
            SET s.description = 'UK GDPR supersedes EU GDPR for UK entities post-Brexit',
                s.effective_date = date('2021-01-01'),
                s.created_at = datetime()
            RETURN uk.id as uk_reg, eu.id as eu_reg
        """,
            )
        async for record in result:
            count += 1
            logger.info('Brexit supersession: %s -> %s' % (record['uk_reg'],
                record['eu_reg']))
        result = await session.run(
            """
            MATCH (new:Regulation)
            WHERE new.id CONTAINS 'data-protection' AND new.id CONTAINS '2018'
            MATCH (old:Regulation)
            WHERE old.id CONTAINS 'data-protection' AND old.id CONTAINS '1998'
            MERGE (new)-[s:SUPERSEDES]->(old)
            SET s.description = 'Data Protection Act 2018 replaced DPA 1998',
                s.effective_date = date('2018-05-25'),
                s.created_at = datetime()
            RETURN new.id as new_reg, old.id as old_reg
        """,
            )
        async for record in result:
            count += 1
            logger.info('DPA supersession: %s -> %s' % (record['new_reg'],
                record['old_reg']))
        return count

    async def _create_industry_supersessions(self, session):
        """Create industry-specific supersession relationships."""
        count = 0
        result = await session.run(
            """
            MATCH (r:Regulation)
            WHERE r.id CONTAINS 'pci' AND r.id CONTAINS 'dss'
            RETURN r.id as id
            ORDER BY r.id
        """,
            )
        pci_regs = []
        async for record in result:
            pci_regs.append(record['id'])
        if len(pci_regs) > 1:
            for i in range(len(pci_regs) - 1):
                result = await session.run(
                    """
                    MATCH (new:Regulation {id: $new_id})
                    MATCH (old:Regulation {id: $old_id})
                    WHERE new.id > old.id  // Newer versions have higher IDs
                    MERGE (new)-[s:SUPERSEDES]->(old)
                    SET s.description = 'PCI DSS version update',
                        s.created_at = datetime()
                    RETURN new.id as new_reg, old.id as old_reg
                """
                    , new_id=pci_regs[i + 1], old_id=pci_regs[i])
                if await result.single():
                    count += 1
                    logger.info('PCI DSS supersession: %s -> %s' % (
                        pci_regs[i + 1], pci_regs[i]))
        result = await session.run(
            """
            MATCH (new:Regulation)
            WHERE new.id CONTAINS 'iso' AND new.id CONTAINS '27001' AND new.id CONTAINS '2022'
            MATCH (old:Regulation)
            WHERE old.id CONTAINS 'iso' AND old.id CONTAINS '27001' AND old.id CONTAINS '2013'
            MERGE (new)-[s:SUPERSEDES]->(old)
            SET s.description = 'ISO 27001:2022 supersedes ISO 27001:2013',
                s.effective_date = date('2022-10-25'),
                s.created_at = datetime()
            RETURN new.id as new_reg, old.id as old_reg
        """,
            )
        async for record in result:
            count += 1
            logger.info('ISO supersession: %s -> %s' % (record['new_reg'],
                record['old_reg']))
        return count

    async def verify_supersedes_relationships(self) ->None:
        """Verify SUPERSEDES relationships have been created."""
        logger.info('\nVerifying SUPERSEDES relationships...')
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH ()-[s:SUPERSEDES]->()
                RETURN count(s) as count
            """,
                )
            count = await result.single()
            logger.info('Total SUPERSEDES relationships: %s' % count['count'])
            result = await session.run(
                """
                MATCH (new:Regulation)-[s:SUPERSEDES]->(old:Regulation)
                RETURN new.id as new_reg, old.id as old_reg, s.description as description
                LIMIT 5
            """,
                )
            logger.info('\nSample SUPERSEDES relationships:')
            async for record in result:
                logger.info('  %s -> %s' % (record['new_reg'], record[
                    'old_reg']))
                logger.info('    Description: %s' % record['description'])


async def main() ->None:
    """Main execution function."""
    neo4j_uri = 'bolt://localhost:7688'
    neo4j_user = 'neo4j'
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    if not neo4j_password:
        raise ValueError("NEO4J_PASSWORD environment variable not set. Configure via Doppler.")
    builder = SupersedesRelationshipBuilder(neo4j_uri, neo4j_user,
        neo4j_password)
    try:
        await builder.create_supersedes_relationships()
        await builder.verify_supersedes_relationships()
        logger.info('\n✅ SUPERSEDES relationship creation completed!')
    except Exception as e:
        logger.error('Error: %s' % e)
        import traceback
        traceback.print_exc()
    finally:
        await builder.close()


if __name__ == '__main__':
    asyncio.run(main())
