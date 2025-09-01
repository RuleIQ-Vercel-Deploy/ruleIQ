#!/usr/bin/env python3
"""
Test IQ Agent integration with enhanced Neo4j compliance data.
"""

import asyncio
import os
from dotenv import load_dotenv
import logging
from services.ai.iq_neo4j_integration import IQNeo4jIntegration
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


async def test_iq_neo4j_integration():
    """Test the IQ Neo4j integration with real compliance data."""
    
    # Initialize integration
    neo4j_uri = "bolt://localhost:7688"
    neo4j_user = "neo4j"
    neo4j_password = "ruleiq123"
    
    integration = IQNeo4jIntegration(neo4j_uri, neo4j_user, neo4j_password)
    
    try:
        # Test 1: Risk Assessment for a Fintech Company
        logger.info("\n" + "="*60)
        logger.info("TEST 1: Risk Assessment for Fintech Company")
        logger.info("="*60)
        
        fintech_profile = {
            "industry": "finance",
            "sub_industry": "fintech",
            "country": "UK",
            "processes_payments": True,
            "stores_customer_data": True,
            "has_eu_customers": True,
            "has_us_customers": True,
            "annual_revenue": 25000000,
            "employee_count": 100,
            "certifications": ["ISO27001"]
        }
        
        risk_assessment = await integration.assess_compliance_risk(fintech_profile)
        
        logger.info(f"\n📊 Risk Assessment Results:")
        logger.info(f"  Total Regulations: {risk_assessment['total_regulations']}")
        logger.info(f"  Average Risk Score: {risk_assessment['average_risk_score']}")
        logger.info(f"  High Risk Count: {risk_assessment['high_risk_count']}")
        logger.info(f"  Risk Level: {risk_assessment['risk_level']}")
        logger.info(f"  Automation Potential: {risk_assessment['automation_potential']}")
        logger.info(f"  Estimated Timeline: {risk_assessment['estimated_implementation_months']} months")
        
        if risk_assessment['critical_regulations']:
            logger.info(f"\n🔴 Critical Regulations:")
            for reg in risk_assessment['critical_regulations'][:5]:
                logger.info(f"    - {reg['title']} (Risk: {reg['risk']})")
                
        if risk_assessment['top_controls']:
            logger.info(f"\n🛡️ Top Recommended Controls:")
            for control in risk_assessment['top_controls'][:5]:
                logger.info(f"    - {control}")
                
        # Test 2: Compliance Roadmap
        logger.info("\n" + "="*60)
        logger.info("TEST 2: Compliance Roadmap Generation")
        logger.info("="*60)
        
        roadmap = await integration.get_compliance_roadmap(fintech_profile)
        
        logger.info(f"\n📋 Compliance Roadmap ({len(roadmap)} items):")
        
        current_phase = None
        for item in roadmap[:10]:  # Show first 10 items
            if item['phase'] != current_phase:
                current_phase = item['phase']
                logger.info(f"\n  {current_phase}:")
            logger.info(f"    • {item['title']}")
            logger.info(f"      Risk: {item['risk_score']}, Timeline: {item['timeline']}")
            logger.info(f"      Reason: {item['reason']}")
            
        # Test 3: Control Overlap Analysis
        logger.info("\n" + "="*60)
        logger.info("TEST 3: Control Overlap Analysis")
        logger.info("="*60)
        
        # Get top regulation IDs for analysis
        top_reg_ids = [reg['id'] for reg in risk_assessment['applicable_regulations'][:10]]
        
        if top_reg_ids:
            overlaps = await integration.find_control_overlaps(top_reg_ids)
            
            logger.info(f"\n🔄 Control Overlap Analysis:")
            logger.info(f"  Total Unique Controls: {overlaps['total_unique_controls']}")
            logger.info(f"  Overlapping Controls: {overlaps['overlapping_control_count']}")
            logger.info(f"  Efficiency Gain: {overlaps['efficiency_gain_percentage']}%")
            
            if overlaps['overlapping_controls']:
                logger.info(f"\n  Top Overlapping Controls:")
                for control in overlaps['overlapping_controls'][:5]:
                    logger.info(f"    • {control['control']} (covers {control['regulation_count']} regulations)")
                    
        # Test 4: Enforcement Pattern Analysis
        logger.info("\n" + "="*60)
        logger.info("TEST 4: Enforcement Pattern Analysis")
        logger.info("="*60)
        
        enforcement = await integration.analyze_enforcement_patterns("finance", 365)
        
        logger.info(f"\n⚖️ Enforcement Analysis for Finance Industry:")
        logger.info(f"  Total Industry Penalties: ${enforcement['total_industry_penalties']:,.0f}")
        
        if enforcement['trending_violations']:
            logger.info(f"\n  Trending Violations:")
            for violation in enforcement['trending_violations']:
                logger.info(f"    • {violation}")
                
        if enforcement['high_risk_areas']:
            logger.info(f"\n  High Risk Areas:")
            for area in enforcement['high_risk_areas'][:3]:
                logger.info(f"    • {area['regulation']}")
                logger.info(f"      Cases: {area['enforcement_count']}, Total Penalties: ${area['total_penalties']:,.0f}")
                
        # Test 5: Automation Opportunities
        logger.info("\n" + "="*60)
        logger.info("TEST 5: Automation Opportunities")
        logger.info("="*60)
        
        if top_reg_ids:
            automation = await integration.get_automation_opportunities(top_reg_ids)
            
            logger.info(f"\n🤖 Automation Analysis:")
            logger.info(f"  Average Automation Potential: {automation['average_automation_potential']}")
            logger.info(f"  High Automation Candidates: {len(automation['high_automation_candidates'])}")
            
            efficiency = automation['estimated_efficiency_gain']
            logger.info(f"\n  Estimated Efficiency Gains:")
            logger.info(f"    • Hours Saved Annually: {efficiency['estimated_hours_saved_annually']}")
            logger.info(f"    • Cost Savings: {efficiency['estimated_cost_savings']}")
            logger.info(f"    • Efficiency Improvement: {efficiency['efficiency_improvement']}")
            
            if automation['implementation_roadmap']:
                logger.info(f"\n  Automation Roadmap:")
                for phase in automation['implementation_roadmap']:
                    logger.info(f"    {phase['phase']} ({phase['timeline']}):")
                    logger.info(f"      Items: {len(phase['items'])}, Impact: {phase['expected_impact']}")
                    
        # Test 6: Healthcare Company Profile
        logger.info("\n" + "="*60)
        logger.info("TEST 6: Healthcare Company Assessment")
        logger.info("="*60)
        
        healthcare_profile = {
            "industry": "healthcare",
            "country": "UK",
            "processes_payments": False,
            "stores_customer_data": True,
            "has_eu_customers": True,
            "annual_revenue": 50000000,
            "employee_count": 250,
            "handles_health_data": True
        }
        
        health_assessment = await integration.assess_compliance_risk(healthcare_profile)
        
        logger.info(f"\n🏥 Healthcare Risk Assessment:")
        logger.info(f"  Total Regulations: {health_assessment['total_regulations']}")
        logger.info(f"  Risk Level: {health_assessment['risk_level']}")
        logger.info(f"  High Risk Count: {health_assessment['high_risk_count']}")
        
        logger.info("\n" + "="*60)
        logger.info("✅ ALL INTEGRATION TESTS COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await integration.close()


if __name__ == "__main__":
    asyncio.run(test_iq_neo4j_integration())