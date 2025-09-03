"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Ingest ISO framework obligations into Neo4j knowledge graph.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from neo4j import GraphDatabase

class ISOComplianceNeo4jIngestion:
    """Ingest ISO compliance data into Neo4j knowledge graph."""

    def __init__(self):
        """Initialize Neo4j connection using Doppler secrets."""
        neo4j_uri = os.popen(
            'doppler secrets get NEO4J_URI --plain 2>/dev/null').read().strip()
        neo4j_user = os.popen(
            'doppler secrets get NEO4J_USER --plain 2>/dev/null').read().strip(
            )
        neo4j_password = os.popen(
            'doppler secrets get NEO4J_PASSWORD --plain 2>/dev/null').read(
            ).strip()
        if not all([neo4j_uri, neo4j_user, neo4j_password]):
            neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7688')
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', 'ruleiq123')
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user,
            neo4j_password))
        logger.info('Connected to Neo4j at: %s' % neo4j_uri)

    def close(self) ->None:
        """Close Neo4j connection."""
        self.driver.close()

    def create_indexes(self) ->None:
        """Create indexes for ISO nodes."""
        with self.driver.session() as session:
            indexes = [
                'CREATE INDEX iso_framework_id IF NOT EXISTS FOR (f:ISOFramework) ON (f.framework_id)'
                ,
                'CREATE INDEX iso_clause_id IF NOT EXISTS FOR (c:ISOClause) ON (c.clause_id)'
                ,
                'CREATE INDEX iso_control_id IF NOT EXISTS FOR (c:ISOControl) ON (c.control_id)'
                ,
                'CREATE INDEX iso_obligation_id IF NOT EXISTS FOR (o:ISOObligation) ON (o.obligation_id)',
                ]
            for index in indexes:
                try:
                    session.run(index)
                    print(
                        f"Created index: {index.split('FOR')[1].split('ON')[0].strip()}",
                        )
                except (ValueError, KeyError, IndexError) as e:
                    logger.info('Index might already exist: %s' % e)

    def ingest_manifest(self, manifest_path: Path) ->None:
        """Ingest ISO compliance manifest into Neo4j."""
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        with self.driver.session() as session:
            meta_framework_query = """
                MERGE (mf:ComplianceFramework {name: 'ISO Standards Suite'})
                SET mf.created_at = $created_at,
                    mf.version = $version,
                    mf.total_obligations = $total_obligations,
                    mf.type = 'ISO',
                    mf.description = 'International Organization for Standardization management system standards'
                RETURN mf
            """
            session.run(meta_framework_query, created_at=manifest.get(
                'created_at', datetime.now().isoformat()), version=manifest
                .get('version', '1.0'), total_obligations=manifest.get(
                'total_obligations', 0))
            logger.info('Created ISO Standards Suite meta-framework node')
            for framework_name, framework_data in manifest['frameworks'].items(
                ):
                framework_query = """
                    MERGE (f:ISOFramework {framework_id: $framework_id})
                    SET f.name = $name,
                        f.title = $title,
                        f.version = $version,
                        f.control_count = $control_count,
                        f.mandatory_count = $mandatory_count,
                        f.status = 'active',
                        f.type = 'ISO'
                    RETURN f
                """
                session.run(framework_query, framework_id=framework_name.
                    replace(':', '_').replace(' ', '_'), name=
                    framework_name, title=framework_data['title'], version=
                    framework_data['version'], control_count=framework_data
                    ['control_count'], mandatory_count=framework_data[
                    'mandatory_count'])
                link_framework_query = """
                    MATCH (mf:ComplianceFramework {name: 'ISO Standards Suite'})
                    MATCH (f:ISOFramework {framework_id: $framework_id})
                    MERGE (mf)-[:INCLUDES_FRAMEWORK]->(f)
                """
                session.run(link_framework_query, framework_id=
                    framework_name.replace(':', '_').replace(' ', '_'))
                logger.info('Created ISO Framework node: %s' % framework_name)
                clauses = {}
                for obligation in framework_data['obligations']:
                    clause_num = obligation['clause']
                    clause_title = obligation['clause_title']
                    if clause_num not in clauses:
                        clauses[clause_num] = {'title': clause_title,
                            'controls': []}
                    clauses[clause_num]['controls'].append(obligation)
                for clause_num, clause_data in clauses.items():
                    clause_id = (
                        f"{framework_name.replace(':', '_').replace(' ', '_')}-Clause-{clause_num}",
                        )
                    clause_query = """
                        MERGE (c:ISOClause {clause_id: $clause_id})
                        SET c.number = $number,
                            c.title = $title,
                            c.framework = $framework,
                            c.control_count = $control_count
                        RETURN c
                    """
                    session.run(clause_query, clause_id=clause_id, number=
                        clause_num, title=clause_data['title'], framework=
                        framework_name, control_count=len(clause_data[
                        'controls']))
                    link_clause_query = """
                        MATCH (f:ISOFramework {framework_id: $framework_id})
                        MATCH (c:ISOClause {clause_id: $clause_id})
                        MERGE (f)-[:HAS_CLAUSE]->(c)
                    """
                    session.run(link_clause_query, framework_id=
                        framework_name.replace(':', '_').replace(' ', '_'),
                        clause_id=clause_id)
                    for control in clause_data['controls']:
                        control_query = """
                            MERGE (c:ISOControl {control_id: $control_id})
                            SET c.number = $number,
                                c.title = $title,
                                c.description = $description,
                                c.type = $type,
                                c.category = $category,
                                c.framework = $framework,
                                c.clause = $clause
                            RETURN c
                        """
                        session.run(control_query, control_id=control[
                            'obligation_id'], number=control['control_id'],
                            title=control['title'], description=control[
                            'description'], type=control['type'], category=
                            control['category'], framework=framework_name,
                            clause=clause_num)
                        obligation_query = """
                            MERGE (o:ISOObligation {obligation_id: $obligation_id})
                            SET o.control_id = $control_id,
                                o.title = $title,
                                o.description = $description,
                                o.compliance_level = $compliance_level,
                                o.framework = $framework,
                                o.clause = $clause,
                                o.category = $category,
                                o.type = 'ISO',
                                o.created_at = datetime()
                            RETURN o
                        """
                        session.run(obligation_query, obligation_id=control
                            ['obligation_id'], control_id=control[
                            'control_id'], title=control['title'],
                            description=control['description'],
                            compliance_level=control['compliance_level'],
                            framework=framework_name, clause=clause_num,
                            category=control['category'])
                        link_control_query = """
                            MATCH (cl:ISOClause {clause_id: $clause_id})
                            MATCH (co:ISOControl {control_id: $control_id})
                            MERGE (cl)-[:CONTAINS_CONTROL]->(co)
                        """
                        session.run(link_control_query, clause_id=clause_id,
                            control_id=control['obligation_id'])
                        link_obligation_query = """
                            MATCH (co:ISOControl {control_id: $control_id})
                            MATCH (o:ISOObligation {obligation_id: $obligation_id})
                            MERGE (co)-[:DEFINES_OBLIGATION]->(o)
                        """
                        session.run(link_obligation_query, control_id=
                            control['obligation_id'], obligation_id=control
                            ['obligation_id'])
            print(
                f"Created {manifest['total_obligations']} ISO control/obligation nodes",
                )

    def create_cross_framework_relationships(self) ->None:
        """Create relationships between related ISO frameworks."""
        with self.driver.session() as session:
            relationships = [('ISO_27001_2022', 'ISO_9001_2015',
                'COMPLEMENTS', 'Information security in quality management'
                ), ('ISO_27001_2022', 'ISO_22301_2019', 'COMPLEMENTS',
                'Information security in business continuity'), (
                'ISO_27001_2022', 'ISO_14001_2015', 'COMPLEMENTS',
                'Information security in environmental management'), (
                'ISO_27001_2022', 'ISO_45001_2018', 'COMPLEMENTS',
                'Information security in OH&S management'), (
                'ISO_9001_2015', 'ISO_22301_2019', 'SUPPORTS',
                'Quality foundation for business continuity'), (
                'ISO_9001_2015', 'ISO_14001_2015', 'SUPPORTS',
                'Quality foundation for environmental management'), (
                'ISO_9001_2015', 'ISO_45001_2018', 'SUPPORTS',
                'Quality foundation for OH&S management'), (
                'ISO_22301_2019', 'ISO_45001_2018', 'COMPLEMENTS',
                'Business continuity for safety incidents'), (
                'ISO_22301_2019', 'ISO_14001_2015', 'COMPLEMENTS',
                'Business continuity for environmental incidents'), (
                'ISO_14001_2015', 'ISO_45001_2018', 'INTEGRATES_WITH',
                'Environmental and occupational health integration')]
            for source, target, rel_type, description in relationships:
                rel_query = """
                    MATCH (f1:ISOFramework {framework_id: $source})
                    MATCH (f2:ISOFramework {framework_id: $target})
                    MERGE (f1)-[r:""" + rel_type + """]->(f2)
                    SET r.description = $description
                """
                session.run(rel_query, source=source, target=target,
                    description=description)
            logger.info('Created %s cross-framework relationships' % len(
                relationships))

    def create_common_controls(self) ->None:
        """Identify and link common controls across ISO standards."""
        with self.driver.session() as session:
            common_themes = [{'theme': 'Leadership and Commitment',
                'controls': ['5.1', '5.2', '5.3'], 'description':
                'Top management leadership requirements'}, {'theme':
                'Risk Management', 'controls': ['6.1', '6.1.1', '6.1.2',
                '8.2', '8.3'], 'description':
                'Risk assessment and treatment'}, {'theme':
                'Document Control', 'controls': ['7.5'], 'description':
                'Documented information management'}, {'theme':
                'Internal Audit', 'controls': ['9.2'], 'description':
                'Internal audit requirements'}, {'theme':
                'Management Review', 'controls': ['9.3'], 'description':
                'Management review requirements'}, {'theme':
                'Continual Improvement', 'controls': ['10.1', '10.2',
                '10.3'], 'description': 'Improvement and corrective action'}]
            for theme_data in common_themes:
                theme_query = """
                    MERGE (t:ISOCommonTheme {name: $name})
                    SET t.description = $description,
                        t.created_at = datetime()
                    RETURN t
                """
                session.run(theme_query, name=theme_data['theme'],
                    description=theme_data['description'])
                for control_pattern in theme_data['controls']:
                    link_theme_query = """
                        MATCH (t:ISOCommonTheme {name: $theme})
                        MATCH (c:ISOControl)
                        WHERE c.number STARTS WITH $control_pattern
                           OR c.number = $control_pattern
                        MERGE (c)-[:IMPLEMENTS_THEME]->(t)
                    """
                    session.run(link_theme_query, theme=theme_data['theme'],
                        control_pattern=control_pattern)
            logger.info('Created %s common control themes' % len(common_themes),
                )

    def link_iso_to_uk_regulations(self) ->None:
        """Create relationships between ISO standards and UK regulations."""
        with self.driver.session() as session:
            mappings = [{'iso': 'ISO_27001_2022', 'uk_pattern': 'GDPR',
                'relationship': 'SUPPORTS_COMPLIANCE', 'description':
                'ISO 27001 supports GDPR compliance'}, {'iso':
                'ISO_22301_2019', 'uk_pattern': 'FCA', 'relationship':
                'SUPPORTS_COMPLIANCE', 'description':
                'ISO 22301 supports FCA operational resilience'}, {'iso':
                'ISO_9001_2015', 'uk_pattern': 'FCA', 'relationship':
                'ENHANCES_COMPLIANCE', 'description':
                'ISO 9001 enhances FCA compliance quality'}, {'iso':
                'ISO_45001_2018', 'uk_pattern': 'HSWA', 'relationship':
                'SUPPORTS_COMPLIANCE', 'description':
                'ISO 45001 supports health and safety compliance'}, {'iso':
                'ISO_14001_2015', 'uk_pattern': 'Environment',
                'relationship': 'SUPPORTS_COMPLIANCE', 'description':
                'ISO 14001 supports environmental compliance'}]
            for mapping in mappings:
                map_query = """
                    MATCH (iso:ISOFramework {framework_id: $iso_id})
                    MATCH (uk:Regulation)
                    WHERE uk.name CONTAINS $uk_pattern
                    MERGE (iso)-[r:""" + mapping['relationship'] + """]->(uk)
                    SET r.description = $description
                """
                try:
                    session.run(map_query, iso_id=mapping['iso'],
                        uk_pattern=mapping['uk_pattern'], description=
                        mapping['description'])
                except (Exception, KeyError, IndexError):
                    pass
            logger.info('Created ISO to UK regulation mappings')

    def generate_statistics(self) ->None:
        """Generate and display graph statistics."""
        with self.driver.session() as session:
            stats_query = """
                MATCH (mf:ComplianceFramework {name: 'ISO Standards Suite'})
                MATCH (f:ISOFramework)
                MATCH (cl:ISOClause)
                MATCH (co:ISOControl)
                MATCH (o:ISOObligation)
                OPTIONAL MATCH (t:ISOCommonTheme)
                RETURN 
                    COUNT(DISTINCT mf) as meta_frameworks,
                    COUNT(DISTINCT f) as frameworks,
                    COUNT(DISTINCT cl) as clauses,
                    COUNT(DISTINCT co) as controls,
                    COUNT(DISTINCT o) as obligations,
                    COUNT(DISTINCT t) as themes
            """
            result = session.run(stats_query).single()
            logger.info('\n' + '=' * 80)
            logger.info('ISO FRAMEWORK NEO4J INGESTION COMPLETE')
            logger.info('=' * 80)
            logger.info('Meta-Frameworks: %s' % result['meta_frameworks'])
            logger.info('ISO Frameworks: %s' % result['frameworks'])
            logger.info('Clauses: %s' % result['clauses'])
            logger.info('Controls: %s' % result['controls'])
            logger.info('Obligations: %s' % result['obligations'])
            logger.info('Common Themes: %s' % result['themes'])
            rel_query = """
                MATCH ()-[r]->()
                WHERE TYPE(r) IN ['INCLUDES_FRAMEWORK', 'HAS_CLAUSE', 'CONTAINS_CONTROL', 
                                  'DEFINES_OBLIGATION', 'COMPLEMENTS', 'SUPPORTS', 
                                  'INTEGRATES_WITH', 'IMPLEMENTS_THEME', 'SUPPORTS_COMPLIANCE']
                RETURN TYPE(r) as type, COUNT(r) as count
                ORDER BY count DESC
            """
            logger.info('\nISO Relationships:')
            for record in session.run(rel_query):
                if record['count'] > 0:
                    logger.info('  - %s: %s' % (record['type'], record[
                        'count']))

def main() ->None:
    """Main ingestion process."""
    ingestion = ISOComplianceNeo4jIngestion()
    try:
        ingestion.create_indexes()
        manifest_path = Path(
            '/home/omar/Documents/ruleIQ/data/manifests/iso_compliance_manifest.json',
            )
        ingestion.ingest_manifest(manifest_path)
        ingestion.create_cross_framework_relationships()
        ingestion.create_common_controls()
        ingestion.link_iso_to_uk_regulations()
        ingestion.generate_statistics()
    finally:
        ingestion.close()

if __name__ == '__main__':
    main()
