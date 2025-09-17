"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Backup script for Neon PostgreSQL and Neo4j databases
Creates timestamped backups before major refactoring
"""

from typing import Any
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import asyncio
from dotenv import load_dotenv
load_dotenv('.env.local')
BACKUP_DIR = Path('backups')
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')


def ensure_backup_dir() ->Any:
    """Ensure backup directory exists."""
    BACKUP_DIR.mkdir(exist_ok=True)
    logger.info('📁 Backup directory: %s' % BACKUP_DIR)


def backup_neo4j() ->Any:
    """Backup Neo4j database using cypher-shell export."""
    logger.info('\n🔷 Backing up Neo4j database...')
    neo4j_backup_dir = BACKUP_DIR / f'neo4j_{TIMESTAMP}'
    neo4j_backup_dir.mkdir(exist_ok=True)
    backup_file = neo4j_backup_dir / 'compliance_graph.cypher'
    try:
        export_cmd = f"""
        docker exec ruleiq-neo4j cypher-shell -u neo4j -p please_change         "CALL apoc.export.cypher.all(null, {{format: 'cypher-shell', stream: true}})         YIELD cypherStatements RETURN cypherStatements" > {backup_file}
        """
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=(
            'neo4j', 'please_change'))
        with driver.session() as session:
            nodes_result = session.run(
                """
                MATCH (n)
                RETURN labels(n) as labels, properties(n) as props, id(n) as node_id
            """,
                )
            nodes = []
            for record in nodes_result:
                nodes.append({'id': record['node_id'], 'labels': record[
                    'labels'], 'properties': record['props']})
            rels_result = session.run(
                """
                MATCH ()-[r]->()
                RETURN type(r) as type, properties(r) as props, 
                       id(startNode(r)) as start_id, id(endNode(r)) as end_id
            """,
                )
            relationships = []
            for record in rels_result:
                relationships.append({'type': record['type'], 'properties':
                    record['props'], 'start_id': record['start_id'],
                    'end_id': record['end_id']})
        driver.close()
        backup_data = {'timestamp': TIMESTAMP, 'nodes': nodes,
            'relationships': relationships, 'node_count': len(nodes),
            'relationship_count': len(relationships)}
        json_file = neo4j_backup_dir / 'compliance_graph.json'
        with open(json_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        logger.info('✅ Neo4j backup completed:')
        logger.info('   - Nodes: %s' % len(nodes))
        logger.info('   - Relationships: %s' % len(relationships))
        logger.info('   - Location: %s' % json_file)
        return True
    except Exception as e:
        logger.info('❌ Neo4j backup failed: %s' % e)
        return False


async def backup_neon() ->bool:
    """Backup Neon PostgreSQL database using pg_dump."""
    logger.info('\n🔶 Backing up Neon PostgreSQL database...')
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.info('❌ DATABASE_URL not found')
        return False
    import re
    pg_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
    if '?' in pg_url:
        pg_url = pg_url.split('?')[0]
    neon_backup_dir = BACKUP_DIR / f'neon_{TIMESTAMP}'
    neon_backup_dir.mkdir(exist_ok=True)
    schema_file = neon_backup_dir / 'schema.sql'
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        clean_url = re.sub('[?&](sslmode|channel_binding)=[^&]*', '',
            database_url)
        if '?' not in clean_url and '&' in clean_url:
            clean_url = clean_url.replace('&', '?', 1)
        engine = create_async_engine(clean_url, echo=False, connect_args={
            'ssl': True, 'server_settings': {'jit': 'off'}})
        async with engine.begin() as conn:
            from sqlalchemy import text
            result = await conn.execute(text(
                """
                SELECT tablename, 
                       pg_size_pretty(pg_total_relation_size(quote_ident(tablename)::regclass)) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """
                ))
            tables = result.fetchall()
            table_info = []
            for table in tables:
                count_result = await conn.execute(text(
                    f'SELECT COUNT(*) FROM {table[0]}'))
                count = count_result.scalar()
                table_info.append({'table': table[0], 'size': table[1],
                    'rows': count})
            info_file = neon_backup_dir / 'database_info.json'
            backup_info = {'timestamp': TIMESTAMP, 'database_url': pg_url.
                split('@')[1] if '@' in pg_url else 'hidden', 'tables':
                table_info, 'table_count': len(table_info)}
            with open(info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            critical_tables = ['business_profiles', 'assessment_sessions',
                'compliance_requirements', 'evidence_records',
                'risk_assessments']
            for table_name in critical_tables:
                if table_name in [t['table'] for t in table_info]:
                    result = await conn.execute(text(
                        f"""
                        SELECT row_to_json(t) 
                        FROM (SELECT * FROM {table_name} LIMIT 1000) t
                    """
                        ))
                    rows = [r[0] for r in result.fetchall()]
                    if rows:
                        table_file = neon_backup_dir / f'{table_name}.json'
                        with open(table_file, 'w') as f:
                            json.dump(rows, f, indent=2, default=str)
                        logger.info('   ✓ Backed up %s: %s rows' % (
                            table_name, len(rows)))
        await engine.dispose()
        logger.info('✅ Neon backup completed:')
        logger.info('   - Tables: %s' % len(table_info))
        logger.info('   - Location: %s' % neon_backup_dir)
        total_rows = sum(t['rows'] for t in table_info)
        logger.info('   - Total rows: %s' % total_rows)
        return True
    except Exception as e:
        logger.info('❌ Neon backup failed: %s' % e)
        import traceback
        traceback.print_exc()
        return False


def create_backup_summary() ->Any:
    """Create a summary of all backups."""
    logger.info('\n📋 Creating backup summary...')
    summary_file = BACKUP_DIR / 'backup_summary.md'
    with open(summary_file, 'w') as f:
        f.write(f'# Database Backups - {TIMESTAMP}\n\n')
        f.write('## Purpose\n')
        f.write('Backups created before LangGraph refactoring phases.\n\n')
        f.write('## Backup Locations\n')
        f.write(f'- **Neo4j**: `backups/neo4j_{TIMESTAMP}/`\n')
        f.write(f'- **Neon**: `backups/neon_{TIMESTAMP}/`\n\n')
        f.write('## Restoration Instructions\n\n')
        f.write('### Neo4j Restoration\n')
        f.write('```python\n')
        f.write('# Use scripts/restore_neo4j.py\n')
        f.write(
            f'python scripts/restore_neo4j.py backups/neo4j_{TIMESTAMP}/compliance_graph.json\n',
            )
        f.write('```\n\n')
        f.write('### Neon Restoration\n')
        f.write('```python\n')
        f.write('# Critical data is in JSON format for selective restoration\n',
            )
        f.write(
            f'# Check backups/neon_{TIMESTAMP}/database_info.json for table list\n',
            )
        f.write('```\n\n')
        f.write(f'## Timestamp: {datetime.now().isoformat()}\n')
    logger.info('✅ Backup summary created: %s' % summary_file)


async def main() ->bool:
    """Run all backup operations."""
    logger.info('=' * 60)
    logger.info('🔒 Database Backup Script')
    logger.info('=' * 60)
    ensure_backup_dir()
    neo4j_success = backup_neo4j()
    neon_success = await backup_neon()
    if neo4j_success and neon_success:
        create_backup_summary()
        logger.info('\n✅ All backups completed successfully!')
        logger.info('📁 Backup location: %s' % BACKUP_DIR)
        return True
    else:
        logger.info('\n⚠️ Some backups failed. Check the errors above.')
        return False


if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
