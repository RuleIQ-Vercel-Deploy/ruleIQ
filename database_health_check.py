#!/usr/bin/env python3
"""
Comprehensive database health check script for ruleIQ.
Tests PostgreSQL (Neon), Neo4j (AuraDB), and Redis connections.
"""

import sys
import asyncio
import time
from typing import Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
import psutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Terminal colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DatabaseHealthChecker:
    def __init__(self):
        self.results = {}
        self.issues = []
        
    async def check_postgresql(self) -> Tuple[bool, Dict]:
        """Check PostgreSQL (Neon) connection and health."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}PostgreSQL (Neon) Health Check{Colors.END}")
        results = {"status": "unknown", "details": {}}
        
        try:
            from database.db_setup import get_db, async_get_db
            from database.session import SessionLocal, AsyncSessionLocal
            from sqlalchemy import text
            from config.settings import settings
            
            # Print connection info (without password)
            db_url = settings.DATABASE_URL
            if db_url:
                # Hide password in URL
                safe_url = db_url.split('@')[1] if '@' in db_url else 'configured'
                print(f"  Database: {safe_url}")
            
            # Test sync connection
            print(f"\n  {Colors.CYAN}Testing sync connection...{Colors.END}")
            start = time.time()
            with SessionLocal() as db:
                result = db.execute(text("SELECT version()")).fetchone()
                sync_time = time.time() - start
                print(f"    {Colors.GREEN}✓ Connected in {sync_time:.2f}s{Colors.END}")
                print(f"    Version: {result[0][:50]}...")
                results["details"]["sync_connection"] = "success"
                results["details"]["version"] = result[0][:100]
            
            # Test async connection
            print(f"\n  {Colors.CYAN}Testing async connection...{Colors.END}")
            start = time.time()
            async with AsyncSessionLocal() as db:
                result = await db.execute(text("SELECT current_database(), current_schema()"))
                row = result.fetchone()
                async_time = time.time() - start
                print(f"    {Colors.GREEN}✓ Connected in {async_time:.2f}s{Colors.END}")
                print(f"    Database: {row[0]}, Schema: {row[1]}")
                results["details"]["async_connection"] = "success"
                results["details"]["database"] = row[0]
                results["details"]["schema"] = row[1]
            
            # Test connection pool
            print(f"\n  {Colors.CYAN}Testing connection pool...{Colors.END}")
            from database.db_setup import engine
            pool = engine.pool
            print(f"    Pool size: {pool.size()}")
            print(f"    Checked out connections: {pool.checked_out()}")
            print(f"    Overflow: {pool.overflow()}")
            print(f"    Total: {pool.total()}")
            results["details"]["pool_healthy"] = pool.total() <= pool.size() + pool._max_overflow
            
            # Check tables exist
            print(f"\n  {Colors.CYAN}Checking database schema...{Colors.END}")
            with SessionLocal() as db:
                result = db.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result]
                print(f"    Found {len(tables)} tables")
                
                critical_tables = ['users', 'business_profiles', 'assessment_sessions']
                for table in critical_tables:
                    if table in tables:
                        print(f"    {Colors.GREEN}✓ Table '{table}' exists{Colors.END}")
                    else:
                        print(f"    {Colors.RED}✗ Table '{table}' missing{Colors.END}")
                        self.issues.append(f"PostgreSQL: Missing table '{table}'")
                
                results["details"]["tables"] = len(tables)
                results["details"]["critical_tables"] = all(t in tables for t in critical_tables)
            
            # Performance test
            print(f"\n  {Colors.CYAN}Testing query performance...{Colors.END}")
            with SessionLocal() as db:
                # Simple query
                start = time.time()
                db.execute(text("SELECT COUNT(*) FROM users"))
                simple_time = time.time() - start
                print(f"    Simple query: {simple_time*1000:.2f}ms")
                
                # Complex query
                start = time.time()
                db.execute(text("""
                    SELECT COUNT(*) 
                    FROM assessment_sessions 
                    WHERE created_at > NOW() - INTERVAL '30 days'
                """))
                complex_time = time.time() - start
                print(f"    Complex query: {complex_time*1000:.2f}ms")
                
                results["details"]["performance"] = {
                    "simple_query_ms": round(simple_time * 1000, 2),
                    "complex_query_ms": round(complex_time * 1000, 2)
                }
            
            results["status"] = "healthy"
            print(f"\n  {Colors.GREEN}{Colors.BOLD}✅ PostgreSQL is healthy{Colors.END}")
            return True, results
            
        except Exception as e:
            print(f"  {Colors.RED}✗ PostgreSQL check failed: {e}{Colors.END}")
            results["status"] = "error"
            results["details"]["error"] = str(e)
            self.issues.append(f"PostgreSQL: {str(e)}")
            return False, results
    
    async def check_redis(self) -> Tuple[bool, Dict]:
        """Check Redis connection and health."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}Redis Health Check{Colors.END}")
        results = {"status": "unknown", "details": {}}
        
        try:
            from database.redis_client import redis_client
            from config.settings import settings
            
            # Print connection info
            print(f"  Redis URL: {settings.REDIS_URL or 'Not configured'}")
            
            # Test connection
            print(f"\n  {Colors.CYAN}Testing connection...{Colors.END}")
            start = time.time()
            pong = await redis_client.ping()
            ping_time = time.time() - start
            
            if pong:
                print(f"    {Colors.GREEN}✓ Connected (ping: {ping_time*1000:.2f}ms){Colors.END}")
                results["details"]["ping_ms"] = round(ping_time * 1000, 2)
            else:
                print(f"    {Colors.RED}✗ Ping failed{Colors.END}")
                return False, results
            
            # Get Redis info
            print(f"\n  {Colors.CYAN}Server information...{Colors.END}")
            info = await redis_client.info()
            print(f"    Version: {info.get('redis_version', 'unknown')}")
            print(f"    Uptime: {info.get('uptime_in_days', 0)} days")
            print(f"    Connected clients: {info.get('connected_clients', 0)}")
            print(f"    Used memory: {info.get('used_memory_human', 'unknown')}")
            
            results["details"]["version"] = info.get('redis_version')
            results["details"]["uptime_days"] = info.get('uptime_in_days')
            results["details"]["memory"] = info.get('used_memory_human')
            
            # Test operations
            print(f"\n  {Colors.CYAN}Testing operations...{Colors.END}")
            test_key = f"health_check_{datetime.now().timestamp()}"
            
            # SET operation
            start = time.time()
            await redis_client.set(test_key, "test_value", ex=10)
            set_time = time.time() - start
            print(f"    SET: {set_time*1000:.2f}ms")
            
            # GET operation
            start = time.time()
            value = await redis_client.get(test_key)
            get_time = time.time() - start
            print(f"    GET: {get_time*1000:.2f}ms")
            
            # DELETE operation
            start = time.time()
            await redis_client.delete(test_key)
            del_time = time.time() - start
            print(f"    DELETE: {del_time*1000:.2f}ms")
            
            results["details"]["operations"] = {
                "set_ms": round(set_time * 1000, 2),
                "get_ms": round(get_time * 1000, 2),
                "delete_ms": round(del_time * 1000, 2)
            }
            
            # Check for existing keys
            keys = await redis_client.keys("*")
            print(f"\n    Total keys in database: {len(keys)}")
            
            results["status"] = "healthy"
            print(f"\n  {Colors.GREEN}{Colors.BOLD}✅ Redis is healthy{Colors.END}")
            return True, results
            
        except Exception as e:
            print(f"  {Colors.RED}✗ Redis check failed: {e}{Colors.END}")
            results["status"] = "error"
            results["details"]["error"] = str(e)
            self.issues.append(f"Redis: {str(e)}")
            return False, results
    
    async def check_neo4j(self) -> Tuple[bool, Dict]:
        """Check Neo4j (AuraDB) connection and health."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}Neo4j (AuraDB) Health Check{Colors.END}")
        results = {"status": "unknown", "details": {}}
        
        try:
            from services.neo4j_service import neo4j_service
            from config.settings import settings
            
            # Check if Neo4j is configured
            if not settings.NEO4J_URI:
                print(f"  {Colors.YELLOW}⚠ Neo4j not configured (optional service){Colors.END}")
                results["status"] = "not_configured"
                return True, results
            
            # Print connection info (without password)
            uri = settings.NEO4J_URI
            if uri:
                safe_uri = uri.replace("neo4j+s://", "").split('@')[0] if '@' in uri else uri
                print(f"  Neo4j URI: {safe_uri}")
            
            if not neo4j_service or not neo4j_service.driver:
                print(f"  {Colors.YELLOW}⚠ Neo4j service not initialized{Colors.END}")
                results["status"] = "not_initialized"
                return False, results
            
            # Test connection
            print(f"\n  {Colors.CYAN}Testing connection...{Colors.END}")
            start = time.time()
            with neo4j_service.driver.session() as session:
                result = session.run("RETURN 1 as test, datetime() as time")
                record = result.single()
                conn_time = time.time() - start
                print(f"    {Colors.GREEN}✓ Connected in {conn_time:.2f}s{Colors.END}")
                print(f"    Server time: {record['time']}")
                results["details"]["connection_time"] = round(conn_time, 2)
            
            # Get database info
            print(f"\n  {Colors.CYAN}Database information...{Colors.END}")
            with neo4j_service.driver.session() as session:
                # Get version
                result = session.run("CALL dbms.components()")
                for record in result:
                    if record['name'] == 'Neo4j Kernel':
                        print(f"    Version: {record['version']}")
                        results["details"]["version"] = record['version']
                
                # Count nodes and relationships
                result = session.run("""
                    MATCH (n) 
                    RETURN COUNT(n) as nodes
                """)
                nodes = result.single()['nodes']
                
                result = session.run("""
                    MATCH ()-[r]->() 
                    RETURN COUNT(r) as relationships
                """)
                relationships = result.single()['relationships']
                
                print(f"    Nodes: {nodes}")
                print(f"    Relationships: {relationships}")
                results["details"]["nodes"] = nodes
                results["details"]["relationships"] = relationships
            
            # Check indexes
            print(f"\n  {Colors.CYAN}Checking indexes...{Colors.END}")
            with neo4j_service.driver.session() as session:
                result = session.run("SHOW INDEXES")
                indexes = list(result)
                print(f"    Found {len(indexes)} indexes")
                results["details"]["indexes"] = len(indexes)
            
            # Performance test
            print(f"\n  {Colors.CYAN}Testing query performance...{Colors.END}")
            with neo4j_service.driver.session() as session:
                # Simple query
                start = time.time()
                session.run("MATCH (n) RETURN n LIMIT 1").single()
                simple_time = time.time() - start
                print(f"    Simple query: {simple_time*1000:.2f}ms")
                
                # Complex query
                start = time.time()
                session.run("""
                    MATCH (n)
                    WITH n, rand() as r
                    ORDER BY r
                    LIMIT 10
                    RETURN n
                """).data()
                complex_time = time.time() - start
                print(f"    Complex query: {complex_time*1000:.2f}ms")
                
                results["details"]["performance"] = {
                    "simple_query_ms": round(simple_time * 1000, 2),
                    "complex_query_ms": round(complex_time * 1000, 2)
                }
            
            results["status"] = "healthy"
            print(f"\n  {Colors.GREEN}{Colors.BOLD}✅ Neo4j is healthy{Colors.END}")
            return True, results
            
        except Exception as e:
            print(f"  {Colors.RED}✗ Neo4j check failed: {e}{Colors.END}")
            results["status"] = "error"
            results["details"]["error"] = str(e)
            self.issues.append(f"Neo4j: {str(e)}")
            return False, results
    
    async def check_migrations(self) -> Tuple[bool, Dict]:
        """Check database migration status."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}Database Migration Status{Colors.END}")
        results = {"status": "unknown", "details": {}}
        
        try:
            from database.session import SessionLocal
            from sqlalchemy import text
            
            with SessionLocal() as db:
                # Check if alembic version table exists
                result = db.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'alembic_version'
                    )
                """))
                has_alembic = result.scalar()
                
                if has_alembic:
                    # Get current migration version
                    result = db.execute(text("SELECT version_num FROM alembic_version"))
                    version = result.scalar()
                    print(f"  {Colors.GREEN}✓ Migrations table exists{Colors.END}")
                    print(f"  Current version: {version}")
                    results["details"]["current_version"] = version
                    results["status"] = "migrated"
                else:
                    print(f"  {Colors.YELLOW}⚠ No migrations table found{Colors.END}")
                    results["status"] = "not_migrated"
                
            return True, results
            
        except Exception as e:
            print(f"  {Colors.RED}✗ Migration check failed: {e}{Colors.END}")
            results["status"] = "error"
            results["details"]["error"] = str(e)
            return False, results
    
    def print_summary(self):
        """Print health check summary."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}DATABASE HEALTH CHECK SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
        
        all_healthy = True
        
        for db_name, result in self.results.items():
            status = result.get("status", "unknown")
            
            if status == "healthy":
                icon = f"{Colors.GREEN}✅"
                status_text = "HEALTHY"
            elif status == "not_configured":
                icon = f"{Colors.YELLOW}⚠️"
                status_text = "NOT CONFIGURED"
            elif status == "error":
                icon = f"{Colors.RED}❌"
                status_text = "ERROR"
                all_healthy = False
            else:
                icon = f"{Colors.YELLOW}⚠️"
                status_text = status.upper()
                all_healthy = False
            
            print(f"\n{icon} {db_name:15} {status_text}{Colors.END}")
            
            # Print key metrics
            details = result.get("details", {})
            if "version" in details:
                print(f"    Version: {details['version']}")
            if "performance" in details:
                perf = details["performance"]
                print(f"    Performance: Simple={perf.get('simple_query_ms', 'N/A')}ms, Complex={perf.get('complex_query_ms', 'N/A')}ms")
        
        # Issues
        if self.issues:
            print(f"\n{Colors.RED}{Colors.BOLD}Issues Found:{Colors.END}")
            for issue in self.issues:
                print(f"  • {issue}")
        
        # System resources
        print(f"\n{Colors.BOLD}System Resources:{Colors.END}")
        print(f"  CPU Usage: {psutil.cpu_percent()}%")
        print(f"  Memory Usage: {psutil.virtual_memory().percent}%")
        print(f"  Disk Usage: {psutil.disk_usage('/').percent}%")
        
        # Overall status
        if all_healthy and not self.issues:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All databases are healthy and ready!{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ Some database issues need attention.{Colors.END}")

async def main():
    """Run database health checks."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║            ruleIQ Database Health Check Suite                   ║")
    print("╚══════════════════════════════════════════════════════════════════╗")
    print(f"{Colors.END}")
    
    checker = DatabaseHealthChecker()
    
    # Run health checks
    pg_healthy, pg_results = await checker.check_postgresql()
    checker.results["PostgreSQL"] = pg_results
    
    redis_healthy, redis_results = await checker.check_redis()
    checker.results["Redis"] = redis_results
    
    neo4j_healthy, neo4j_results = await checker.check_neo4j()
    checker.results["Neo4j"] = neo4j_results
    
    migration_healthy, migration_results = await checker.check_migrations()
    checker.results["Migrations"] = migration_results
    
    # Print summary
    checker.print_summary()
    
    # Exit code
    all_healthy = all(
        r.get("status") in ["healthy", "not_configured", "migrated"] 
        for r in checker.results.values()
    )
    sys.exit(0 if all_healthy else 1)

if __name__ == "__main__":
    asyncio.run(main())