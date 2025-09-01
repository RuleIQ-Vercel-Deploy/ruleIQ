#!/usr/bin/env python3
"""
Integration test for Neo4j compliance ingestion pipeline.
Tests the full flow from manifest files to IQ agent queries.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our components
from services.ai.compliance_ingestion_pipeline import (
    Neo4jComplianceIngestion,
    IngestionMetrics
)
from services.ai.compliance_query_engine import ComplianceQueryEngine
from services.neo4j_service import Neo4jGraphRAGService
from services.iq_agent import IQComplianceAgent
from database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

class IngestionIntegrationTest:
    """Test suite for Neo4j ingestion and IQ agent integration."""
    
    def __init__(self):
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7688")
        self.neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.ingestion = None
        self.query_engine = None
        self.iq_agent = None
        self.metrics: Dict[str, Any] = {}
        
    async def setup(self):
        """Initialize all components."""
        logger.info("Setting up integration test environment...")
        
        # Initialize Neo4j ingestion pipeline
        self.ingestion = Neo4jComplianceIngestion(
            uri=self.neo4j_uri,
            user=self.neo4j_user,
            password=self.neo4j_password
        )
        
        # Initialize query engine
        self.query_engine = ComplianceQueryEngine(
            uri=self.neo4j_uri,
            user=self.neo4j_user,
            password=self.neo4j_password
        )
        
        # Initialize Neo4j service for IQ agent
        neo4j_service = Neo4jGraphRAGService(
            uri=self.neo4j_uri,
            user=self.neo4j_user,
            password=self.neo4j_password
        )
        
        # Get PostgreSQL session
        async for session in get_db():
            self.iq_agent = IQComplianceAgent(
                neo4j_service=neo4j_service,
                postgres_session=session
            )
            break
            
        logger.info("Setup complete!")
        
    async def test_phase1_ingestion(self) -> Dict[str, Any]:
        """Test Phase 1: Enhanced metadata ingestion."""
        logger.info("\n" + "="*60)
        logger.info("PHASE 1: Testing Enhanced Metadata Ingestion")
        logger.info("="*60)
        
        results = {}
        
        try:
            # 1. Ingest main compliance manifest
            logger.info("\n1. Ingesting main compliance manifest...")
            manifest_path = Path("data/manifests/compliance_ml_manifest_enhanced.json")
            
            if not manifest_path.exists():
                # Use the original manifest if enhanced doesn't exist yet
                manifest_path = Path("data/manifests/compliance_ml_manifest.json")
                logger.warning(f"Enhanced manifest not found, using: {manifest_path}")
            
            metrics = await self.ingestion.ingest_compliance_manifest(
                manifest_path=manifest_path,
                validate_only=False
            )
            
            results['main_manifest'] = {
                'success': metrics.success,
                'items_processed': metrics.items_processed,
                'items_failed': metrics.items_failed,
                'duration': metrics.duration_seconds,
                'nodes_created': metrics.nodes_created,
                'relationships_created': metrics.relationships_created
            }
            
            logger.info(f"✓ Main manifest ingested: {metrics.items_processed} items")
            
            # 2. Ingest UK industry regulations
            logger.info("\n2. Ingesting UK industry regulations...")
            uk_path = Path("data/manifests/uk_industry_regulations.json")
            
            if uk_path.exists():
                uk_metrics = await self.ingestion.ingest_compliance_manifest(
                    manifest_path=uk_path,
                    validate_only=False
                )
                results['uk_regulations'] = {
                    'success': uk_metrics.success,
                    'items_processed': uk_metrics.items_processed,
                    'duration': uk_metrics.duration_seconds
                }
                logger.info(f"✓ UK regulations ingested: {uk_metrics.items_processed} items")
            else:
                logger.warning("UK regulations file not found")
                
            # 3. Test business trigger matching
            logger.info("\n3. Testing business trigger matching...")
            test_profile = {
                "industry": "finance",
                "processes_payments": True,
                "has_eu_customers": True,
                "stores_customer_data": True,
                "annual_revenue": 50000000,
                "employee_count": 150,
                "country": "UK"
            }
            
            applicable = await self.query_engine.get_applicable_regulations(test_profile)
            results['business_trigger_test'] = {
                'test_profile': test_profile,
                'applicable_regulations': len(applicable),
                'high_risk_count': sum(1 for r in applicable if r.get('risk_score', 0) >= 8),
                'sample_regulations': [r['title'] for r in applicable[:5]]
            }
            
            logger.info(f"✓ Found {len(applicable)} applicable regulations")
            logger.info(f"  High risk (≥8): {results['business_trigger_test']['high_risk_count']}")
            
            # 4. Test risk scoring
            logger.info("\n4. Testing risk scoring integration...")
            if applicable:
                sample_reg = applicable[0]
                risk_analysis = await self.query_engine.get_regulation_risk_analysis(
                    sample_reg['id']
                )
                results['risk_scoring'] = {
                    'regulation': sample_reg['title'],
                    'base_risk': risk_analysis.get('base_risk_score'),
                    'enforcement_adjusted': risk_analysis.get('adjusted_risk'),
                    'enforcement_frequency': risk_analysis.get('enforcement_frequency'),
                    'max_penalty': risk_analysis.get('max_penalty')
                }
                logger.info(f"✓ Risk scoring functional for: {sample_reg['title']}")
                
            # 5. Test control suggestions
            logger.info("\n5. Testing control suggestions...")
            if applicable:
                controls = await self.query_engine.get_suggested_controls(
                    applicable[0]['id']
                )
                results['control_suggestions'] = {
                    'regulation': applicable[0]['title'],
                    'control_count': len(controls),
                    'sample_controls': controls[:3] if controls else []
                }
                logger.info(f"✓ Found {len(controls)} suggested controls")
                
            # 6. Test automation potential
            logger.info("\n6. Testing automation potential scores...")
            automation_stats = await self.query_engine.get_automation_statistics()
            results['automation_potential'] = automation_stats
            logger.info(f"✓ Average automation potential: {automation_stats.get('average_potential', 0):.2f}")
            
            # Store metrics
            self.metrics['phase1'] = results
            
            return results
            
        except Exception as e:
            logger.error(f"Phase 1 test failed: {str(e)}")
            results['error'] = str(e)
            return results
            
    async def test_phase2_relationships(self) -> Dict[str, Any]:
        """Test Phase 2: Relationship mapping."""
        logger.info("\n" + "="*60)
        logger.info("PHASE 2: Testing Relationship Mapping")
        logger.info("="*60)
        
        results = {}
        
        try:
            # 1. Ingest relationship mappings
            logger.info("\n1. Ingesting regulatory relationships...")
            rel_path = Path("data/manifests/regulatory_relationships.json")
            
            if rel_path.exists():
                with open(rel_path, 'r') as f:
                    relationships = json.load(f)
                    
                created_count = await self.ingestion.ingest_regulatory_relationships(
                    relationships.get('relationships', [])
                )
                
                results['relationships_created'] = created_count
                logger.info(f"✓ Created {created_count} regulatory relationships")
                
            # 2. Test dependency chains
            logger.info("\n2. Testing dependency chain queries...")
            gdpr_deps = await self.query_engine.get_regulation_dependencies("gdpr-2016")
            results['dependency_test'] = {
                'regulation': 'GDPR',
                'dependencies': len(gdpr_deps),
                'sample': gdpr_deps[:3] if gdpr_deps else []
            }
            logger.info(f"✓ Found {len(gdpr_deps)} GDPR dependencies")
            
            # 3. Test equivalence detection
            logger.info("\n3. Testing equivalence detection...")
            equivalents = await self.query_engine.find_equivalent_regulations("gdpr-2016")
            results['equivalence_test'] = {
                'regulation': 'GDPR',
                'equivalents': len(equivalents),
                'regions': list(set(e.get('country', 'Global') for e in equivalents))
            }
            logger.info(f"✓ Found {len(equivalents)} equivalent regulations")
            
            # 4. Test conflict detection
            logger.info("\n4. Testing conflict detection...")
            conflicts = await self.query_engine.find_conflicting_regulations("ccpa-2018")
            results['conflict_test'] = {
                'regulation': 'CCPA',
                'conflicts': len(conflicts),
                'conflict_types': list(set(c.get('conflict_type', 'unknown') for c in conflicts))
            }
            logger.info(f"✓ Found {len(conflicts)} potential conflicts")
            
            self.metrics['phase2'] = results
            return results
            
        except Exception as e:
            logger.error(f"Phase 2 test failed: {str(e)}")
            results['error'] = str(e)
            return results
            
    async def test_iq_integration(self) -> Dict[str, Any]:
        """Test IQ agent integration with enhanced data."""
        logger.info("\n" + "="*60)
        logger.info("IQ AGENT INTEGRATION TEST")
        logger.info("="*60)
        
        results = {}
        
        try:
            # 1. Test IQ's perception with enhanced metadata
            logger.info("\n1. Testing IQ perception with enhanced metadata...")
            
            # Create a test business profile
            test_context = {
                "business_profile": {
                    "industry": "finance",
                    "sub_industry": "fintech",
                    "processes_payments": True,
                    "stores_customer_data": True,
                    "has_eu_customers": True,
                    "has_us_customers": True,
                    "annual_revenue": 25000000,
                    "employee_count": 100,
                    "country": "UK",
                    "certifications": ["ISO27001"],
                    "data_types": ["personal", "financial", "health"]
                },
                "request": "What are my top compliance risks?"
            }
            
            # Test IQ's assessment
            perception = await self.iq_agent._perceive_node(test_context)
            results['perception'] = {
                'identified_regulations': len(perception.get('applicable_regulations', [])),
                'risk_level': perception.get('risk_level'),
                'top_risks': perception.get('top_risks', [])[:3]
            }
            logger.info(f"✓ IQ identified {results['perception']['identified_regulations']} regulations")
            
            # 2. Test IQ's planning with relationships
            logger.info("\n2. Testing IQ planning with relationship awareness...")
            
            plan = await self.iq_agent._plan_node(perception)
            results['planning'] = {
                'action_count': len(plan.get('actions', [])),
                'priority_actions': [a.get('title') for a in plan.get('actions', [])[:3]],
                'considers_dependencies': any('depend' in str(a).lower() for a in plan.get('actions', [])),
                'automation_enabled': any(a.get('automation_potential', 0) > 0.5 for a in plan.get('actions', []))
            }
            logger.info(f"✓ IQ generated {results['planning']['action_count']} compliance actions")
            
            # 3. Test GraphRAG query performance
            logger.info("\n3. Testing GraphRAG query performance...")
            
            import time
            start_time = time.time()
            
            # Complex GraphRAG query through IQ
            complex_query = {
                "business_profile": test_context["business_profile"],
                "request": "Show me all GDPR-related requirements and their equivalent regulations in other jurisdictions"
            }
            
            rag_response = await self.iq_agent.process_request(complex_query)
            query_time = time.time() - start_time
            
            results['graphrag_performance'] = {
                'query_time_seconds': round(query_time, 3),
                'response_size': len(str(rag_response)),
                'includes_relationships': 'equivalent' in str(rag_response).lower(),
                'includes_evidence': 'evidence' in str(rag_response).lower() or 'source' in str(rag_response).lower()
            }
            logger.info(f"✓ GraphRAG query completed in {query_time:.3f} seconds")
            
            # 4. Test enforcement-adjusted risk scoring
            logger.info("\n4. Testing enforcement-adjusted risk scoring...")
            
            enforcement_context = {
                "business_profile": test_context["business_profile"],
                "request": "What are the enforcement trends for my industry?"
            }
            
            enforcement_analysis = await self.iq_agent.analyze_enforcement_patterns(enforcement_context)
            results['enforcement_analysis'] = {
                'patterns_identified': len(enforcement_analysis.get('patterns', [])),
                'total_penalties_analyzed': enforcement_analysis.get('total_penalties'),
                'risk_adjustments': enforcement_analysis.get('risk_adjustments', {}),
                'recommended_priority_changes': len(enforcement_analysis.get('priority_changes', []))
            }
            logger.info(f"✓ Analyzed {results['enforcement_analysis']['patterns_identified']} enforcement patterns")
            
            self.metrics['iq_integration'] = results
            return results
            
        except Exception as e:
            logger.error(f"IQ integration test failed: {str(e)}")
            results['error'] = str(e)
            return results
            
    async def generate_report(self):
        """Generate comprehensive test report."""
        logger.info("\n" + "="*60)
        logger.info("INTEGRATION TEST REPORT")
        logger.info("="*60)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_environment": {
                "neo4j_uri": self.neo4j_uri,
                "python_version": "3.11+",
                "test_type": "end-to-end integration"
            },
            "results": self.metrics,
            "summary": {
                "phase1_success": self.metrics.get('phase1', {}).get('main_manifest', {}).get('success', False),
                "phase2_success": 'error' not in self.metrics.get('phase2', {}),
                "iq_integration_success": 'error' not in self.metrics.get('iq_integration', {}),
                "total_regulations_ingested": sum([
                    self.metrics.get('phase1', {}).get('main_manifest', {}).get('items_processed', 0),
                    self.metrics.get('phase1', {}).get('uk_regulations', {}).get('items_processed', 0)
                ]),
                "total_relationships": self.metrics.get('phase2', {}).get('relationships_created', 0),
                "graphrag_performance_ms": self.metrics.get('iq_integration', {}).get('graphrag_performance', {}).get('query_time_seconds', 0) * 1000
            }
        }
        
        # Save report
        report_path = Path("reports/integration_test_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"\n✓ Report saved to: {report_path}")
        
        # Print summary
        logger.info("\n" + "-"*60)
        logger.info("TEST SUMMARY")
        logger.info("-"*60)
        
        summary = report['summary']
        logger.info(f"Phase 1 (Enhanced Metadata): {'✓ PASSED' if summary['phase1_success'] else '✗ FAILED'}")
        logger.info(f"Phase 2 (Relationships): {'✓ PASSED' if summary['phase2_success'] else '✗ FAILED'}")
        logger.info(f"IQ Integration: {'✓ PASSED' if summary['iq_integration_success'] else '✗ FAILED'}")
        logger.info(f"\nTotal Regulations: {summary['total_regulations_ingested']}")
        logger.info(f"Total Relationships: {summary['total_relationships']}")
        logger.info(f"GraphRAG Query Time: {summary['graphrag_performance_ms']:.1f}ms")
        
        return report
        
    async def cleanup(self):
        """Clean up resources."""
        logger.info("\nCleaning up...")
        if self.ingestion:
            await self.ingestion.close()
        if self.query_engine:
            await self.query_engine.close()
        logger.info("✓ Cleanup complete")
        
    async def run_all_tests(self):
        """Run complete integration test suite."""
        try:
            await self.setup()
            await self.test_phase1_ingestion()
            await self.test_phase2_relationships()
            await self.test_iq_integration()
            report = await self.generate_report()
            
            # Determine overall success
            all_passed = all([
                report['summary']['phase1_success'],
                report['summary']['phase2_success'],
                report['summary']['iq_integration_success']
            ])
            
            if all_passed:
                logger.info("\n" + "="*60)
                logger.info("✅ ALL INTEGRATION TESTS PASSED!")
                logger.info("="*60)
            else:
                logger.info("\n" + "="*60)
                logger.info("⚠️ SOME TESTS FAILED - Review report for details")
                logger.info("="*60)
                
            return all_passed
            
        except Exception as e:
            logger.error(f"Critical test failure: {str(e)}")
            return False
        finally:
            await self.cleanup()

async def main():
    """Main entry point."""
    test_suite = IngestionIntegrationTest()
    success = await test_suite.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)