"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Initialize Neo4j compliance graph with CCO compliance playbook data
"""

import os
import sys
import time
from typing import Optional
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'please_change')


class ComplianceGraphInitializer:
    """Initialize Neo4j with compliance graph data."""

    def __init__(self, uri: str, username: str, password: str):
        self.driver = None
        self.uri = uri
        self.username = username
        self.password = password

    def connect(self, max_retries: int=5) ->bool:
        """Connect to Neo4j with retries."""
        for attempt in range(max_retries):
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=(self.
                    username, self.password))
                with self.driver.session() as session:
                    result = session.run('RETURN 1 as test')
                    result.single()
                logger.info('✅ Connected to Neo4j successfully')
                return True
            except ServiceUnavailable:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    logger.info('⏳ Neo4j not ready, waiting %s seconds...' %
                        wait_time)
                    time.sleep(wait_time)
                else:
                    logger.info('❌ Failed to connect to Neo4j at %s' % self.uri,
                        )
                    return False
            except Exception as e:
                logger.info('❌ Error connecting to Neo4j: %s' % str(e))
                return False
        return False

    def clear_database(self) ->None:
        """Clear all existing data from the database."""
        logger.info('🗑️  Clearing existing data...')
        with self.driver.session() as session:
            session.run('MATCH (n) DETACH DELETE n')
            logger.info('✅ Database cleared')

    def create_constraints(self) ->None:
        """Create uniqueness constraints for the graph."""
        logger.info('🔧 Creating constraints...')
        constraints = [
            'CREATE CONSTRAINT domain_id IF NOT EXISTS FOR (d:Domain) REQUIRE d.id IS UNIQUE'
            ,
            'CREATE CONSTRAINT jurisdiction_id IF NOT EXISTS FOR (j:Jurisdiction) REQUIRE j.id IS UNIQUE'
            ,
            'CREATE CONSTRAINT regulation_id IF NOT EXISTS FOR (r:Regulation) REQUIRE r.id IS UNIQUE'
            ,
            'CREATE CONSTRAINT requirement_id IF NOT EXISTS FOR (req:Requirement) REQUIRE req.id IS UNIQUE'
            ,
            'CREATE CONSTRAINT control_id IF NOT EXISTS FOR (c:Control) REQUIRE c.id IS UNIQUE'
            ,
            'CREATE CONSTRAINT metric_id IF NOT EXISTS FOR (m:Metric) REQUIRE m.id IS UNIQUE',
            ]
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.info('   Note: %s' % str(e))
        logger.info('✅ Constraints created')

    def create_compliance_data(self) ->None:
        """Create compliance graph with domains, jurisdictions, regulations, etc."""
        logger.info('📊 Creating compliance graph data...')
        with self.driver.session() as session:
            logger.info('   Creating domains...')
            domains = [{'id': 'privacy', 'name': 'Privacy', 'description':
                'Data privacy and protection'}, {'id': 'security', 'name':
                'Security', 'description':
                'Information security and cybersecurity'}, {'id':
                'governance', 'name': 'Governance', 'description':
                'Corporate governance and compliance'}, {'id': 'financial',
                'name': 'Financial', 'description':
                'Financial compliance and reporting'}, {'id': 'operational',
                'name': 'Operational', 'description':
                'Operational compliance and standards'}]
            for domain in domains:
                session.run(
                    'MERGE (d:Domain {id: $id}) SET d.name = $name, d.description = $description'
                    , **domain)
            logger.info('   Creating jurisdictions...')
            jurisdictions = [{'id': 'us', 'name': 'United States', 'code':
                'US'}, {'id': 'eu', 'name': 'European Union', 'code': 'EU'},
                {'id': 'uk', 'name': 'United Kingdom', 'code': 'UK'}, {'id':
                'ca', 'name': 'Canada', 'code': 'CA'}, {'id': 'global',
                'name': 'Global', 'code': 'GLOBAL'}]
            for jurisdiction in jurisdictions:
                session.run(
                    'MERGE (j:Jurisdiction {id: $id}) SET j.name = $name, j.code = $code'
                    , **jurisdiction)
            logger.info('   Creating regulations...')
            regulations = [{'id': 'gdpr', 'name': 'GDPR', 'full_name':
                'General Data Protection Regulation', 'domain': 'privacy',
                'jurisdiction': 'eu', 'effective_date': '2018-05-25'}, {
                'id': 'ccpa', 'name': 'CCPA', 'full_name':
                'California Consumer Privacy Act', 'domain': 'privacy',
                'jurisdiction': 'us', 'effective_date': '2020-01-01'}, {
                'id': 'hipaa', 'name': 'HIPAA', 'full_name':
                'Health Insurance Portability and Accountability Act',
                'domain': 'privacy', 'jurisdiction': 'us', 'effective_date':
                '1996-08-21'}, {'id': 'iso27001', 'name': 'ISO 27001',
                'full_name':
                'ISO/IEC 27001 Information Security Management', 'domain':
                'security', 'jurisdiction': 'global', 'effective_date':
                '2013-10-01'}, {'id': 'soc2', 'name': 'SOC 2', 'full_name':
                'Service Organization Control 2', 'domain': 'security',
                'jurisdiction': 'us', 'effective_date': '2017-01-01'}, {
                'id': 'pci_dss', 'name': 'PCI DSS', 'full_name':
                'Payment Card Industry Data Security Standard', 'domain':
                'security', 'jurisdiction': 'global', 'effective_date':
                '2004-12-01'}, {'id': 'sox', 'name': 'SOX', 'full_name':
                'Sarbanes-Oxley Act', 'domain': 'financial', 'jurisdiction':
                'us', 'effective_date': '2002-07-30'}, {'id': 'mifid2',
                'name': 'MiFID II', 'full_name':
                'Markets in Financial Instruments Directive II', 'domain':
                'financial', 'jurisdiction': 'eu', 'effective_date':
                '2018-01-03'}]
            for regulation in regulations:
                session.run(
                    """
                    MERGE (r:Regulation {id: $id})
                    SET r.name = $name, 
                        r.full_name = $full_name,
                        r.effective_date = date($effective_date)
                    WITH r
                    MATCH (d:Domain {id: $domain})
                    MERGE (r)-[:BELONGS_TO]->(d)
                    WITH r
                    MATCH (j:Jurisdiction {id: $jurisdiction})
                    MERGE (r)-[:APPLIES_IN]->(j)
                    """
                    , **regulation)
            logger.info('   Creating requirements...')
            requirements = [{'id': 'gdpr_consent', 'regulation': 'gdpr',
                'article': 'Article 7', 'name': 'Consent Requirements',
                'description':
                'Organizations must obtain freely given, specific, informed consent'
                }, {'id': 'gdpr_dpo', 'regulation': 'gdpr', 'article':
                'Article 37', 'name': 'Data Protection Officer',
                'description':
                'Designate a DPO when processing operations require regular monitoring'
                }, {'id': 'gdpr_breach', 'regulation': 'gdpr', 'article':
                'Article 33', 'name': 'Breach Notification', 'description':
                'Notify supervisory authority within 72 hours of breach awareness'
                }, {'id': 'iso_risk', 'regulation': 'iso27001', 'article':
                'Clause 6.1', 'name': 'Risk Assessment', 'description':
                'Identify and assess information security risks'}, {'id':
                'iso_access', 'regulation': 'iso27001', 'article': 'A.9',
                'name': 'Access Control', 'description':
                'Limit access to information and information processing facilities'
                }, {'id': 'soc2_security', 'regulation': 'soc2', 'article':
                'CC6', 'name': 'Security Principle', 'description':
                'Protection against unauthorized access'}, {'id':
                'soc2_availability', 'regulation': 'soc2', 'article': 'A1',
                'name': 'Availability Principle', 'description':
                'System availability for operation and use'}]
            for requirement in requirements:
                session.run(
                    """
                    MERGE (req:Requirement {id: $id})
                    SET req.name = $name,
                        req.article = $article,
                        req.description = $description
                    WITH req
                    MATCH (r:Regulation {id: $regulation})
                    MERGE (req)-[:REQUIRED_BY]->(r)
                    """
                    , **requirement)
            logger.info('   Creating controls...')
            controls = [{'id': 'ctrl_consent_mgmt', 'name':
                'Consent Management System', 'type': 'Technical',
                'description':
                'Automated consent collection and management',
                'requirements': ['gdpr_consent']}, {'id':
                'ctrl_access_mgmt', 'name': 'Access Management System',
                'type': 'Technical', 'description':
                'Role-based access control implementation', 'requirements':
                ['iso_access', 'soc2_security']}, {'id': 'ctrl_breach_proc',
                'name': 'Breach Response Procedure', 'type':
                'Administrative', 'description':
                'Documented breach notification process', 'requirements': [
                'gdpr_breach']}, {'id': 'ctrl_risk_assess', 'name':
                'Risk Assessment Process', 'type': 'Administrative',
                'description': 'Regular risk assessment and treatment',
                'requirements': ['iso_risk']}, {'id': 'ctrl_monitoring',
                'name': 'System Monitoring', 'type': 'Technical',
                'description': '24/7 system availability monitoring',
                'requirements': ['soc2_availability']}]
            for control in controls:
                req_ids = control.pop('requirements')
                session.run(
                    """
                    MERGE (c:Control {id: $id})
                    SET c.name = $name,
                        c.type = $type,
                        c.description = $description
                    """
                    , **control)
                for req_id in req_ids:
                    session.run(
                        """
                        MATCH (c:Control {id: $control_id})
                        MATCH (req:Requirement {id: $req_id})
                        MERGE (c)-[:SATISFIES]->(req)
                        """
                        , control_id=control['id'], req_id=req_id)
            logger.info('   Creating metrics...')
            metrics = [{'id': 'metric_consent_rate', 'name':
                'Consent Collection Rate', 'type': 'Percentage', 'target': 
                100, 'control': 'ctrl_consent_mgmt'}, {'id':
                'metric_breach_time', 'name': 'Breach Notification Time',
                'type': 'Hours', 'target': 72, 'control':
                'ctrl_breach_proc'}, {'id': 'metric_access_review', 'name':
                'Access Review Frequency', 'type': 'Days', 'target': 90,
                'control': 'ctrl_access_mgmt'}, {'id': 'metric_uptime',
                'name': 'System Uptime', 'type': 'Percentage', 'target': 
                99.9, 'control': 'ctrl_monitoring'}, {'id':
                'metric_risk_review', 'name': 'Risk Review Frequency',
                'type': 'Days', 'target': 180, 'control': 'ctrl_risk_assess'}]
            for metric in metrics:
                control_id = metric.pop('control')
                session.run(
                    """
                    MERGE (m:Metric {id: $id})
                    SET m.name = $name,
                        m.type = $type,
                        m.target = $target
                    WITH m
                    MATCH (c:Control {id: $control_id})
                    MERGE (m)-[:MEASURES]->(c)
                    """
                    , **metric, control_id=control_id)
            logger.info('✅ Compliance graph data created')

    def create_indexes(self) ->None:
        """Create indexes for better query performance."""
        logger.info('📑 Creating indexes...')
        indexes = [
            'CREATE INDEX domain_name IF NOT EXISTS FOR (d:Domain) ON (d.name)'
            ,
            'CREATE INDEX jurisdiction_code IF NOT EXISTS FOR (j:Jurisdiction) ON (j.code)'
            ,
            'CREATE INDEX regulation_name IF NOT EXISTS FOR (r:Regulation) ON (r.name)'
            ,
            'CREATE INDEX requirement_article IF NOT EXISTS FOR (req:Requirement) ON (req.article)'
            ,
            'CREATE INDEX control_type IF NOT EXISTS FOR (c:Control) ON (c.type)'
            ,
            'CREATE INDEX metric_type IF NOT EXISTS FOR (m:Metric) ON (m.type)',
            ]
        with self.driver.session() as session:
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    logger.info('   Note: %s' % str(e))
        logger.info('✅ Indexes created')

    def verify_data(self) ->None:
        """Verify the created data."""
        logger.info('\n🔍 Verifying compliance graph...')
        with self.driver.session() as session:
            node_counts = [('Domain', 'Domain'), ('Jurisdiction',
                'Jurisdiction'), ('Regulation', 'Regulation'), (
                'Requirement', 'Requirement'), ('Control', 'Control'), (
                'Metric', 'Metric')]
            for label, name in node_counts:
                result = session.run(
                    f'MATCH (n:{label}) RETURN count(n) as count')
                count = result.single()['count']
                logger.info('   %ss: %s' % (name, count))
            result = session.run('MATCH ()-[r]->() RETURN count(r) as count')
            rel_count = result.single()['count']
            logger.info('   Total relationships: %s' % rel_count)
            logger.info('\n📊 Sample compliance coverage query:')
            result = session.run(
                """
                MATCH (r:Regulation)-[:BELONGS_TO]->(d:Domain)
                RETURN d.name as domain, count(r) as regulations
                ORDER BY regulations DESC
            """,
                )
            for record in result:
                logger.info('   %s: %s regulations' % (record['domain'],
                    record['regulations']))

    def close(self) ->None:
        """Close the database connection."""
        if self.driver:
            self.driver.close()


def main() ->None:
    """Initialize Neo4j compliance graph."""
    logger.info('=' * 60)
    logger.info('🚀 Neo4j Compliance Graph Initialization')
    logger.info('=' * 60)
    logger.info('\n📍 Connecting to Neo4j at %s' % NEO4J_URI)
    logger.info('   Username: %s' % NEO4J_USERNAME)
    initializer = ComplianceGraphInitializer(NEO4J_URI, NEO4J_USERNAME,
        NEO4J_PASSWORD)
    if not initializer.connect():
        logger.info('\n❌ Failed to connect to Neo4j')
        logger.info('\nPlease ensure:')
        logger.info(
            '1. Neo4j is running (docker compose -f docker-compose.neo4j.yml up -d)',
            )
        logger.info('2. Connection details are correct')
        logger.info('3. Neo4j has finished starting up')
        sys.exit(1)
    try:
        initializer.clear_database()
        initializer.create_constraints()
        initializer.create_compliance_data()
        initializer.create_indexes()
        initializer.verify_data()
        logger.info('\n' + '=' * 60)
        logger.info('✅ Neo4j compliance graph initialized successfully!')
        logger.info('\nYou can now:')
        logger.info('1. Access Neo4j Browser at http://localhost:7474')
        logger.info('2. Login with username: neo4j, password: please_change')
        logger.info('3. Run queries like: MATCH (n) RETURN n LIMIT 50')
        logger.info('4. Use the compliance graph in your application')
    except Exception as e:
        logger.info('\n❌ Error initializing compliance graph: %s' % str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        initializer.close()


if __name__ == '__main__':
    main()
