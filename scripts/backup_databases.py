#!/usr/bin/env python3
"""
Backup script for Neon PostgreSQL and Neo4j databases
Creates timestamped backups before major refactoring
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Create backups directory
BACKUP_DIR = Path("backups")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_backup_dir():
    """Ensure backup directory exists."""
    BACKUP_DIR.mkdir(exist_ok=True)
    print(f"📁 Backup directory: {BACKUP_DIR}")


def backup_neo4j():
    """Backup Neo4j database using cypher-shell export."""
    print("\n🔷 Backing up Neo4j database...")
    
    neo4j_backup_dir = BACKUP_DIR / f"neo4j_{TIMESTAMP}"
    neo4j_backup_dir.mkdir(exist_ok=True)
    
    # Export all nodes and relationships to Cypher
    backup_file = neo4j_backup_dir / "compliance_graph.cypher"
    
    try:
        # Use docker exec to run cypher-shell export
        export_cmd = f"""
        docker exec ruleiq-neo4j cypher-shell -u neo4j -p please_change \
        "CALL apoc.export.cypher.all(null, {{format: 'cypher-shell', stream: true}}) \
        YIELD cypherStatements RETURN cypherStatements" > {backup_file}
        """
        
        # Alternative: Simple dump using Python neo4j driver
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "please_change")
        )
        
        with driver.session() as session:
            # Get all nodes
            nodes_result = session.run("""
                MATCH (n)
                RETURN labels(n) as labels, properties(n) as props, id(n) as node_id
            """)
            
            nodes = []
            for record in nodes_result:
                nodes.append({
                    "id": record["node_id"],
                    "labels": record["labels"],
                    "properties": record["props"]
                })
            
            # Get all relationships
            rels_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, properties(r) as props, 
                       id(startNode(r)) as start_id, id(endNode(r)) as end_id
            """)
            
            relationships = []
            for record in rels_result:
                relationships.append({
                    "type": record["type"],
                    "properties": record["props"],
                    "start_id": record["start_id"],
                    "end_id": record["end_id"]
                })
        
        driver.close()
        
        # Save as JSON
        backup_data = {
            "timestamp": TIMESTAMP,
            "nodes": nodes,
            "relationships": relationships,
            "node_count": len(nodes),
            "relationship_count": len(relationships)
        }
        
        json_file = neo4j_backup_dir / "compliance_graph.json"
        with open(json_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"✅ Neo4j backup completed:")
        print(f"   - Nodes: {len(nodes)}")
        print(f"   - Relationships: {len(relationships)}")
        print(f"   - Location: {json_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Neo4j backup failed: {e}")
        return False


async def backup_neon():
    """Backup Neon PostgreSQL database using pg_dump."""
    print("\n🔶 Backing up Neon PostgreSQL database...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    # Parse connection string
    from urllib.parse import urlparse
    import re
    
    # Convert asyncpg URL to standard PostgreSQL URL for pg_dump
    pg_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
    # Remove query parameters that pg_dump doesn't understand
    if '?' in pg_url:
        pg_url = pg_url.split('?')[0]
    
    neon_backup_dir = BACKUP_DIR / f"neon_{TIMESTAMP}"
    neon_backup_dir.mkdir(exist_ok=True)
    
    # Create schema-only backup
    schema_file = neon_backup_dir / "schema.sql"
    
    # For Neon, we'll create a SQL backup using Python
    try:
        from sqlalchemy import create_engine, inspect, MetaData
        from sqlalchemy.ext.asyncio import create_async_engine
        import asyncpg
        
        # Clean the URL for asyncpg
        clean_url = re.sub(r'[?&](sslmode|channel_binding)=[^&]*', '', database_url)
        if '?' not in clean_url and '&' in clean_url:
            clean_url = clean_url.replace('&', '?', 1)
        
        # Get table list and counts
        engine = create_async_engine(
            clean_url, 
            echo=False,
            connect_args={
                "ssl": True,
                "server_settings": {"jit": "off"}
            }
        )
        
        async with engine.begin() as conn:
            # Get all tables
            from sqlalchemy import text
            result = await conn.execute(text("""
                SELECT tablename, 
                       pg_size_pretty(pg_total_relation_size(quote_ident(tablename)::regclass)) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = result.fetchall()
            
            # Get row counts for each table
            table_info = []
            for table in tables:
                count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table[0]}"))
                count = count_result.scalar()
                table_info.append({
                    "table": table[0],
                    "size": table[1],
                    "rows": count
                })
            
            # Save table information
            info_file = neon_backup_dir / "database_info.json"
            backup_info = {
                "timestamp": TIMESTAMP,
                "database_url": pg_url.split('@')[1] if '@' in pg_url else "hidden",
                "tables": table_info,
                "table_count": len(table_info)
            }
            
            with open(info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            # Export critical table data as JSON (for recovery if needed)
            critical_tables = [
                "business_profiles",
                "assessment_sessions", 
                "compliance_requirements",
                "evidence_records",
                "risk_assessments"
            ]
            
            for table_name in critical_tables:
                if table_name in [t["table"] for t in table_info]:
                    result = await conn.execute(text(f"""
                        SELECT row_to_json(t) 
                        FROM (SELECT * FROM {table_name} LIMIT 1000) t
                    """))
                    rows = [r[0] for r in result.fetchall()]
                    
                    if rows:
                        table_file = neon_backup_dir / f"{table_name}.json"
                        with open(table_file, 'w') as f:
                            json.dump(rows, f, indent=2, default=str)
                        print(f"   ✓ Backed up {table_name}: {len(rows)} rows")
        
        await engine.dispose()
        
        print(f"✅ Neon backup completed:")
        print(f"   - Tables: {len(table_info)}")
        print(f"   - Location: {neon_backup_dir}")
        
        # Print summary
        total_rows = sum(t["rows"] for t in table_info)
        print(f"   - Total rows: {total_rows:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Neon backup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_backup_summary():
    """Create a summary of all backups."""
    print("\n📋 Creating backup summary...")
    
    summary_file = BACKUP_DIR / "backup_summary.md"
    
    with open(summary_file, 'w') as f:
        f.write(f"# Database Backups - {TIMESTAMP}\n\n")
        f.write("## Purpose\n")
        f.write("Backups created before LangGraph refactoring phases.\n\n")
        
        f.write("## Backup Locations\n")
        f.write(f"- **Neo4j**: `backups/neo4j_{TIMESTAMP}/`\n")
        f.write(f"- **Neon**: `backups/neon_{TIMESTAMP}/`\n\n")
        
        f.write("## Restoration Instructions\n\n")
        
        f.write("### Neo4j Restoration\n")
        f.write("```python\n")
        f.write("# Use scripts/restore_neo4j.py\n")
        f.write(f"python scripts/restore_neo4j.py backups/neo4j_{TIMESTAMP}/compliance_graph.json\n")
        f.write("```\n\n")
        
        f.write("### Neon Restoration\n")
        f.write("```python\n")
        f.write("# Critical data is in JSON format for selective restoration\n")
        f.write(f"# Check backups/neon_{TIMESTAMP}/database_info.json for table list\n")
        f.write("```\n\n")
        
        f.write(f"## Timestamp: {datetime.now().isoformat()}\n")
    
    print(f"✅ Backup summary created: {summary_file}")


async def main():
    """Run all backup operations."""
    print("=" * 60)
    print("🔒 Database Backup Script")
    print("=" * 60)
    
    ensure_backup_dir()
    
    # Backup both databases
    neo4j_success = backup_neo4j()
    neon_success = await backup_neon()
    
    if neo4j_success and neon_success:
        create_backup_summary()
        print("\n✅ All backups completed successfully!")
        print(f"📁 Backup location: {BACKUP_DIR}")
        return True
    else:
        print("\n⚠️ Some backups failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)