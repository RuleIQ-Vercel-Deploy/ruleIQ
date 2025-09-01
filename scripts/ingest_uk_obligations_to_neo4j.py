#!/usr/bin/env python3
"""
Ingest UK regulatory obligations into Neo4j knowledge graph.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from neo4j import GraphDatabase
import hashlib

class UKComplianceNeo4jIngestion:
    """Ingest UK compliance data into Neo4j knowledge graph."""
    
    def __init__(self):
        """Initialize Neo4j connection using Doppler secrets."""
        # Get Neo4j credentials from Doppler
        neo4j_uri = os.popen('doppler secrets get NEO4J_URI --plain 2>/dev/null').read().strip()
        neo4j_user = os.popen('doppler secrets get NEO4J_USER --plain 2>/dev/null').read().strip()
        neo4j_password = os.popen('doppler secrets get NEO4J_PASSWORD --plain 2>/dev/null').read().strip()
        
        if not all([neo4j_uri, neo4j_user, neo4j_password]):
            # Fallback to environment variables - using correct port 7688
            neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7688')
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', 'ruleiq123')
        
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        print(f"Connected to Neo4j at: {neo4j_uri}")
    
    def close(self):
        """Close Neo4j connection."""
        self.driver.close()
    
    def clear_existing_data(self):
        """Clear existing UK compliance data."""
        with self.driver.session() as session:
            # Clear existing UK compliance nodes
            session.run("""
                MATCH (n)
                WHERE n:Regulation OR n:Obligation OR n:Control OR n:Penalty OR n:ComplianceFramework
                DELETE n
            """)
            print("Cleared existing compliance data")
    
    def create_indexes(self):
        """Create indexes for better query performance."""
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX regulation_id IF NOT EXISTS FOR (r:Regulation) ON (r.regulation_id)",
                "CREATE INDEX obligation_id IF NOT EXISTS FOR (o:Obligation) ON (o.obligation_id)",
                "CREATE INDEX control_id IF NOT EXISTS FOR (c:Control) ON (c.control_id)",
                "CREATE INDEX penalty_id IF NOT EXISTS FOR (p:Penalty) ON (p.penalty_id)",
                "CREATE INDEX framework_name IF NOT EXISTS FOR (f:ComplianceFramework) ON (f.name)"
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                    print(f"Created index: {index.split('FOR')[1].split('ON')[0].strip()}")
                except Exception as e:
                    print(f"Index might already exist: {e}")
    
    def ingest_manifest(self, manifest_path: Path):
        """Ingest UK compliance manifest into Neo4j."""
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        with self.driver.session() as session:
            # Create UK Compliance Framework node
            framework_query = """
                MERGE (f:ComplianceFramework {name: 'UK Regulatory Compliance'})
                SET f.created_at = $created_at,
                    f.version = $version,
                    f.total_obligations = $total_obligations,
                    f.description = 'Comprehensive UK regulatory compliance framework covering GDPR, FCA, MLR, and other key regulations'
                RETURN f
            """
            
            session.run(framework_query, 
                       created_at=manifest.get('created_at', datetime.now().isoformat()),
                       version=manifest.get('version', '2.0'),
                       total_obligations=manifest.get('total_obligations', 108))
            
            print("Created UK Compliance Framework node")
            
            # Create Regulation nodes and relationships
            for reg_name, reg_data in manifest['regulations'].items():
                # Create Regulation node
                reg_query = """
                    MERGE (r:Regulation {regulation_id: $regulation_id})
                    SET r.name = $name,
                        r.obligation_count = $obligation_count,
                        r.status = 'active',
                        r.jurisdiction = 'UK'
                    RETURN r
                """
                
                session.run(reg_query,
                           regulation_id=f"UK-REG-{reg_name.replace(' ', '_').replace('/', '_')}",
                           name=reg_name,
                           obligation_count=len(reg_data['obligations']))
                
                # Link Regulation to Framework
                link_query = """
                    MATCH (f:ComplianceFramework {name: 'UK Regulatory Compliance'})
                    MATCH (r:Regulation {regulation_id: $regulation_id})
                    MERGE (f)-[:INCLUDES_REGULATION]->(r)
                """
                
                session.run(link_query,
                           regulation_id=f"UK-REG-{reg_name.replace(' ', '_').replace('/', '_')}")
                
                print(f"Created Regulation node: {reg_name}")
                
                # Create Obligation nodes
                for obl in reg_data['obligations']:
                    # Generate unique obligation ID
                    obl_text = f"{obl.get('title', '')}_{obl.get('text', '')}_{obl.get('type', '')}"
                    obl_hash = hashlib.md5(obl_text.encode()).hexdigest()[:8]
                    obl_id = f"UK-OBL-{obl_hash}"
                    
                    # Create Obligation node
                    obl_query = """
                        MERGE (o:Obligation {obligation_id: $obligation_id})
                        SET o.title = $title,
                            o.description = $description,
                            o.text = $text,
                            o.type = $type,
                            o.category = $category,
                            o.compliance_level = $compliance_level,
                            o.regulation = $regulation,
                            o.source_url = $source_url,
                            o.created_at = datetime()
                        RETURN o
                    """
                    
                    session.run(obl_query,
                               obligation_id=obl_id,
                               title=obl.get('title', '')[:200],  # Truncate long titles
                               description=obl.get('description', '')[:500],
                               text=obl.get('text', '')[:1000],  # Truncate long text
                               type=obl.get('type', 'requirement'),
                               category=obl.get('category', 'general'),
                               compliance_level=obl.get('compliance_level', 'mandatory'),
                               regulation=reg_name,
                               source_url=obl.get('source_url', ''))
                    
                    # Link Obligation to Regulation
                    link_obl_query = """
                        MATCH (r:Regulation {regulation_id: $regulation_id})
                        MATCH (o:Obligation {obligation_id: $obligation_id})
                        MERGE (r)-[:HAS_OBLIGATION]->(o)
                    """
                    
                    session.run(link_obl_query,
                               regulation_id=f"UK-REG-{reg_name.replace(' ', '_').replace('/', '_')}",
                               obligation_id=obl_id)
            
            print(f"Created {manifest['total_obligations']} Obligation nodes")
    
    def create_cross_references(self):
        """Create cross-references between related obligations."""
        with self.driver.session() as session:
            # Link obligations that share similar text patterns
            similarity_query = """
                MATCH (o1:Obligation), (o2:Obligation)
                WHERE o1.obligation_id < o2.obligation_id
                AND (
                    (o1.text CONTAINS 'data protection' AND o2.text CONTAINS 'data protection')
                    OR (o1.text CONTAINS 'money laundering' AND o2.text CONTAINS 'money laundering')
                    OR (o1.text CONTAINS 'financial' AND o2.text CONTAINS 'financial')
                    OR (o1.category = o2.category AND o1.category <> 'general')
                )
                MERGE (o1)-[:RELATED_TO]->(o2)
                RETURN COUNT(*) as relationships_created
            """
            
            result = session.run(similarity_query).single()
            if result:
                print(f"Created {result['relationships_created']} cross-references between obligations")
    
    def create_compliance_controls(self):
        """Create standard compliance controls and link to obligations."""
        with self.driver.session() as session:
            # Define standard controls
            controls = [
                {
                    'id': 'CTRL-001',
                    'name': 'Data Protection Impact Assessment',
                    'type': 'assessment',
                    'keywords': ['data protection', 'privacy', 'personal data', 'GDPR']
                },
                {
                    'id': 'CTRL-002',
                    'name': 'Customer Due Diligence',
                    'type': 'verification',
                    'keywords': ['money laundering', 'KYC', 'customer identification', 'MLR']
                },
                {
                    'id': 'CTRL-003',
                    'name': 'Risk Assessment',
                    'type': 'assessment',
                    'keywords': ['risk', 'assessment', 'evaluation', 'analysis']
                },
                {
                    'id': 'CTRL-004',
                    'name': 'Training and Awareness',
                    'type': 'training',
                    'keywords': ['training', 'awareness', 'education', 'competence']
                },
                {
                    'id': 'CTRL-005',
                    'name': 'Monitoring and Reporting',
                    'type': 'monitoring',
                    'keywords': ['monitoring', 'reporting', 'suspicious', 'surveillance']
                }
            ]
            
            for control in controls:
                # Create Control node
                ctrl_query = """
                    MERGE (c:Control {control_id: $control_id})
                    SET c.name = $name,
                        c.type = $type,
                        c.status = 'active',
                        c.created_at = datetime()
                    RETURN c
                """
                
                session.run(ctrl_query,
                           control_id=control['id'],
                           name=control['name'],
                           type=control['type'])
                
                # Link Control to relevant Obligations
                for keyword in control['keywords']:
                    link_ctrl_query = """
                        MATCH (c:Control {control_id: $control_id})
                        MATCH (o:Obligation)
                        WHERE toLower(o.text) CONTAINS toLower($keyword)
                           OR toLower(o.description) CONTAINS toLower($keyword)
                        MERGE (o)-[:REQUIRES_CONTROL]->(c)
                    """
                    
                    session.run(link_ctrl_query,
                               control_id=control['id'],
                               keyword=keyword)
                
                print(f"Created Control: {control['name']}")
    
    def create_penalty_nodes(self):
        """Create penalty nodes for violations."""
        with self.driver.session() as session:
            # Define standard penalties
            penalties = [
                {
                    'id': 'PEN-001',
                    'regulation': 'GDPR/DPA',
                    'violation': 'Data breach notification failure',
                    'max_amount': '€20 million or 4% of global turnover',
                    'severity': 'critical'
                },
                {
                    'id': 'PEN-002',
                    'regulation': 'MLR',
                    'violation': 'AML compliance failure',
                    'max_amount': 'Unlimited fine',
                    'severity': 'critical'
                },
                {
                    'id': 'PEN-003',
                    'regulation': 'Bribery Act',
                    'violation': 'Bribery offense',
                    'max_amount': 'Unlimited fine + imprisonment',
                    'severity': 'critical'
                },
                {
                    'id': 'PEN-004',
                    'regulation': 'FCA',
                    'violation': 'Market abuse',
                    'max_amount': 'Unlimited fine',
                    'severity': 'high'
                }
            ]
            
            for penalty in penalties:
                # Create Penalty node
                pen_query = """
                    MERGE (p:Penalty {penalty_id: $penalty_id})
                    SET p.regulation = $regulation,
                        p.violation = $violation,
                        p.max_amount = $max_amount,
                        p.severity = $severity,
                        p.created_at = datetime()
                    RETURN p
                """
                
                session.run(pen_query,
                           penalty_id=penalty['id'],
                           regulation=penalty['regulation'],
                           violation=penalty['violation'],
                           max_amount=penalty['max_amount'],
                           severity=penalty['severity'])
                
                # Link Penalty to relevant Regulation
                link_pen_query = """
                    MATCH (p:Penalty {penalty_id: $penalty_id})
                    MATCH (r:Regulation)
                    WHERE r.name CONTAINS $regulation_name
                    MERGE (r)-[:HAS_PENALTY]->(p)
                """
                
                session.run(link_pen_query,
                           penalty_id=penalty['id'],
                           regulation_name=penalty['regulation'].split('/')[0])
                
                print(f"Created Penalty: {penalty['violation']}")
    
    def generate_statistics(self):
        """Generate and display graph statistics."""
        with self.driver.session() as session:
            stats_query = """
                MATCH (f:ComplianceFramework)
                MATCH (r:Regulation)
                MATCH (o:Obligation)
                MATCH (c:Control)
                MATCH (p:Penalty)
                RETURN 
                    COUNT(DISTINCT f) as frameworks,
                    COUNT(DISTINCT r) as regulations,
                    COUNT(DISTINCT o) as obligations,
                    COUNT(DISTINCT c) as controls,
                    COUNT(DISTINCT p) as penalties
            """
            
            result = session.run(stats_query).single()
            
            print("\n" + "="*80)
            print("NEO4J INGESTION COMPLETE")
            print("="*80)
            print(f"Frameworks: {result['frameworks']}")
            print(f"Regulations: {result['regulations']}")
            print(f"Obligations: {result['obligations']}")
            print(f"Controls: {result['controls']}")
            print(f"Penalties: {result['penalties']}")
            
            # Count relationships
            rel_query = """
                MATCH ()-[r]->()
                RETURN TYPE(r) as type, COUNT(r) as count
                ORDER BY count DESC
            """
            
            print("\nRelationships:")
            for record in session.run(rel_query):
                print(f"  - {record['type']}: {record['count']}")

def main():
    """Main ingestion process."""
    ingestion = UKComplianceNeo4jIngestion()
    
    try:
        # Clear existing data
        ingestion.clear_existing_data()
        
        # Create indexes
        ingestion.create_indexes()
        
        # Ingest manifest
        manifest_path = Path('/home/omar/Documents/ruleIQ/data/manifests/uk_compliance_manifest_complete.json')
        ingestion.ingest_manifest(manifest_path)
        
        # Create cross-references
        ingestion.create_cross_references()
        
        # Create controls
        ingestion.create_compliance_controls()
        
        # Create penalties
        ingestion.create_penalty_nodes()
        
        # Generate statistics
        ingestion.generate_statistics()
        
    finally:
        ingestion.close()

if __name__ == "__main__":
    main()