"""
from __future__ import annotations

Fix Neo4j relationships and populate missing business_triggers.
This script addresses the warnings about missing relationship types and business_triggers.
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from neo4j import AsyncGraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jRelationshipFixer:
    """Fix missing relationships and business_triggers in Neo4j."""

    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self) ->None:
        await self.driver.close()
        """Close"""

    async def populate_business_triggers(self) ->None:
        """Populate business_triggers from manifest files."""
        logger.info('Starting business_triggers population...')
        uk_regs_path = Path('data/manifests/uk_industry_regulations.json')
        if uk_regs_path.exists():
            with open(uk_regs_path, 'r') as f:
                data = json.load(f)
            async with self.driver.session() as session:
                count = 0
                for item in data.get('items', []):
                    if 'business_triggers' in item:
                        result = await session.run(
                            """
                            MATCH (r:Regulation {id: $id})
                            SET r.business_triggers = $business_triggers
                            RETURN r.id as id
                        """
                            , id=item['id'], business_triggers=json.dumps(
                            item['business_triggers']))
                        if await result.single():
                            count += 1
                            logger.info('Updated %s with business_triggers' %
                                item['id'])
                logger.info(
                    '✅ Updated %s regulations with business_triggers' % count)
        await self._add_generic_business_triggers()

    async def _add_generic_business_triggers(self):
        """Add generic business_triggers based on tags for regulations without them."""
        logger.info('Adding generic business_triggers based on tags...')
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (r:Regulation)
                WHERE r.business_triggers IS NULL
                RETURN r.id as id, r.tags as tags, r.title as title
            """,
                )
            regulations = []
            async for record in result:
                regulations.append({'id': record['id'], 'tags': record[
                    'tags'], 'title': record['title']})
            logger.info('Found %s regulations without business_triggers' %
                len(regulations))
            for reg in regulations:
                triggers = self._generate_business_triggers(reg['tags'],
                    reg['title'])
                await session.run(
                    """
                    MATCH (r:Regulation {id: $id})
                    SET r.business_triggers = $business_triggers
                    RETURN r.id
                """
                    , id=reg['id'], business_triggers=json.dumps(triggers))
            logger.info(
                '✅ Added generic business_triggers to %s regulations' % len
                (regulations))

    def _generate_business_triggers(self, tags: List[str], title: str) ->Dict[
        str, Any]:
        """Generate business_triggers based on tags and title."""
        triggers = {}
        if 'finance' in tags or 'banking' in tags:
            triggers['industry'] = 'finance'
        elif 'healthcare' in tags or 'health' in tags:
            triggers['industry'] = 'healthcare'
        elif 'technology' in tags or 'tech' in tags:
            triggers['industry'] = 'technology'
        elif 'retail' in tags:
            triggers['industry'] = 'retail'
        else:
            triggers['industry'] = 'general'
        if 'UK' in tags:
            triggers['country'] = 'UK'
        elif 'EU' in tags or 'GDPR' in title:
            triggers['country'] = 'EU'
        elif 'US' in tags or 'California' in tags:
            triggers['country'] = 'US'
        else:
            triggers['country'] = 'global'
        if 'data' in tags or 'privacy' in tags or 'GDPR' in title:
            triggers['stores_customer_data'] = True
        if 'payment' in tags or 'PCI' in title:
            triggers['processes_payments'] = True
        if 'health' in tags or 'HIPAA' in title:
            triggers['handles_health_data'] = True
        if 'enterprise' in tags:
            triggers['employee_count'] = '>500'
        elif 'SME' in tags or 'small' in tags:
            triggers['employee_count'] = '<100'
        return triggers

    async def create_dependency_relationships(self) ->None:
        """Create DEPENDS_ON relationships between related regulations."""
        logger.info('Creating DEPENDS_ON relationships...')
        async with self.driver.session() as session:
            dependencies = [('gdpr-general', 'gdpr-article-6',
                'Article 6 depends on general GDPR'), ('gdpr-general',
                'gdpr-article-7', 'Article 7 depends on general GDPR'), (
                'gdpr-general', 'gdpr-article-32',
                'Article 32 depends on general GDPR'), ('pci-dss-general',
                'pci-dss-requirement-1', 'Requirement 1 depends on PCI DSS'
                ), ('pci-dss-general', 'pci-dss-requirement-2',
                'Requirement 2 depends on PCI DSS'), ('soc2-general',
                'soc2-security', 'Security principle depends on SOC 2'), (
                'soc2-general', 'soc2-availability',
                'Availability principle depends on SOC 2')]
            created = 0
            for parent_id, child_id, description in dependencies:
                result = await session.run(
                    """
                    MATCH (parent:Regulation)
                    WHERE parent.id CONTAINS $parent_pattern
                    MATCH (child:Regulation)
                    WHERE child.id CONTAINS $child_pattern
                    MERGE (child)-[d:DEPENDS_ON]->(parent)
                    SET d.description = $description,
                        d.created_at = datetime()
                    RETURN parent.id as parent, child.id as child
                """
                    , parent_pattern=parent_id, child_pattern=child_id,
                    description=description)
                async for record in result:
                    created += 1
                    logger.info('Created DEPENDS_ON: %s -> %s' % (record[
                        'child'], record['parent']))
            logger.info('✅ Created %s DEPENDS_ON relationships' % created)

    async def create_equivalence_relationships(self) ->None:
        """Create EQUIVALENT_TO relationships between similar regulations."""
        logger.info('Creating EQUIVALENT_TO relationships...')
        async with self.driver.session() as session:
            equivalences = [('gdpr', 'ccpa', 'privacy',
                'Both handle personal data protection'), ('gdpr',
                'uk-data-protection', 'privacy',
                'Similar data protection laws'), ('iso27001',
                'soc2-security', 'security',
                'Security management frameworks'), ('nist', 'iso27001',
                'security', 'Security control frameworks'), ('pci-dss',
                'psd2', 'payment', 'Payment security regulations')]
            created = 0
            for reg1_pattern, reg2_pattern, tag, description in equivalences:
                result = await session.run(
                    """
                    MATCH (r1:Regulation)
                    WHERE r1.id CONTAINS $pattern1 AND $tag IN r1.tags
                    MATCH (r2:Regulation)
                    WHERE r2.id CONTAINS $pattern2 AND $tag IN r2.tags
                    WITH r1, r2
                    WHERE id(r1) < id(r2)  // Avoid duplicates
                    MERGE (r1)-[e:EQUIVALENT_TO]-(r2)
                    SET e.description = $description,
                        e.similarity_score = 0.8,
                        e.created_at = datetime()
                    RETURN r1.id as reg1, r2.id as reg2
                """
                    , pattern1=reg1_pattern, pattern2=reg2_pattern, tag=tag,
                    description=description)
                async for record in result:
                    created += 1
                    logger.info('Created EQUIVALENT_TO: %s <-> %s' % (
                        record['reg1'], record['reg2']))
            logger.info('✅ Created %s EQUIVALENT_TO relationships' % created)

    async def create_supersedes_relationships(self) ->None:
        """Create SUPERSEDES relationships for regulations that replace older ones."""
        logger.info('Creating SUPERSEDES relationships...')
        async with self.driver.session() as session:
            supersessions = [('gdpr-general',
                'data-protection-directive-95',
                'GDPR replaced 1995 directive'), ('iso27001-2022',
                'iso27001-2013', '2022 version supersedes 2013'), (
                'pci-dss-v4', 'pci-dss-v3',
                'Version 4 supersedes Version 3'), ('uk-gdpr',
                'gdpr-general', 'UK GDPR supersedes EU GDPR post-Brexit', 'UK'),
                ]
            created = 0
            for new_pattern, old_pattern, description, *conditions in supersessions:
                query = """
                    MATCH (new:Regulation)
                    WHERE new.id CONTAINS $new_pattern
                    MATCH (old:Regulation)
                    WHERE old.id CONTAINS $old_pattern
                """
                params = {'new_pattern': new_pattern, 'old_pattern':
                    old_pattern, 'description': description}
                if conditions:
                    query += " AND 'UK' IN new.tags"
                query += """
                    MERGE (new)-[s:SUPERSEDES]->(old)
                    SET s.description = $description,
                        s.effective_date = datetime(),
                        s.created_at = datetime()
                    RETURN new.id as new_reg, old.id as old_reg
                """
                result = await session.run(query, **params)
                async for record in result:
                    created += 1
                    logger.info('Created SUPERSEDES: %s -> %s' % (record[
                        'new_reg'], record['old_reg']))
            logger.info('✅ Created %s SUPERSEDES relationships' % created)

    async def create_control_dependencies(self) ->None:
        """Create relationships between controls that depend on each other."""
        logger.info('Creating control dependency relationships...')
        async with self.driver.session() as session:
            control_deps = [('encryption_at_rest', 'key_management',
                'Encryption requires key management'), ('access_control',
                'authentication', 'Access control requires authentication'),
                ('audit_logging', 'log_management',
                'Audit logs require log management'), ('incident_response',
                'monitoring', 'Incident response requires monitoring'), (
                'backup', 'disaster_recovery',
                'Backup is part of disaster recovery')]
            created = 0
            for control1, control2, description in control_deps:
                result = await session.run(
                    """
                    MATCH (c1:Control)
                    WHERE c1.name CONTAINS $pattern1
                    MATCH (c2:Control)
                    WHERE c2.name CONTAINS $pattern2
                    MERGE (c1)-[d:DEPENDS_ON]->(c2)
                    SET d.description = $description,
                        d.created_at = datetime()
                    RETURN c1.name as control1, c2.name as control2
                """
                    , pattern1=control1, pattern2=control2, description=
                    description)
                async for record in result:
                    created += 1
                    logger.info('Control dependency: %s -> %s' % (record[
                        'control1'], record['control2']))
            logger.info('✅ Created %s control dependency relationships' %
                created)

    async def verify_relationships(self) ->None:
        """Verify all relationships have been created."""
        logger.info('\n' + '=' * 60)
        logger.info('RELATIONSHIP VERIFICATION')
        logger.info('=' * 60)
        async with self.driver.session() as session:
            result = await session.run(
                """
                CALL db.relationshipTypes() YIELD relationshipType
                RETURN relationshipType
            """,
                )
            rel_types = []
            async for record in result:
                rel_types.append(record['relationshipType'])
            logger.info('\nRelationship types found: %s' % rel_types)
            for rel_type in rel_types:
                result = await session.run(
                    f"""
                    MATCH ()-[r:{rel_type}]->()
                    RETURN count(r) as count
                """,
                    )
                count = await result.single()
                logger.info('  %s: %s relationships' % (rel_type, count[
                    'count']))
            result = await session.run(
                """
                MATCH (r:Regulation)
                RETURN 
                    count(r) as total,
                    count(r.business_triggers) as with_triggers
            """,
                )
            stats = await result.single()
            logger.info('\nBusiness triggers stats:')
            logger.info('  Total regulations: %s' % stats['total'])
            logger.info('  With business_triggers: %s' % stats['with_triggers'],
                )
            logger.info('  Coverage: %s%' % (stats['with_triggers'] / stats
                ['total'] * 100))
            result = await session.run(
                """
                MATCH (r:Regulation)
                WHERE r.business_triggers IS NOT NULL
                RETURN r.id as id, r.business_triggers as triggers
                LIMIT 3
            """,
                )
            logger.info('\nSample business_triggers:')
            async for record in result:
                triggers = json.loads(record['triggers'])
                logger.info('  %s: %s' % (record['id'], triggers))


async def main() ->None:
    """Main execution function."""
    neo4j_uri = 'bolt://localhost:7688'
    neo4j_user = 'neo4j'
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    if not neo4j_password:
        raise ValueError("NEO4J_PASSWORD environment variable not set. Configure via Doppler.")
    fixer = Neo4jRelationshipFixer(neo4j_uri, neo4j_user, neo4j_password)
    try:
        await fixer.populate_business_triggers()
        await fixer.create_dependency_relationships()
        await fixer.create_equivalence_relationships()
        await fixer.create_supersedes_relationships()
        await fixer.create_control_dependencies()
        await fixer.verify_relationships()
        logger.info('\n✅ All relationship fixes completed successfully!')
    except Exception as e:
        logger.error('Error: %s' % e)
        import traceback
        traceback.print_exc()
    finally:
        await fixer.close()


if __name__ == '__main__':
    asyncio.run(main())
