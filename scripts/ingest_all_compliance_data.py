"""
from __future__ import annotations

Full ingestion script for all compliance data into Neo4j.
Production-grade implementation with all manifests.
"""
import asyncio
import json
import os
from pathlib import Path
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv
import logging
from datetime import datetime
from typing import Dict, Any, List
logging.basicConfig(level=logging.INFO, format=
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

class ComplianceDataIngestion:
    """Production Neo4j ingestion for all compliance data."""

    def __init__(self):
        self.uri = 'bolt://localhost:7688'
        self.user = os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'ruleiq123')
        self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user,
            self.password))
        self.batch_size = 50
        self.stats = {'regulations_created': 0, 'relationships_created': 0,
            'enforcement_cases_created': 0, 'controls_created': 0, 'errors': [],
            }

    async def close(self) ->None:
        await self.driver.close()

    async def clear_database(self) ->None:
        """Clear all nodes and relationships."""
        logger.info('Clearing existing data...')
        async with self.driver.session() as session:
            await session.run('MATCH (n) DETACH DELETE n')
            logger.info('✓ Database cleared')

    async def create_indexes(self) ->None:
        """Create all necessary indexes for optimal performance."""
        logger.info('Creating indexes...')
        indexes = [
            'CREATE INDEX regulation_id IF NOT EXISTS FOR (r:Regulation) ON (r.id)'
            ,
            'CREATE INDEX regulation_title IF NOT EXISTS FOR (r:Regulation) ON (r.title)'
            ,
            'CREATE INDEX regulation_risk IF NOT EXISTS FOR (r:Regulation) ON (r.base_risk_score)'
            ,
            'CREATE INDEX enforcement_id IF NOT EXISTS FOR (e:Enforcement) ON (e.id)'
            ,
            'CREATE INDEX control_id IF NOT EXISTS FOR (c:Control) ON (c.id)',
            'CREATE INDEX trigger_industry IF NOT EXISTS FOR (t:BusinessTrigger) ON (t.industry)'
            ,
            'CREATE INDEX trigger_country IF NOT EXISTS FOR (t:BusinessTrigger) ON (t.country)',
            ]
        async with self.driver.session() as session:
            for index in indexes:
                try:
                    await session.run(index)
                except Exception as e:
                    if 'already exists' not in str(e):
                        logger.error('Index creation failed: %s' % e)
        logger.info('✓ Indexes created')

    async def ingest_enhanced_manifest(self, manifest_path: Path) ->int:
        """
        Ingest the enhanced compliance manifest with all metadata.

        Returns:
            Number of regulations created
        """
        logger.info('Ingesting enhanced manifest: %s' % manifest_path)
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        items = data.get('items', [])
        total_items = len(items)
        created = 0
        for i in range(0, total_items, self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_created = await self._ingest_regulation_batch(batch)
            created += batch_created
            logger.info('  Progress: %s/%s items' % (min(i + self.
                batch_size, total_items), total_items))
        self.stats['regulations_created'] = created
        logger.info('✓ Created %s regulations' % created)
        return created

    async def _ingest_regulation_batch(self, batch: List[Dict]) ->int:
        """Ingest a batch of regulations."""
        created = 0
        async with self.driver.session() as session:
            for item in batch:
                try:
                    query = """
                    MERGE (r:Regulation {id: $id})
                    SET r.title = $title,
                        r.url = $url,
                        r.category = $category,
                        r.tags = $tags,
                        r.priority = $priority,
                        r.base_risk_score = $risk_score,
                        r.automation_potential = $automation,
                        r.enforcement_frequency = $enforcement_freq,
                        r.max_penalty = $max_penalty,
                        r.implementation_complexity = $complexity,
                        r.typical_timeline = $timeline,
                        r.updated_at = datetime()
                    RETURN r
                    """
                    risk_meta = item.get('risk_metadata', {})
                    params = {'id': item.get('id'), 'title': item.get(
                        'title'), 'url': item.get('url'), 'category': item.
                        get('category', 'General'), 'tags': item.get('tags',
                        []), 'priority': item.get('priority', 3),
                        'risk_score': risk_meta.get('base_risk_score', 5),
                        'automation': item.get('automation_potential', 0.5),
                        'enforcement_freq': risk_meta.get(
                        'enforcement_frequency', 'medium'), 'max_penalty':
                        risk_meta.get('max_penalty', 'Unknown'),
                        'complexity': risk_meta.get(
                        'implementation_complexity', 5), 'timeline':
                        risk_meta.get('typical_implementation_timeline',
                        'Unknown')}
                    await session.run(query, params)
                    created += 1
                    if 'business_triggers' in item:
                        await self._create_business_triggers(session, item[
                            'id'], item['business_triggers'])
                    if 'suggested_controls' in item:
                        await self._create_controls(session, item['id'],
                            item['suggested_controls'])
                    if 'evidence_templates' in item:
                        await self._add_evidence_templates(session, item[
                            'id'], item['evidence_templates'])
                except Exception as e:
                    logger.error('Failed to ingest %s: %s' % (item.get('id'
                        ), e))
                    self.stats['errors'].append({'item': item.get('id'),
                        'error': str(e)})
        return created

    async def _create_business_triggers(self, session, reg_id: str,
        triggers: Dict):
        """Create business trigger nodes and relationships."""
        query = """
        MATCH (r:Regulation {id: $reg_id})
        MERGE (t:BusinessTrigger {
            industry: $industry,
            country: $country
        })
        MERGE (r)-[:APPLIES_TO]->(t)
        SET t.processes_payments = $processes_payments,
            t.stores_customer_data = $stores_customer_data,
            t.has_eu_customers = $has_eu_customers,
            t.annual_revenue = $annual_revenue,
            t.employee_count = $employee_count
        """
        params = {'reg_id': reg_id, 'industry': triggers.get('industry',
            'any'), 'country': triggers.get('country', 'Global'),
            'processes_payments': triggers.get('processes_payments'),
            'stores_customer_data': triggers.get('stores_customer_data'),
            'has_eu_customers': triggers.get('has_eu_customers'),
            'annual_revenue': triggers.get('annual_revenue'),
            'employee_count': triggers.get('employee_count')}
        await session.run(query, params)

    async def _create_controls(self, session, reg_id: str, controls: List[str]
        ):
        """Create control nodes and relationships."""
        for control_name in controls:
            query = """
            MATCH (r:Regulation {id: $reg_id})
            MERGE (c:Control {id: $control_id, name: $control_name})
            MERGE (r)-[:SUGGESTS_CONTROL]->(c)
            """
            params = {'reg_id': reg_id, 'control_id': control_name.lower().
                replace(' ', '_'), 'control_name': control_name}
            await session.run(query, params)
            self.stats['controls_created'] += 1

    async def _add_evidence_templates(self, session, reg_id: str, templates:
        List[str]):
        """Add evidence templates to regulation."""
        query = """
        MATCH (r:Regulation {id: $reg_id})
        SET r.evidence_templates = $templates
        """
        await session.run(query, {'reg_id': reg_id, 'templates': templates})

    async def ingest_uk_regulations(self, uk_path: Path) ->int:
        """Ingest UK-specific industry regulations."""
        if not uk_path.exists():
            logger.warning('UK regulations file not found: %s' % uk_path)
            return 0
        logger.info('Ingesting UK regulations: %s' % uk_path)
        with open(uk_path, 'r') as f:
            data = json.load(f)
        items = data.get('items', [])
        created = await self._ingest_regulation_batch(items)
        logger.info('✓ Created %s UK regulations' % created)
        return created

    async def ingest_enforcement_database(self, enforcement_path: Path) ->int:
        """Ingest enforcement cases and link to regulations."""
        if not enforcement_path.exists():
            logger.warning('Enforcement database not found: %s' %
                enforcement_path)
            return 0
        logger.info('Ingesting enforcement database: %s' % enforcement_path)
        with open(enforcement_path, 'r') as f:
            data = json.load(f)
        cases = data.get('enforcement_cases', [])
        created = 0
        async with self.driver.session() as session:
            for case in cases:
                try:
                    query = """
                    CREATE (e:Enforcement {
                        id: $id,
                        date: $date,
                        regulator: $regulator,
                        firm: $firm,
                        penalty_amount: $penalty,
                        violation_type: $violation,
                        jurisdiction: $jurisdiction,
                        outcome: $outcome
                    })
                    WITH e
                    UNWIND $regulations as reg_id
                    MATCH (r:Regulation {id: reg_id})
                    MERGE (r)-[:HAS_ENFORCEMENT]->(e)
                    RETURN e
                    """
                    params = {'id': case.get('case_id'), 'date': case.get(
                        'date'), 'regulator': case.get('regulator'), 'firm':
                        case.get('firm'), 'penalty': case.get(
                        'penalty_amount', 0), 'violation': case.get(
                        'violation_type'), 'jurisdiction': case.get(
                        'jurisdiction'), 'outcome': case.get('outcome'),
                        'regulations': case.get('related_regulations', [])}
                    await session.run(query, params)
                    created += 1
                except Exception as e:
                    logger.error('Failed to ingest enforcement %s: %s' % (
                        case.get('case_id'), e))
        self.stats['enforcement_cases_created'] = created
        logger.info('✓ Created %s enforcement cases' % created)
        return created

    async def ingest_regulatory_relationships(self, relationships_path: Path
        ) ->int:
        """Ingest relationships between regulations."""
        if not relationships_path.exists():
            logger.warning('Relationships file not found: %s' %
                relationships_path)
            return 0
        logger.info('Ingesting regulatory relationships: %s' %
            relationships_path)
        with open(relationships_path, 'r') as f:
            data = json.load(f)
        relationships = data.get('regulatory_relationships', {})
        created = 0
        async with self.driver.session() as session:
            for source_id, source_data in relationships.items():
                for rel in source_data.get('relationships', []):
                    try:
                        rel_type = rel.get('type', 'RELATES_TO').upper(
                            ).replace(' ', '_')
                        query = f"""
                        MATCH (source:Regulation {{id: $source_id}})
                        MATCH (target:Regulation {{id: $target_id}})
                        MERGE (source)-[r:{rel_type}]->(target)
                        SET r.strength = $strength,
                            r.control_overlap = $overlap,
                            r.description = $description
                        """
                        params = {'source_id': source_id, 'target_id': rel.
                            get('target'), 'strength': rel.get('strength', 
                            0.5), 'overlap': rel.get('control_overlap', 0),
                            'description': rel.get('description', '')}
                        await session.run(query, params)
                        created += 1
                    except Exception as e:
                        logger.error(
                            'Failed to create relationship %s -> %s: %s' %
                            (source_id, rel.get('target'), e))
        self.stats['relationships_created'] = created
        logger.info('✓ Created %s relationships' % created)
        return created

    async def verify_ingestion(self) ->None:
        """Verify the ingestion was successful."""
        logger.info('\nVerifying ingestion...')
        async with self.driver.session() as session:
            counts = {}
            for label in ['Regulation', 'Enforcement', 'Control',
                'BusinessTrigger']:
                result = await session.run(
                    f'MATCH (n:{label}) RETURN count(n) as count')
                record = await result.single()
                counts[label] = record['count']
            rel_result = await session.run(
                'MATCH ()-[r]->() RETURN count(r) as count')
            rel_record = await rel_result.single()
            counts['Relationships'] = rel_record['count']
            high_risk = await session.run(
                """
                MATCH (r:Regulation)
                WHERE r.base_risk_score >= 9
                RETURN r.title as title, r.base_risk_score as risk
                ORDER BY risk DESC
                LIMIT 5
            """,
                )
            logger.info('\n📊 INGESTION SUMMARY')
            logger.info('=' * 50)
            for label, count in counts.items():
                logger.info('  %s: %s' % (label, count))
            logger.info('\n🔴 High-Risk Regulations:')
            async for record in high_risk:
                logger.info('  - %s (risk: %s)' % (record['title'], record[
                    'risk']))
            logger.info('\n📈 Statistics:')
            logger.info('  Regulations created: %s' % self.stats[
                'regulations_created'])
            logger.info('  Relationships created: %s' % self.stats[
                'relationships_created'])
            logger.info('  Enforcement cases: %s' % self.stats[
                'enforcement_cases_created'])
            logger.info('  Controls mapped: %s' % self.stats[
                'controls_created'])
            logger.info('  Errors encountered: %s' % len(self.stats['errors']))

async def main() ->int:
    """Run the full compliance data ingestion."""
    start_time = datetime.now()
    ingestion = ComplianceDataIngestion()
    try:
        logger.info('🚀 Starting full compliance data ingestion...')
        logger.info('=' * 60)
        await ingestion.clear_database()
        await ingestion.create_indexes()
        manifest_path = Path(
            'data/manifests/compliance_ml_manifest_enhanced.json')
        if not manifest_path.exists():
            manifest_path = Path('data/manifests/compliance_ml_manifest.json')
        await ingestion.ingest_enhanced_manifest(manifest_path)
        uk_path = Path('data/manifests/uk_industry_regulations.json')
        await ingestion.ingest_uk_regulations(uk_path)
        enforcement_path = Path('data/enforcement/uk_enforcement_database.json',
            )
        await ingestion.ingest_enforcement_database(enforcement_path)
        relationships_path = Path(
            'data/manifests/regulatory_relationships.json')
        await ingestion.ingest_regulatory_relationships(relationships_path)
        await ingestion.verify_ingestion()
        duration = (datetime.now() - start_time).total_seconds()
        logger.info('\n✅ Ingestion completed in %s seconds!' % duration)
        if ingestion.stats['errors']:
            logger.warning('\n⚠️ %s errors occurred - check logs' % len(
                ingestion.stats['errors']))
    except Exception as e:
        logger.error('Critical failure: %s' % e)
        return 1
    finally:
        await ingestion.close()
    return 0

if __name__ == '__main__':
    exit(asyncio.run(main()))
