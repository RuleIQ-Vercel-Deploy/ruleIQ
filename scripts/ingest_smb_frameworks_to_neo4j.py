#!/usr/bin/env python3
"""
Ingest SMB framework obligations into Neo4j knowledge graph.
Replaces programmatically-created ISO data with real extracted obligations.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from neo4j import GraphDatabase
import hashlib

class SMBFrameworkNeo4jIngestion:
    """Ingest SMB framework data into Neo4j knowledge graph."""
    
    def __init__(self):
        """Initialize Neo4j connection."""
        # Neo4j connection details
        neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7688')
        neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'ruleiq123')
        
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        print(f"Connected to Neo4j at: {neo4j_uri}")
    
    def close(self):
        """Close Neo4j connection."""
        self.driver.close()
    
    def clear_existing_iso_data(self):
        """Clear existing ISO/Framework data to replace with real extracted data."""
        with self.driver.session() as session:
            # Clear old ISO nodes
            session.run("""
                MATCH (n)
                WHERE n:ISOFramework OR n:ISOClause OR n:ISOControl OR n:ISOObligation 
                   OR n:ISOCommonTheme OR n:FrameworkObligation OR n:SMBFramework
                DETACH DELETE n
            """)
            print("Cleared existing framework data")
    
    def create_indexes(self):
        """Create indexes for better query performance."""
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX framework_id IF NOT EXISTS FOR (f:SMBFramework) ON (f.framework_id)",
                "CREATE INDEX framework_obligation_id IF NOT EXISTS FOR (o:FrameworkObligation) ON (o.obligation_id)",
                "CREATE INDEX framework_category IF NOT EXISTS FOR (o:FrameworkObligation) ON (o.category)",
                "CREATE INDEX framework_priority IF NOT EXISTS FOR (o:FrameworkObligation) ON (o.priority)"
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                    print(f"Created index: {index.split('FOR')[1].split('ON')[0].strip()}")
                except Exception as e:
                    print(f"Index might already exist: {e}")
    
    def ingest_smb_frameworks(self, manifest_path: Path):
        """Ingest SMB framework manifest into Neo4j."""
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        with self.driver.session() as session:
            # Create SMB Framework Suite meta-node
            suite_query = """
                MERGE (s:ComplianceFramework {name: 'SMB Framework Suite'})
                SET s.description = 'Comprehensive framework obligations for Small and Medium Businesses',
                    s.created_at = $created_at,
                    s.total_frameworks = $total_frameworks,
                    s.total_obligations = $total_obligations,
                    s.type = 'SMB-Focused'
                RETURN s
            """
            
            session.run(suite_query,
                       created_at=manifest.get('created_at', datetime.now().isoformat()),
                       total_frameworks=len(manifest['frameworks']),
                       total_obligations=manifest['total_obligations'])
            
            print(f"Created SMB Framework Suite node")
            
            # Create Framework nodes
            for framework_name, framework_info in manifest['frameworks'].items():
                framework_query = """
                    MERGE (f:SMBFramework {framework_id: $framework_id})
                    SET f.name = $name,
                        f.title = $title,
                        f.source = $source,
                        f.obligation_count = $obligation_count,
                        f.categories = $categories,
                        f.core_principles = $core_principles
                    RETURN f
                """
                
                session.run(framework_query,
                           framework_id=f"SMB-{framework_name.replace(' ', '_').replace(':', '_')}",
                           name=framework_name,
                           title=framework_info['title'],
                           source=framework_info['source'],
                           obligation_count=framework_info['obligation_count'],
                           categories=framework_info['categories'],
                           core_principles=framework_info.get('core_principles', []))
                
                # Link to Suite
                link_query = """
                    MATCH (s:ComplianceFramework {name: 'SMB Framework Suite'})
                    MATCH (f:SMBFramework {framework_id: $framework_id})
                    MERGE (s)-[:INCLUDES_FRAMEWORK]->(f)
                """
                
                session.run(link_query,
                           framework_id=f"SMB-{framework_name.replace(' ', '_').replace(':', '_')}")
                
                print(f"Created framework: {framework_name}")
            
            # Create Obligation nodes
            for obligation in manifest['obligations']:
                obl_query = """
                    MERGE (o:FrameworkObligation {obligation_id: $obligation_id})
                    SET o.framework = $framework,
                        o.framework_title = $framework_title,
                        o.source_url = $source_url,
                        o.internal_id = $internal_id,
                        o.title = $title,
                        o.description = $description,
                        o.requirement = $requirement,
                        o.smb_guidance = $smb_guidance,
                        o.category = $category,
                        o.priority = $priority,
                        o.implementation_level = $implementation_level,
                        o.created_at = $created_at
                    RETURN o
                """
                
                session.run(obl_query,
                           obligation_id=obligation['obligation_id'],
                           framework=obligation['framework'],
                           framework_title=obligation['framework_title'],
                           source_url=obligation['source_url'],
                           internal_id=obligation['id'],
                           title=obligation['title'],
                           description=obligation['description'],
                           requirement=obligation['requirement'],
                           smb_guidance=obligation['smb_guidance'],
                           category=obligation['category'],
                           priority=obligation['priority'],
                           implementation_level=obligation.get('implementation_level', 'SMB'),
                           created_at=obligation.get('created_at', datetime.now().isoformat()))
                
                # Link to Framework
                framework_id = f"SMB-{obligation['framework'].replace(' ', '_').replace(':', '_')}"
                link_obl_query = """
                    MATCH (f:SMBFramework {framework_id: $framework_id})
                    MATCH (o:FrameworkObligation {obligation_id: $obligation_id})
                    MERGE (f)-[:DEFINES_OBLIGATION]->(o)
                """
                
                session.run(link_obl_query,
                           framework_id=framework_id,
                           obligation_id=obligation['obligation_id'])
            
            print(f"Created {manifest['total_obligations']} obligation nodes")
    
    def create_cross_framework_relationships(self):
        """Create relationships between related framework obligations."""
        with self.driver.session() as session:
            # Link related security obligations
            security_query = """
                MATCH (o1:FrameworkObligation), (o2:FrameworkObligation)
                WHERE o1.obligation_id < o2.obligation_id
                AND (
                    (o1.category CONTAINS 'Security' AND o2.category CONTAINS 'Security')
                    OR (o1.category CONTAINS 'Risk' AND o2.category CONTAINS 'Risk')
                    OR (o1.category CONTAINS 'Compliance' AND o2.category CONTAINS 'Compliance')
                    OR (o1.category CONTAINS 'Audit' AND o2.category CONTAINS 'Audit')
                )
                MERGE (o1)-[:RELATED_FRAMEWORK_REQUIREMENT]->(o2)
                RETURN COUNT(*) as relationships_created
            """
            
            result = session.run(security_query).single()
            if result:
                print(f"Created {result['relationships_created']} cross-framework relationships")
    
    def link_to_uk_regulations(self):
        """Link framework obligations to relevant UK regulations."""
        with self.driver.session() as session:
            # Link ISO 27001 to GDPR/DPA
            gdpr_link = """
                MATCH (f:FrameworkObligation)
                WHERE f.framework = 'ISO 27001:2022'
                MATCH (r:Regulation)
                WHERE r.name CONTAINS 'GDPR' OR r.name CONTAINS 'DPA'
                MERGE (f)-[:SUPPORTS_COMPLIANCE_WITH]->(r)
            """
            session.run(gdpr_link)
            
            # Link ISO 37301 to various compliance regulations
            compliance_link = """
                MATCH (f:FrameworkObligation)
                WHERE f.framework = 'ISO 37301:2021'
                MATCH (r:Regulation)
                WHERE r.name IN ['MLR', 'Bribery Act', 'FCA']
                MERGE (f)-[:SUPPORTS_COMPLIANCE_WITH]->(r)
            """
            session.run(compliance_link)
            
            # Link NIST CSF to NIS Regulations
            nis_link = """
                MATCH (f:FrameworkObligation)
                WHERE f.framework = 'NIST CSF 2.0'
                MATCH (r:Regulation)
                WHERE r.name CONTAINS 'NIS'
                MERGE (f)-[:SUPPORTS_COMPLIANCE_WITH]->(r)
            """
            session.run(nis_link)
            
            print("Created links to UK regulations")
    
    def create_priority_categories(self):
        """Create priority-based categories for SMB implementation."""
        with self.driver.session() as session:
            # Create Priority nodes
            priorities = [
                {"level": "critical", "description": "Must implement immediately", "order": 1},
                {"level": "high", "description": "Implement within 3 months", "order": 2},
                {"level": "medium", "description": "Implement within 6 months", "order": 3},
                {"level": "low", "description": "Implement within 12 months", "order": 4}
            ]
            
            for priority in priorities:
                priority_query = """
                    MERGE (p:ImplementationPriority {level: $level})
                    SET p.description = $description,
                        p.order = $order
                    RETURN p
                """
                
                session.run(priority_query,
                           level=priority['level'],
                           description=priority['description'],
                           order=priority['order'])
                
                # Link obligations to priorities
                link_priority = """
                    MATCH (o:FrameworkObligation {priority: $level})
                    MATCH (p:ImplementationPriority {level: $level})
                    MERGE (o)-[:HAS_PRIORITY]->(p)
                """
                
                session.run(link_priority, level=priority['level'])
            
            print("Created priority categories")
    
    def create_category_themes(self):
        """Create thematic categories across frameworks."""
        with self.driver.session() as session:
            # Get unique categories
            category_query = """
                MATCH (o:FrameworkObligation)
                RETURN DISTINCT o.category as category
            """
            
            categories = [record['category'] for record in session.run(category_query)]
            
            for category in categories:
                theme_query = """
                    MERGE (t:ComplianceTheme {name: $category})
                    SET t.type = 'SMB Framework Theme'
                    RETURN t
                """
                
                session.run(theme_query, category=category)
                
                # Link obligations to themes
                link_theme = """
                    MATCH (o:FrameworkObligation {category: $category})
                    MATCH (t:ComplianceTheme {name: $category})
                    MERGE (o)-[:BELONGS_TO_THEME]->(t)
                """
                
                session.run(link_theme, category=category)
            
            print(f"Created {len(categories)} compliance themes")
    
    def generate_statistics(self):
        """Generate and display graph statistics."""
        with self.driver.session() as session:
            # Count nodes
            stats_query = """
                MATCH (f:SMBFramework)
                MATCH (o:FrameworkObligation)
                MATCH (t:ComplianceTheme)
                MATCH (p:ImplementationPriority)
                RETURN 
                    COUNT(DISTINCT f) as frameworks,
                    COUNT(DISTINCT o) as obligations,
                    COUNT(DISTINCT t) as themes,
                    COUNT(DISTINCT p) as priorities
            """
            
            result = session.run(stats_query).single()
            
            print("\n" + "="*80)
            print("SMB FRAMEWORK NEO4J INGESTION COMPLETE")
            print("="*80)
            print(f"Frameworks: {result['frameworks']}")
            print(f"Obligations: {result['obligations']}")
            print(f"Themes: {result['themes']}")
            print(f"Priorities: {result['priorities']}")
            
            # Count relationships
            rel_query = """
                MATCH ()-[r]->()
                WHERE TYPE(r) IN ['INCLUDES_FRAMEWORK', 'DEFINES_OBLIGATION', 
                                  'RELATED_FRAMEWORK_REQUIREMENT', 'SUPPORTS_COMPLIANCE_WITH',
                                  'HAS_PRIORITY', 'BELONGS_TO_THEME']
                RETURN TYPE(r) as type, COUNT(r) as count
                ORDER BY count DESC
            """
            
            print("\nRelationships:")
            for record in session.run(rel_query):
                print(f"  - {record['type']}: {record['count']}")
            
            # Priority breakdown
            priority_query = """
                MATCH (o:FrameworkObligation)
                RETURN o.priority as priority, COUNT(o) as count
                ORDER BY 
                    CASE o.priority
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                    END
            """
            
            print("\nPriority Breakdown:")
            for record in session.run(priority_query):
                print(f"  - {record['priority']}: {record['count']} obligations")
            
            # Framework breakdown
            framework_query = """
                MATCH (f:SMBFramework)-[:DEFINES_OBLIGATION]->(o:FrameworkObligation)
                RETURN f.name as framework, COUNT(o) as count
                ORDER BY count DESC
            """
            
            print("\nFramework Breakdown:")
            for record in session.run(framework_query):
                print(f"  - {record['framework']}: {record['count']} obligations")

def main():
    """Main ingestion process."""
    ingestion = SMBFrameworkNeo4jIngestion()
    
    try:
        # Clear old ISO data
        ingestion.clear_existing_iso_data()
        
        # Create indexes
        ingestion.create_indexes()
        
        # Ingest SMB frameworks
        manifest_path = Path('/home/omar/Documents/ruleIQ/data/manifests/smb_frameworks_manifest.json')
        ingestion.ingest_smb_frameworks(manifest_path)
        
        # Create relationships
        ingestion.create_cross_framework_relationships()
        
        # Link to UK regulations
        ingestion.link_to_uk_regulations()
        
        # Create priority categories
        ingestion.create_priority_categories()
        
        # Create themes
        ingestion.create_category_themes()
        
        # Generate statistics
        ingestion.generate_statistics()
        
    finally:
        ingestion.close()

if __name__ == "__main__":
    main()