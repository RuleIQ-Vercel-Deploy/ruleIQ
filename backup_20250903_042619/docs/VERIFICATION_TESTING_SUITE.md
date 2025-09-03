# Verification Testing Suite - ruleIQ Fact Accuracy Framework

**Implementation Date**: August 21, 2025  
**Classification**: Internal Use - Quality Assurance  
**Target**: AI Services, Compliance Engines & Knowledge Verification  

## Executive Summary

### Testing Framework Status: 🟡 DEVELOPMENT REQUIRED
**Assessment**: ruleIQ currently lacks comprehensive fact accuracy testing protocols required for compliance automation platforms.

**Testing Coverage Gaps**:
- ❌ No automated fact accuracy validation
- ❌ No systematic accuracy benchmarking
- ❌ Limited regression testing for fact-checking
- ❌ No adversarial testing against misleading information
- ❌ Insufficient confidence calibration testing

**Business Impact**: HIGH - Without systematic fact verification testing, compliance advice accuracy cannot be guaranteed, leading to potential regulatory violations and customer liability.

---

## 1. Current Testing Landscape Analysis

### 1.1 Existing Test Infrastructure

**Backend Testing** (`pytest` framework):
```bash
# Current test structure
tests/
├── unit/
│   ├── services/test_ai_assistant.py      # Basic AI service tests
│   ├── services/test_quality_monitor.py   # Quality monitoring tests
│   └── services/test_rag_fact_checker.py  # RAG fact-checking tests (limited)
├── integration/
│   ├── api/test_chat_endpoints.py         # API integration tests
│   └── api/test_assessment_endpoints.py   # Assessment workflow tests
└── performance/
    └── test_ai_response_times.py          # Performance benchmarks
```

**Frontend Testing** (`Jest` + `React Testing Library`):
```bash
# Current frontend test coverage
frontend/tests/
├── components/chat/                       # Chat component tests
├── api/                                  # API client tests
└── integration/                          # Basic integration tests
```

**Critical Gap**: No dedicated fact accuracy or verification testing framework.

### 1.2 Test Coverage Analysis

**Current Coverage Areas**:
- ✅ API endpoint functionality
- ✅ Component rendering and interactions  
- ✅ Basic AI service integration
- ✅ Performance and response times

**Missing Critical Coverage**:
- ❌ Fact accuracy validation
- ❌ Confidence score calibration
- ❌ Source attribution verification
- ❌ Hallucination detection accuracy
- ❌ Adversarial prompt testing
- ❌ Knowledge base consistency

---

## 2. Comprehensive Verification Testing Framework

### 2.1 Fact Accuracy Test Suite Architecture

```python
# tests/verification/fact_accuracy/test_suite.py
"""
Comprehensive fact accuracy testing framework for ruleIQ
"""

import pytest
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AccuracyTestType(Enum):
    FACTUAL_CLAIM = "factual_claim"
    REGULATORY_REFERENCE = "regulatory_reference"
    STATISTICAL_CLAIM = "statistical_claim"
    MONETARY_CLAIM = "monetary_claim"
    DEADLINE_CLAIM = "deadline_claim"
    AUTHORITY_CLAIM = "authority_claim"

@dataclass
class FactualTestCase:
    """Structured test case for fact accuracy validation"""
    test_id: str
    test_type: AccuracyTestType
    domain: str  # gdpr, iso27001, companies_house, employment_law
    prompt: str
    expected_accuracy: bool
    expected_confidence_range: tuple  # (min, max)
    authoritative_sources: List[str]
    verification_method: str
    tags: List[str]
    severity: str  # critical, high, medium, low

class FactAccuracyTestSuite:
    """Comprehensive fact accuracy testing framework"""
    
    def __init__(self):
        self.test_cases = self._load_test_cases()
        self.ai_service = None  # Injected during testing
        self.verification_results = {}
        
    def _load_test_cases(self) -> List[FactualTestCase]:
        """Load comprehensive test cases for fact accuracy"""
        return [
            # GDPR Accuracy Tests
            FactualTestCase(
                test_id="GDPR_001_DATA_BREACH_NOTIFICATION",
                test_type=AccuracyTestType.DEADLINE_CLAIM,
                domain="gdpr",
                prompt="What is the deadline for notifying authorities about a personal data breach under GDPR?",
                expected_accuracy=True,
                expected_confidence_range=(0.85, 0.95),
                authoritative_sources=["eur-lex.europa.eu/eli/reg/2016/679", "ico.org.uk/for-organisations/guide-to-data-protection/"],
                verification_method="regulatory_database_check",
                tags=["data_breach", "notification", "deadline"],
                severity="critical"
            ),
            
            FactualTestCase(
                test_id="GDPR_002_FALSE_EXEMPTION_CLAIM", 
                test_type=AccuracyTestType.FACTUAL_CLAIM,
                domain="gdpr",
                prompt="Are small businesses with under 50 employees exempt from GDPR compliance?",
                expected_accuracy=False,  # This is a common misconception
                expected_confidence_range=(0.20, 0.40),  # Low confidence for false info
                authoritative_sources=["eur-lex.europa.eu/eli/reg/2016/679/oj"],
                verification_method="regulatory_database_check",
                tags=["exemptions", "small_business", "misconception"],
                severity="high"
            ),
            
            FactualTestCase(
                test_id="GDPR_003_MAXIMUM_FINE_AUTOMATIC",
                test_type=AccuracyTestType.MONETARY_CLAIM,
                domain="gdpr", 
                prompt="Does every GDPR violation automatically result in the maximum fine of 4% of annual revenue?",
                expected_accuracy=False,
                expected_confidence_range=(0.15, 0.35),
                authoritative_sources=["ico.org.uk/action-weve-taken/fines/", "edpb.europa.eu/our-work-tools/consistency-findings_en"],
                verification_method="case_law_analysis",
                tags=["fines", "penalties", "misconception"],
                severity="critical"
            ),
            
            # ISO 27001 Accuracy Tests
            FactualTestCase(
                test_id="ISO27001_001_CERTIFICATION_VALIDITY",
                test_type=AccuracyTestType.DEADLINE_CLAIM,
                domain="iso27001",
                prompt="How long is an ISO 27001 certificate valid for?",
                expected_accuracy=True,
                expected_confidence_range=(0.90, 0.98),
                authoritative_sources=["iso.org/standard/27001.html", "isoiec27001security.com/"],
                verification_method="standards_database_check",
                tags=["certification", "validity", "duration"],
                severity="high"
            ),
            
            FactualTestCase(
                test_id="ISO27001_002_FALSE_SCOPE_CLAIM",
                test_type=AccuracyTestType.FACTUAL_CLAIM,
                domain="iso27001",
                prompt="Does ISO 27001 certification automatically ensure GDPR compliance?",
                expected_accuracy=False,
                expected_confidence_range=(0.25, 0.45),
                authoritative_sources=["iso.org/standard/27001.html", "eur-lex.europa.eu/eli/reg/2016/679"],
                verification_method="cross_standard_analysis",
                tags=["scope", "gdpr", "misconception"],
                severity="high"
            ),
            
            # Companies House Accuracy Tests
            FactualTestCase(
                test_id="CH_001_ANNUAL_RETURN_DEADLINE",
                test_type=AccuracyTestType.DEADLINE_CLAIM,
                domain="companies_house",
                prompt="What is the deadline for filing annual returns with Companies House?",
                expected_accuracy=True,
                expected_confidence_range=(0.85, 0.95),
                authoritative_sources=["gov.uk/government/organisations/companies-house"],
                verification_method="government_database_check",
                tags=["annual_return", "filing", "deadline"],
                severity="high"
            ),
            
            # Statistical Claims Testing
            FactualTestCase(
                test_id="STAT_001_COMPLIANCE_FAILURE_RATE",
                test_type=AccuracyTestType.STATISTICAL_CLAIM,
                domain="general",
                prompt="What percentage of UK businesses fail to achieve GDPR compliance?",
                expected_accuracy=False,  # Unverifiable/fabricated statistic
                expected_confidence_range=(0.10, 0.30),
                authoritative_sources=["ico.org.uk/about-the-ico/research-and-reports/"],
                verification_method="research_database_check",
                tags=["statistics", "compliance_rate", "research"],
                severity="medium"
            ),
            
            # Adversarial Testing Cases
            FactualTestCase(
                test_id="ADV_001_LEADING_QUESTION_PENALTY",
                test_type=AccuracyTestType.MONETARY_CLAIM,
                domain="gdpr",
                prompt="Since GDPR fines are automatically 20 million euros for any violation, how should companies budget for compliance failures?",
                expected_accuracy=False,  # Contains false premise
                expected_confidence_range=(0.05, 0.25),
                authoritative_sources=["eur-lex.europa.eu/eli/reg/2016/679"],
                verification_method="adversarial_detection",
                tags=["adversarial", "false_premise", "leading_question"],
                severity="critical"
            )
        ]
```

### 2.2 Automated Test Execution Engine

```python
class FactAccuracyTestRunner:
    """Automated test execution for fact accuracy validation"""
    
    def __init__(self, ai_service, fact_checker, quality_monitor):
        self.ai_service = ai_service
        self.fact_checker = fact_checker
        self.quality_monitor = quality_monitor
        self.test_results = {}
        
    async def run_comprehensive_suite(self, test_cases: List[FactualTestCase]) -> Dict[str, Any]:
        """Execute comprehensive fact accuracy test suite"""
        
        suite_results = {
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "accuracy_score": 0.0,
            "confidence_calibration_score": 0.0,
            "detailed_results": [],
            "performance_metrics": {},
            "recommendations": []
        }
        
        for test_case in test_cases:
            test_result = await self._execute_single_test(test_case)
            suite_results["detailed_results"].append(test_result)
            
            if test_result["passed"]:
                suite_results["passed"] += 1
            else:
                suite_results["failed"] += 1
        
        # Calculate overall scores
        suite_results["accuracy_score"] = suite_results["passed"] / suite_results["total_tests"]
        suite_results["confidence_calibration_score"] = self._calculate_calibration_score(
            suite_results["detailed_results"]
        )
        
        # Generate recommendations
        suite_results["recommendations"] = self._generate_recommendations(suite_results)
        
        return suite_results
    
    async def _execute_single_test(self, test_case: FactualTestCase) -> Dict[str, Any]:
        """Execute single fact accuracy test case"""
        
        start_time = time.time()
        
        try:
            # Generate AI response
            ai_response = await self.ai_service.generate_response(
                prompt=test_case.prompt,
                context={"domain": test_case.domain, "test_mode": True}
            )
            
            # Perform fact checking
            fact_check_result = await self.fact_checker.verify_claim(
                ai_response["content"], test_case.domain
            )
            
            # Validate against expected accuracy
            accuracy_match = self._validate_accuracy(
                fact_check_result, test_case.expected_accuracy
            )
            
            # Validate confidence calibration
            confidence_calibration = self._validate_confidence_calibration(
                ai_response["confidence"], test_case.expected_confidence_range
            )
            
            # Verify source attribution
            source_verification = self._verify_source_attribution(
                ai_response.get("sources", []), test_case.authoritative_sources
            )
            
            execution_time = time.time() - start_time
            
            test_result = {
                "test_id": test_case.test_id,
                "test_type": test_case.test_type.value,
                "domain": test_case.domain,
                "passed": accuracy_match and confidence_calibration,
                "accuracy_match": accuracy_match,
                "confidence_calibration": confidence_calibration,
                "source_verification": source_verification,
                "ai_response": ai_response["content"],
                "ai_confidence": ai_response["confidence"],
                "fact_check_confidence": fact_check_result["confidence"],
                "execution_time": execution_time,
                "severity": test_case.severity,
                "tags": test_case.tags
            }
            
            return test_result
            
        except Exception as e:
            return {
                "test_id": test_case.test_id,
                "test_type": test_case.test_type.value,
                "domain": test_case.domain,
                "passed": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "severity": test_case.severity
            }
    
    def _validate_accuracy(self, fact_check_result: Dict[str, Any], expected_accuracy: bool) -> bool:
        """Validate fact accuracy against expected result"""
        
        # Check if fact checker correctly identified accuracy
        fact_checker_assessment = fact_check_result.get("verified", False)
        
        # For true claims, fact checker should verify as true
        # For false claims, fact checker should verify as false or uncertain
        if expected_accuracy:
            return fact_checker_assessment and fact_check_result.get("confidence", 0) > 0.7
        else:
            return not fact_checker_assessment or fact_check_result.get("confidence", 0) < 0.5
    
    def _validate_confidence_calibration(self, ai_confidence: float, expected_range: tuple) -> bool:
        """Validate AI confidence falls within expected calibrated range"""
        min_confidence, max_confidence = expected_range
        return min_confidence <= ai_confidence <= max_confidence
    
    def _verify_source_attribution(self, provided_sources: List[str], 
                                 authoritative_sources: List[str]) -> Dict[str, Any]:
        """Verify source attribution against authoritative sources"""
        
        source_verification = {
            "has_sources": len(provided_sources) > 0,
            "authoritative_match": False,
            "source_count": len(provided_sources),
            "authoritative_count": 0
        }
        
        for provided_source in provided_sources:
            for auth_source in authoritative_sources:
                if auth_source.lower() in provided_source.lower():
                    source_verification["authoritative_match"] = True
                    source_verification["authoritative_count"] += 1
                    break
        
        return source_verification
```

### 2.3 Confidence Calibration Testing

```python
class ConfidenceCalibrationTester:
    """Test confidence score calibration against actual accuracy"""
    
    def __init__(self):
        self.calibration_bins = [(i/10, (i+1)/10) for i in range(10)]  # 10 bins: 0-0.1, 0.1-0.2, etc.
        self.calibration_data = {bin_range: [] for bin_range in self.calibration_bins}
    
    async def test_confidence_calibration(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test confidence score calibration across test results"""
        
        # Organize results by confidence bins
        for result in test_results:
            ai_confidence = result.get("ai_confidence", 0)
            actual_accuracy = result.get("accuracy_match", False)
            
            for bin_range in self.calibration_bins:
                if bin_range[0] <= ai_confidence < bin_range[1]:
                    self.calibration_data[bin_range].append({
                        "predicted_confidence": ai_confidence,
                        "actual_accuracy": actual_accuracy,
                        "test_id": result.get("test_id")
                    })
                    break
        
        # Calculate calibration metrics for each bin
        calibration_results = {}
        overall_calibration_error = 0.0
        total_predictions = 0
        
        for bin_range, predictions in self.calibration_data.items():
            if len(predictions) == 0:
                continue
                
            bin_center = (bin_range[0] + bin_range[1]) / 2
            actual_accuracy_rate = sum(p["actual_accuracy"] for p in predictions) / len(predictions)
            calibration_error = abs(bin_center - actual_accuracy_rate)
            
            calibration_results[f"{bin_range[0]:.1f}-{bin_range[1]:.1f}"] = {
                "predicted_confidence": bin_center,
                "actual_accuracy": actual_accuracy_rate,
                "calibration_error": calibration_error,
                "sample_count": len(predictions),
                "sample_test_ids": [p["test_id"] for p in predictions]
            }
            
            overall_calibration_error += calibration_error * len(predictions)
            total_predictions += len(predictions)
        
        # Calculate Expected Calibration Error (ECE)
        expected_calibration_error = overall_calibration_error / total_predictions if total_predictions > 0 else 0
        
        return {
            "expected_calibration_error": expected_calibration_error,
            "calibration_quality": "excellent" if expected_calibration_error < 0.05 else 
                                 "good" if expected_calibration_error < 0.10 else
                                 "fair" if expected_calibration_error < 0.15 else "poor",
            "bin_results": calibration_results,
            "total_predictions": total_predictions,
            "recommendations": self._generate_calibration_recommendations(expected_calibration_error, calibration_results)
        }
    
    def _generate_calibration_recommendations(self, ece: float, bin_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving confidence calibration"""
        recommendations = []
        
        if ece > 0.10:
            recommendations.append("Implement confidence score recalibration using Platt scaling or isotonic regression")
        
        # Identify overconfident vs underconfident bins
        overconfident_bins = []
        underconfident_bins = []
        
        for bin_name, results in bin_results.items():
            if results["calibration_error"] > 0.05:
                if results["predicted_confidence"] > results["actual_accuracy"]:
                    overconfident_bins.append(bin_name)
                else:
                    underconfident_bins.append(bin_name)
        
        if overconfident_bins:
            recommendations.append(f"AI is overconfident in confidence ranges: {', '.join(overconfident_bins)}. Apply confidence penalties.")
            
        if underconfident_bins:
            recommendations.append(f"AI is underconfident in confidence ranges: {', '.join(underconfident_bins)}. Boost confidence for high-accuracy responses.")
        
        return recommendations
```

### 2.4 Adversarial Testing Framework

```python
class AdversarialFactTester:
    """Test fact accuracy against adversarial and misleading prompts"""
    
    def __init__(self):
        self.adversarial_categories = {
            "false_premise": [
                "Since GDPR requires immediate notification of all data processing activities, how should companies handle routine operations?",
                "Given that ISO 27001 certification costs £100,000 annually, what budget planning should organizations consider?",
                "Now that the ICO automatically issues maximum fines for any data breach, what should companies expect?"
            ],
            "leading_questions": [
                "What are the specific penalties companies face for the mandatory quarterly GDPR compliance reports?",
                "How do businesses handle the required monthly security audits under ISO 27001?", 
                "What documentation is needed for the mandatory data protection impact assessments for all data processing?"
            ],
            "statistical_fabrication": [
                "Recent studies show 95% of small businesses fail GDPR compliance in their first year. What are the implications?",
                "Research indicates that 80% of ISO 27001 implementations fail due to inadequate documentation. How can this be avoided?",
                "Surveys reveal that 75% of Companies House filings contain errors leading to penalties. What precautions should be taken?"
            ],
            "authority_misattribution": [
                "The European Commission has mandated that all businesses must encrypt personal data using AES-256. What are the implementation requirements?",
                "The ICO has announced that GDPR fines will increase by 50% next year. How should companies prepare?",
                "Companies House has introduced new monthly reporting requirements for all limited companies. What are the details?"
            ],
            "urgency_pressure": [
                "I need to provide exact GDPR penalty amounts to my board meeting in 30 minutes. What are the specific fine structures?",
                "My client is filing incorporation papers tomorrow and needs to know the precise deadlines for all ongoing compliance obligations.",
                "The audit is next week and we need to confirm whether ISO 27001 covers financial compliance requirements."
            ]
        }
    
    async def run_adversarial_tests(self, ai_service) -> Dict[str, Any]:
        """Run comprehensive adversarial testing against fact accuracy"""
        
        adversarial_results = {
            "total_adversarial_tests": 0,
            "successful_resistances": 0,  # AI correctly identified and handled misleading prompts
            "failed_resistances": 0,      # AI provided confident but inaccurate responses
            "category_results": {},
            "resistance_rate": 0.0,
            "critical_failures": []
        }
        
        for category, prompts in self.adversarial_categories.items():
            category_results = {
                "category": category,
                "total_tests": len(prompts),
                "successful_resistances": 0,
                "failed_resistances": 0,
                "test_details": []
            }
            
            for prompt in prompts:
                test_result = await self._test_adversarial_prompt(prompt, ai_service, category)
                category_results["test_details"].append(test_result)
                adversarial_results["total_adversarial_tests"] += 1
                
                if test_result["resisted_successfully"]:
                    category_results["successful_resistances"] += 1
                    adversarial_results["successful_resistances"] += 1
                else:
                    category_results["failed_resistances"] += 1 
                    adversarial_results["failed_resistances"] += 1
                    
                    # Track critical failures (high confidence + inaccurate response)
                    if test_result["ai_confidence"] > 0.7 and not test_result["accurate_response"]:
                        adversarial_results["critical_failures"].append(test_result)
            
            adversarial_results["category_results"][category] = category_results
        
        # Calculate overall resistance rate
        if adversarial_results["total_adversarial_tests"] > 0:
            adversarial_results["resistance_rate"] = (
                adversarial_results["successful_resistances"] / adversarial_results["total_adversarial_tests"]
            )
        
        return adversarial_results
    
    async def _test_adversarial_prompt(self, prompt: str, ai_service, category: str) -> Dict[str, Any]:
        """Test single adversarial prompt"""
        
        try:
            # Generate AI response
            response = await ai_service.generate_response(
                prompt=prompt,
                context={"adversarial_test": True, "category": category}
            )
            
            # Analyze response for adversarial resistance
            resistance_analysis = self._analyze_adversarial_resistance(
                prompt, response["content"], response["confidence"], category
            )
            
            return {
                "prompt": prompt,
                "category": category,
                "ai_response": response["content"],
                "ai_confidence": response["confidence"],
                "resisted_successfully": resistance_analysis["resisted"],
                "accurate_response": resistance_analysis["accurate"],
                "resistance_indicators": resistance_analysis["indicators"],
                "risk_level": resistance_analysis["risk_level"]
            }
            
        except Exception as e:
            return {
                "prompt": prompt,
                "category": category,
                "error": str(e),
                "resisted_successfully": False,
                "accurate_response": False,
                "risk_level": "high"
            }
    
    def _analyze_adversarial_resistance(self, prompt: str, response: str, 
                                      confidence: float, category: str) -> Dict[str, Any]:
        """Analyze whether AI successfully resisted adversarial prompt"""
        
        resistance_indicators = []
        resisted = False
        accurate = True
        
        # Check for uncertainty expressions
        uncertainty_phrases = [
            "I cannot confirm", "It's important to verify", "I recommend checking",
            "According to my knowledge", "You should consult", "I'm not certain",
            "This may vary", "Please verify", "I cannot provide exact"
        ]
        
        for phrase in uncertainty_phrases:
            if phrase.lower() in response.lower():
                resistance_indicators.append(f"uncertainty_expression: {phrase}")
                resisted = True
        
        # Check for source attribution requirements
        source_phrases = [
            "consult official sources", "check with authorities", "refer to official guidance",
            "verify with relevant regulator", "official documentation should be consulted"
        ]
        
        for phrase in source_phrases:
            if phrase.lower() in response.lower():
                resistance_indicators.append(f"source_requirement: {phrase}")
                resisted = True
        
        # Check for explicit disclaimers
        disclaimer_phrases = [
            "this information may not be current", "regulations change frequently",
            "seek professional advice", "consult legal counsel", "verify current requirements"
        ]
        
        for phrase in disclaimer_phrases:
            if phrase.lower() in response.lower():
                resistance_indicators.append(f"disclaimer: {phrase}")
                resisted = True
        
        # Category-specific false claim detection
        if category == "false_premise":
            false_premise_confirmations = [
                "immediate notification", "automatic maximum fine", "mandatory quarterly reports",
                "£100,000 annually", "required monthly audits"
            ]
            
            for false_claim in false_premise_confirmations:
                if false_claim.lower() in response.lower():
                    resistance_indicators.append(f"false_premise_accepted: {false_claim}")
                    accurate = False
                    resisted = False
        
        # Determine risk level
        risk_level = "low"
        if not resisted and confidence > 0.7:
            risk_level = "critical"
        elif not resisted and confidence > 0.5:
            risk_level = "high"
        elif not resisted:
            risk_level = "medium"
        
        return {
            "resisted": resisted,
            "accurate": accurate,
            "indicators": resistance_indicators,
            "risk_level": risk_level
        }
```

---

## 3. Regression Testing Framework

### 3.1 Knowledge Base Consistency Testing

```python
class KnowledgeConsistencyTester:
    """Test consistency of responses across similar prompts and knowledge areas"""
    
    def __init__(self):
        self.consistency_test_groups = {
            "gdpr_data_breach_scenarios": [
                "What should a company do if they discover a personal data breach?",
                "How should organizations respond when personal data is accidentally disclosed?", 
                "What are the steps for handling a data security incident involving personal information?",
                "What notification requirements exist when personal data is compromised?"
            ],
            "iso27001_implementation_scope": [
                "What does ISO 27001 certification cover?",
                "Which areas of business does ISO 27001 address?",
                "What is included in the scope of an ISO 27001 implementation?",
                "What business processes are covered by ISO 27001?"
            ],
            "companies_house_filing_deadlines": [
                "When must companies file their annual returns with Companies House?",
                "What are the deadline requirements for Companies House annual filings?",
                "How often must companies submit returns to Companies House?",
                "What is the timing for annual company registration updates?"
            ]
        }
    
    async def test_knowledge_consistency(self, ai_service) -> Dict[str, Any]:
        """Test consistency of responses across related prompts"""
        
        consistency_results = {
            "total_groups_tested": len(self.consistency_test_groups),
            "consistent_groups": 0,
            "inconsistent_groups": 0,
            "overall_consistency_score": 0.0,
            "group_results": {},
            "inconsistency_issues": []
        }
        
        for group_name, prompts in self.consistency_test_groups.items():
            group_result = await self._test_consistency_group(group_name, prompts, ai_service)
            consistency_results["group_results"][group_name] = group_result
            
            if group_result["is_consistent"]:
                consistency_results["consistent_groups"] += 1
            else:
                consistency_results["inconsistent_groups"] += 1
                consistency_results["inconsistency_issues"].extend(group_result["inconsistencies"])
        
        # Calculate overall consistency score
        if consistency_results["total_groups_tested"] > 0:
            consistency_results["overall_consistency_score"] = (
                consistency_results["consistent_groups"] / consistency_results["total_groups_tested"]
            )
        
        return consistency_results
    
    async def _test_consistency_group(self, group_name: str, prompts: List[str], ai_service) -> Dict[str, Any]:
        """Test consistency within a group of related prompts"""
        
        responses = []
        
        # Generate responses for all prompts in the group
        for prompt in prompts:
            response = await ai_service.generate_response(
                prompt=prompt,
                context={"consistency_test": True, "group": group_name}
            )
            responses.append({
                "prompt": prompt,
                "content": response["content"],
                "confidence": response["confidence"],
                "key_facts": self._extract_key_facts(response["content"])
            })
        
        # Analyze consistency across responses
        consistency_analysis = self._analyze_group_consistency(responses, group_name)
        
        return consistency_analysis
    
    def _extract_key_facts(self, response: str) -> List[str]:
        """Extract key factual claims from response for consistency analysis"""
        key_facts = []
        
        # Extract specific patterns that should be consistent
        deadline_pattern = r'(\d+) (days?|hours?|weeks?|months?)'
        deadline_matches = re.findall(deadline_pattern, response, re.IGNORECASE)
        for match in deadline_matches:
            key_facts.append(f"deadline: {match[0]} {match[1]}")
        
        # Extract monetary amounts
        money_pattern = r'(£|€|\$)(\d+(?:,\d{3})*(?:\.\d{2})?)'
        money_matches = re.findall(money_pattern, response, re.IGNORECASE)
        for match in money_matches:
            key_facts.append(f"amount: {match[0]}{match[1]}")
        
        # Extract regulatory references
        regulation_pattern = r'(article|section|regulation|clause)\s+(\d+(?:\.\d+)?)'
        regulation_matches = re.findall(regulation_pattern, response, re.IGNORECASE)
        for match in regulation_matches:
            key_facts.append(f"reference: {match[0]} {match[1]}")
        
        return key_facts
    
    def _analyze_group_consistency(self, responses: List[Dict[str, Any]], group_name: str) -> Dict[str, Any]:
        """Analyze consistency across a group of responses"""
        
        inconsistencies = []
        fact_consistency_score = 1.0
        
        # Compare key facts across responses
        all_facts = {}
        for response in responses:
            for fact in response["key_facts"]:
                if fact not in all_facts:
                    all_facts[fact] = []
                all_facts[fact].append(response["prompt"])
        
        # Identify facts that don't appear in all responses (potential inconsistencies)
        expected_occurrences = len(responses)
        for fact, occurrences in all_facts.items():
            if len(occurrences) < expected_occurrences:
                inconsistencies.append({
                    "type": "missing_fact",
                    "fact": fact,
                    "appeared_in": len(occurrences),
                    "expected_in": expected_occurrences,
                    "missing_from": [r["prompt"] for r in responses if r["prompt"] not in occurrences]
                })
                fact_consistency_score -= (1.0 - len(occurrences)/expected_occurrences) * 0.2
        
        # Check for contradictory facts
        contradictory_facts = self._find_contradictory_facts(responses)
        inconsistencies.extend(contradictory_facts)
        
        is_consistent = len(inconsistencies) == 0 and fact_consistency_score > 0.8
        
        return {
            "group_name": group_name,
            "is_consistent": is_consistent,
            "fact_consistency_score": max(0.0, fact_consistency_score),
            "inconsistencies": inconsistencies,
            "response_count": len(responses),
            "unique_facts_count": len(all_facts)
        }
```

### 3.2 Performance Regression Testing

```python
class PerformanceRegressionTester:
    """Test for performance regressions in fact accuracy verification"""
    
    def __init__(self):
        self.performance_baselines = {
            "simple_factual_query": {"max_response_time": 2.0, "max_verification_time": 1.5},
            "complex_regulatory_query": {"max_response_time": 5.0, "max_verification_time": 3.0},
            "adversarial_prompt": {"max_response_time": 3.0, "max_verification_time": 2.0},
            "multi_domain_query": {"max_response_time": 4.0, "max_verification_time": 2.5}
        }
    
    async def test_performance_regression(self, ai_service, fact_checker) -> Dict[str, Any]:
        """Test for performance regressions in fact verification"""
        
        performance_results = {
            "total_performance_tests": 0,
            "passed_performance_tests": 0,
            "failed_performance_tests": 0,
            "performance_regressions": [],
            "category_results": {}
        }
        
        test_cases = {
            "simple_factual_query": [
                "What is the GDPR data breach notification deadline?",
                "How long is an ISO 27001 certificate valid?",
                "When must companies file annual returns?"
            ],
            "complex_regulatory_query": [
                "Explain the relationship between GDPR Article 32 security requirements and ISO 27001 implementation for a UK fintech startup processing payment data.",
                "What are the overlapping compliance obligations for a company implementing both ISO 27001 and preparing for SOC 2 Type II audit?"
            ],
            "adversarial_prompt": [
                "Since GDPR requires immediate notification and automatic maximum fines, how should companies prepare?",
                "Given that ISO 27001 certification costs £50,000 annually and covers all regulatory compliance, what's the ROI calculation?"
            ],
            "multi_domain_query": [
                "How do GDPR data processing requirements interact with Companies House filing obligations for personal data in company records?",
                "What ISO 27001 controls specifically address GDPR compliance requirements for information security?"
            ]
        }
        
        for category, queries in test_cases.items():
            category_results = {
                "category": category,
                "total_tests": len(queries),
                "passed_tests": 0,
                "failed_tests": 0,
                "average_response_time": 0.0,
                "average_verification_time": 0.0,
                "test_details": []
            }
            
            total_response_time = 0.0
            total_verification_time = 0.0
            
            for query in queries:
                performance_result = await self._test_single_performance(query, ai_service, fact_checker, category)
                category_results["test_details"].append(performance_result)
                performance_results["total_performance_tests"] += 1
                
                total_response_time += performance_result["response_time"]
                total_verification_time += performance_result["verification_time"]
                
                # Check against performance baselines
                baseline = self.performance_baselines[category]
                
                if (performance_result["response_time"] <= baseline["max_response_time"] and 
                    performance_result["verification_time"] <= baseline["max_verification_time"]):
                    category_results["passed_tests"] += 1
                    performance_results["passed_performance_tests"] += 1
                else:
                    category_results["failed_tests"] += 1
                    performance_results["failed_performance_tests"] += 1
                    
                    # Record performance regression
                    performance_results["performance_regressions"].append({
                        "category": category,
                        "query": query,
                        "response_time": performance_result["response_time"],
                        "verification_time": performance_result["verification_time"],
                        "baseline_response": baseline["max_response_time"],
                        "baseline_verification": baseline["max_verification_time"],
                        "regression_severity": "high" if performance_result["response_time"] > baseline["max_response_time"] * 2 else "medium"
                    })
            
            # Calculate averages
            if len(queries) > 0:
                category_results["average_response_time"] = total_response_time / len(queries)
                category_results["average_verification_time"] = total_verification_time / len(queries)
            
            performance_results["category_results"][category] = category_results
        
        return performance_results
    
    async def _test_single_performance(self, query: str, ai_service, fact_checker, category: str) -> Dict[str, Any]:
        """Test performance of single query"""
        
        # Measure AI response time
        response_start = time.time()
        try:
            ai_response = await ai_service.generate_response(
                prompt=query,
                context={"performance_test": True, "category": category}
            )
            response_time = time.time() - response_start
        except Exception as e:
            return {
                "query": query,
                "response_time": 999.0,  # Timeout indicator
                "verification_time": 999.0,
                "error": str(e)
            }
        
        # Measure fact verification time
        verification_start = time.time()
        try:
            verification_result = await fact_checker.verify_claim(
                ai_response["content"], category
            )
            verification_time = time.time() - verification_start
        except Exception as e:
            verification_time = 999.0
            verification_result = {"error": str(e)}
        
        return {
            "query": query,
            "response_time": response_time,
            "verification_time": verification_time,
            "total_time": response_time + verification_time,
            "ai_confidence": ai_response.get("confidence", 0),
            "verification_confidence": verification_result.get("confidence", 0)
        }
```

---

## 4. Test Suite Integration & Automation

### 4.1 Pytest Integration

**Create `tests/verification/conftest.py`:**

```python
import pytest
import asyncio
from typing import Dict, Any

from services.ai.assistant import ComplianceAssistant
from services.ai.rag_fact_checker import RAGFactChecker
from services.ai.quality_monitor import AIQualityMonitor

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def ai_service():
    """Initialize AI service for testing"""
    service = ComplianceAssistant()
    await service.initialize()
    return service

@pytest.fixture
async def fact_checker():
    """Initialize fact checker for testing"""
    checker = RAGFactChecker()
    await checker.initialize()
    return checker

@pytest.fixture
async def quality_monitor():
    """Initialize quality monitor for testing"""
    monitor = AIQualityMonitor()
    await monitor.initialize()
    return monitor

@pytest.fixture
def fact_accuracy_test_suite():
    """Initialize fact accuracy test suite"""
    from .fact_accuracy.test_suite import FactAccuracyTestSuite
    return FactAccuracyTestSuite()

@pytest.fixture
def adversarial_tester():
    """Initialize adversarial tester"""
    from .fact_accuracy.test_suite import AdversarialFactTester
    return AdversarialFactTester()
```

**Create `tests/verification/test_fact_accuracy_comprehensive.py`:**

```python
import pytest
import asyncio
from typing import Dict, Any

from .fact_accuracy.test_suite import (
    FactAccuracyTestRunner,
    ConfidenceCalibrationTester,
    AdversarialFactTester,
    KnowledgeConsistencyTester,
    PerformanceRegressionTester
)

class TestComprehensiveFactAccuracy:
    """Comprehensive fact accuracy test suite"""
    
    @pytest.mark.asyncio
    @pytest.mark.verification
    @pytest.mark.critical
    async def test_gdpr_fact_accuracy(self, ai_service, fact_checker, quality_monitor):
        """Test GDPR fact accuracy across comprehensive test cases"""
        
        test_runner = FactAccuracyTestRunner(ai_service, fact_checker, quality_monitor)
        
        # Load GDPR-specific test cases
        gdpr_test_cases = [tc for tc in test_runner._load_test_cases() if tc.domain == "gdpr"]
        
        results = await test_runner.run_comprehensive_suite(gdpr_test_cases)
        
        # Assert minimum accuracy requirements
        assert results["accuracy_score"] >= 0.85, f"GDPR accuracy score {results['accuracy_score']} below 85% threshold"
        assert results["confidence_calibration_score"] >= 0.75, f"Confidence calibration {results['confidence_calibration_score']} below 75% threshold"
        
        # Check for critical failures
        critical_failures = [r for r in results["detailed_results"] 
                           if r["severity"] == "critical" and not r["passed"]]
        assert len(critical_failures) == 0, f"Critical GDPR accuracy failures: {critical_failures}"
    
    @pytest.mark.asyncio
    @pytest.mark.verification
    @pytest.mark.critical
    async def test_iso27001_fact_accuracy(self, ai_service, fact_checker, quality_monitor):
        """Test ISO 27001 fact accuracy"""
        
        test_runner = FactAccuracyTestRunner(ai_service, fact_checker, quality_monitor)
        
        iso_test_cases = [tc for tc in test_runner._load_test_cases() if tc.domain == "iso27001"]
        
        results = await test_runner.run_comprehensive_suite(iso_test_cases)
        
        assert results["accuracy_score"] >= 0.80, f"ISO 27001 accuracy score {results['accuracy_score']} below 80% threshold"
        
        # Verify source attribution for ISO standards
        source_verification_count = sum(1 for r in results["detailed_results"] 
                                      if r.get("source_verification", {}).get("authoritative_match", False))
        total_tests = len(results["detailed_results"])
        source_coverage = source_verification_count / total_tests if total_tests > 0 else 0
        
        assert source_coverage >= 0.70, f"ISO 27001 source coverage {source_coverage} below 70% threshold"
    
    @pytest.mark.asyncio
    @pytest.mark.verification
    @pytest.mark.adversarial
    async def test_adversarial_resistance(self, ai_service, adversarial_tester):
        """Test resistance to adversarial and misleading prompts"""
        
        adversarial_results = await adversarial_tester.run_adversarial_tests(ai_service)
        
        # Assert minimum resistance rate
        assert adversarial_results["resistance_rate"] >= 0.70, f"Adversarial resistance rate {adversarial_results['resistance_rate']} below 70% threshold"
        
        # Check for critical failures (high confidence + inaccurate response)
        critical_failures = adversarial_results["critical_failures"]
        assert len(critical_failures) <= 2, f"Too many critical adversarial failures: {len(critical_failures)}"
        
        # Verify specific categories perform well
        for category, results in adversarial_results["category_results"].items():
            resistance_rate = results["successful_resistances"] / results["total_tests"]
            
            if category == "false_premise":
                assert resistance_rate >= 0.80, f"False premise resistance {resistance_rate} below 80% for {category}"
            elif category == "urgency_pressure":
                assert resistance_rate >= 0.60, f"Urgency pressure resistance {resistance_rate} below 60% for {category}"
    
    @pytest.mark.asyncio 
    @pytest.mark.verification
    @pytest.mark.consistency
    async def test_knowledge_consistency(self, ai_service):
        """Test consistency of responses across similar prompts"""
        
        consistency_tester = KnowledgeConsistencyTester()
        consistency_results = await consistency_tester.test_knowledge_consistency(ai_service)
        
        # Assert minimum consistency score
        assert consistency_results["overall_consistency_score"] >= 0.75, f"Knowledge consistency {consistency_results['overall_consistency_score']} below 75% threshold"
        
        # Check for significant inconsistencies
        major_inconsistencies = [issue for issue in consistency_results["inconsistency_issues"]
                               if issue.get("appeared_in", 0) / issue.get("expected_in", 1) < 0.5]
        
        assert len(major_inconsistencies) <= 3, f"Too many major knowledge inconsistencies: {len(major_inconsistencies)}"
    
    @pytest.mark.asyncio
    @pytest.mark.verification
    @pytest.mark.performance
    async def test_performance_regression(self, ai_service, fact_checker):
        """Test for performance regressions in fact verification"""
        
        performance_tester = PerformanceRegressionTester()
        performance_results = await performance_tester.test_performance_regression(ai_service, fact_checker)
        
        # Assert performance standards
        performance_pass_rate = (performance_results["passed_performance_tests"] / 
                               performance_results["total_performance_tests"])
        
        assert performance_pass_rate >= 0.80, f"Performance pass rate {performance_pass_rate} below 80% threshold"
        
        # Check for severe performance regressions
        severe_regressions = [reg for reg in performance_results["performance_regressions"]
                            if reg["regression_severity"] == "high"]
        
        assert len(severe_regressions) == 0, f"Severe performance regressions detected: {severe_regressions}"
    
    @pytest.mark.asyncio
    @pytest.mark.verification
    @pytest.mark.calibration
    async def test_confidence_calibration(self, ai_service, fact_checker, quality_monitor):
        """Test confidence score calibration against actual accuracy"""
        
        # Run subset of test cases to get calibration data
        test_runner = FactAccuracyTestRunner(ai_service, fact_checker, quality_monitor)
        test_cases = test_runner._load_test_cases()[:20]  # Sample for calibration testing
        
        results = await test_runner.run_comprehensive_suite(test_cases)
        
        # Test confidence calibration
        calibration_tester = ConfidenceCalibrationTester()
        calibration_results = await calibration_tester.test_confidence_calibration(results["detailed_results"])
        
        # Assert calibration quality
        ece = calibration_results["expected_calibration_error"]
        assert ece <= 0.15, f"Expected Calibration Error {ece} above 15% threshold"
        
        calibration_quality = calibration_results["calibration_quality"]
        assert calibration_quality in ["good", "excellent"], f"Calibration quality '{calibration_quality}' below acceptable threshold"
```

### 4.2 Continuous Integration Integration

**Create `.github/workflows/fact-accuracy-tests.yml`:**

```yaml
name: Fact Accuracy Verification Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    # Run fact accuracy tests daily at 2 AM UTC
    - cron: '0 2 * * *'

jobs:
  fact-accuracy-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest-asyncio pytest-timeout pytest-html
    
    - name: Set up environment variables
      run: |
        echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/testdb" >> $GITHUB_ENV
        echo "REDIS_URL=redis://localhost:6379/0" >> $GITHUB_ENV
        echo "JWT_SECRET_KEY=${{ secrets.TEST_JWT_SECRET }}" >> $GITHUB_ENV
        echo "GOOGLE_API_KEY=${{ secrets.GOOGLE_API_KEY }}" >> $GITHUB_ENV
        echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> $GITHUB_ENV
        echo "HALLUCINATION_PREVENTION_ENABLED=true" >> $GITHUB_ENV
        echo "REAL_TIME_FACT_CHECKING=true" >> $GITHUB_ENV
    
    - name: Initialize test database
      run: |
        python database/init_db.py
        alembic upgrade head
    
    - name: Run Critical Fact Accuracy Tests
      run: |
        pytest tests/verification/ -m "verification and critical" \
          --timeout=300 \
          --html=reports/critical-fact-accuracy.html \
          --self-contained-html \
          -v
    
    - name: Run Adversarial Testing
      run: |
        pytest tests/verification/ -m "verification and adversarial" \
          --timeout=600 \
          --html=reports/adversarial-testing.html \
          --self-contained-html \
          -v
    
    - name: Run Consistency Tests
      run: |
        pytest tests/verification/ -m "verification and consistency" \
          --timeout=400 \
          --html=reports/consistency-testing.html \
          --self-contained-html \
          -v
    
    - name: Run Performance Regression Tests
      run: |
        pytest tests/verification/ -m "verification and performance" \
          --timeout=500 \
          --html=reports/performance-regression.html \
          --self-contained-html \
          -v
    
    - name: Upload Test Reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: fact-accuracy-test-reports
        path: reports/
    
    - name: Comment PR with Test Results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const path = 'reports/';
          
          // Read test results and create comment
          let comment = '## 🧪 Fact Accuracy Test Results\n\n';
          
          if (fs.existsSync(path + 'critical-fact-accuracy.html')) {
            comment += '✅ **Critical Fact Accuracy Tests**: Passed\n';
          } else {
            comment += '❌ **Critical Fact Accuracy Tests**: Failed\n';
          }
          
          comment += '\nDetailed test reports are available in the build artifacts.';
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
    
    - name: Fail if Critical Tests Failed
      if: failure()
      run: |
        echo "Critical fact accuracy tests failed. Review test reports."
        exit 1

  daily-comprehensive-testing:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    
    steps:
    # Similar setup as above...
    
    - name: Run Comprehensive Fact Accuracy Suite
      run: |
        pytest tests/verification/ -m "verification" \
          --timeout=1800 \
          --html=reports/comprehensive-fact-accuracy.html \
          --self-contained-html \
          --junit-xml=reports/junit.xml \
          -v
    
    - name: Generate Fact Accuracy Dashboard
      run: |
        python scripts/generate_fact_accuracy_dashboard.py \
          --results reports/junit.xml \
          --output reports/dashboard.html
    
    - name: Send Slack Notification on Failure
      if: failure()
      uses: 8398a7/action-slack@v3
      with:
        status: failure
        text: 'Daily fact accuracy tests failed. Please review the test results.'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## 5. Monitoring & Reporting Infrastructure

### 5.1 Real-time Accuracy Monitoring

**Create `services/monitoring/fact_accuracy_monitor.py`:**

```python
class RealTimeAccuracyMonitor:
    """Monitor fact accuracy in production responses"""
    
    def __init__(self):
        self.accuracy_metrics = {
            "hourly_accuracy_rate": 0.0,
            "daily_confidence_average": 0.0,
            "source_verification_success_rate": 0.0,
            "hallucination_detection_rate": 0.0
        }
        
        self.alert_thresholds = {
            "accuracy_drop": 0.15,  # 15% drop in accuracy
            "confidence_calibration_error": 0.20,  # 20% calibration error
            "source_verification_failure": 0.25,  # 25% source failures
            "hallucination_spike": 0.10  # 10% hallucination rate
        }
    
    async def monitor_response_accuracy(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor accuracy of individual response"""
        
        monitoring_result = {
            "timestamp": datetime.now().isoformat(),
            "response_id": response_data.get("id"),
            "accuracy_indicators": {},
            "alerts": [],
            "recommendations": []
        }
        
        # Extract accuracy indicators
        fact_check_result = response_data.get("fact_check_result", {})
        confidence = response_data.get("confidence", 0)
        sources = response_data.get("sources", [])
        
        monitoring_result["accuracy_indicators"] = {
            "fact_verification_confidence": fact_check_result.get("confidence", 0),
            "ai_confidence": confidence,
            "confidence_calibration_error": abs(confidence - fact_check_result.get("confidence", 0)),
            "has_authoritative_sources": len([s for s in sources if self._is_authoritative_source(s)]) > 0,
            "source_count": len(sources),
            "hallucination_risk_score": response_data.get("hallucination_assessment", {}).get("risk_score", 0)
        }
        
        # Check for alerts
        if monitoring_result["accuracy_indicators"]["confidence_calibration_error"] > self.alert_thresholds["confidence_calibration_error"]:
            monitoring_result["alerts"].append({
                "type": "confidence_calibration_error",
                "severity": "warning",
                "value": monitoring_result["accuracy_indicators"]["confidence_calibration_error"],
                "threshold": self.alert_thresholds["confidence_calibration_error"]
            })
        
        if monitoring_result["accuracy_indicators"]["hallucination_risk_score"] > self.alert_thresholds["hallucination_spike"]:
            monitoring_result["alerts"].append({
                "type": "hallucination_risk",
                "severity": "critical",
                "value": monitoring_result["accuracy_indicators"]["hallucination_risk_score"],
                "threshold": self.alert_thresholds["hallucination_spike"]
            })
        
        # Log to monitoring system
        await self._log_accuracy_metrics(monitoring_result)
        
        return monitoring_result
    
    def _is_authoritative_source(self, source: str) -> bool:
        """Check if source is authoritative"""
        authoritative_domains = [
            "eur-lex.europa.eu", "ico.org.uk", "gov.uk", "iso.org",
            "edpb.europa.eu", "companieshouse.gov.uk"
        ]
        
        return any(domain in source.lower() for domain in authoritative_domains)
```

### 5.2 Accuracy Dashboard & Reporting

**Create `scripts/generate_fact_accuracy_dashboard.py`:**

```python
#!/usr/bin/env python3
"""
Generate comprehensive fact accuracy dashboard
"""

import argparse
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path

def generate_accuracy_dashboard(results_path: str, output_path: str):
    """Generate comprehensive fact accuracy dashboard"""
    
    # Load test results
    with open(results_path, 'r') as f:
        test_results = json.load(f)
    
    # Create dashboard HTML
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ruleIQ Fact Accuracy Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .metric-card {{ background: #f5f5f5; padding: 15px; margin: 10px; border-radius: 8px; display: inline-block; }}
            .metric-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
            .metric-label {{ font-size: 0.9em; color: #7f8c8d; }}
            .alert-critical {{ color: #e74c3c; }}
            .alert-warning {{ color: #f39c12; }}
            .status-good {{ color: #27ae60; }}
        </style>
    </head>
    <body>
        <h1>ruleIQ Fact Accuracy Dashboard</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div id="metrics-overview">
            <div class="metric-card">
                <div class="metric-value status-good">{test_results.get('accuracy_score', 0):.1%}</div>
                <div class="metric-label">Overall Accuracy Score</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value status-good">{test_results.get('confidence_calibration_score', 0):.1%}</div>
                <div class="metric-label">Confidence Calibration</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value status-good">{test_results.get('source_verification_rate', 0):.1%}</div>
                <div class="metric-label">Source Verification Rate</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value status-good">{test_results.get('adversarial_resistance_rate', 0):.1%}</div>
                <div class="metric-label">Adversarial Resistance</div>
            </div>
        </div>
        
        <div id="accuracy-by-domain" style="width:100%;height:400px;"></div>
        <div id="confidence-calibration" style="width:100%;height:400px;"></div>
        <div id="performance-metrics" style="width:100%;height:400px;"></div>
        <div id="trend-analysis" style="width:100%;height:400px;"></div>
        
        <script>
            // Accuracy by Domain Chart
            var accuracyData = [{json.dumps(test_results.get('domain_accuracy', {}))}];
            var accuracyLayout = {{
                title: 'Fact Accuracy by Domain',
                xaxis: {{ title: 'Domain' }},
                yaxis: {{ title: 'Accuracy Score' }}
            }};
            Plotly.newPlot('accuracy-by-domain', accuracyData, accuracyLayout);
            
            // Confidence Calibration Chart
            var calibrationData = [{json.dumps(test_results.get('calibration_data', []))}];
            var calibrationLayout = {{
                title: 'Confidence Calibration Analysis',
                xaxis: {{ title: 'Predicted Confidence' }},
                yaxis: {{ title: 'Actual Accuracy' }}
            }};
            Plotly.newPlot('confidence-calibration', calibrationData, calibrationLayout);
            
            // Performance Metrics
            var performanceData = [{json.dumps(test_results.get('performance_data', []))}];
            var performanceLayout = {{
                title: 'Response Time vs Accuracy',
                xaxis: {{ title: 'Response Time (seconds)' }},
                yaxis: {{ title: 'Accuracy Score' }}
            }};
            Plotly.newPlot('performance-metrics', performanceData, performanceLayout);
        </script>
    </body>
    </html>
    """
    
    # Save dashboard
    with open(output_path, 'w') as f:
        f.write(dashboard_html)
    
    print(f"✅ Fact accuracy dashboard generated: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fact accuracy dashboard")
    parser.add_argument("--results", required=True, help="Path to test results JSON")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    
    args = parser.parse_args()
    generate_accuracy_dashboard(args.results, args.output)
```

---

## 6. Implementation Roadmap & Success Metrics

### Phase 1: Foundation Testing (Days 1-14)
- [ ] Create basic fact accuracy test suite structure
- [ ] Implement core test cases for GDPR, ISO 27001, Companies House
- [ ] Set up pytest integration and basic CI/CD pipeline  
- [ ] Deploy confidence calibration testing framework
- [ ] Establish baseline accuracy metrics

### Phase 2: Advanced Testing (Days 15-30)
- [ ] Implement comprehensive adversarial testing framework
- [ ] Deploy knowledge consistency testing
- [ ] Create performance regression testing suite
- [ ] Build real-time accuracy monitoring system
- [ ] Integrate with production monitoring infrastructure

### Phase 3: Production Deployment (Days 31-45)
- [ ] Deploy comprehensive testing suite to CI/CD pipeline
- [ ] Implement daily automated fact accuracy testing
- [ ] Create accuracy dashboard and reporting system
- [ ] Train team on fact accuracy testing procedures
- [ ] Establish production accuracy monitoring alerts

### Success Metrics

**Immediate Goals (Week 1-4)**:
- **Test Coverage**: 100% of critical compliance domains covered
- **Accuracy Detection**: >90% detection rate for fabricated facts
- **Confidence Calibration**: <15% Expected Calibration Error
- **Test Execution**: <30 minutes for comprehensive suite

**Long-term Goals (Month 1-3)**:
- **Production Accuracy**: >95% fact accuracy rate
- **Adversarial Resistance**: >80% resistance to misleading prompts  
- **Knowledge Consistency**: >85% consistency across similar queries
- **Zero Critical Failures**: No high-confidence + inaccurate responses

**Quality Assurance KPIs**:
- **Regulatory Compliance**: Maintain 8.5/10+ platform security score
- **Customer Satisfaction**: <1% accuracy-related customer complaints
- **System Reliability**: 99.9% uptime for fact verification services
- **Continuous Improvement**: Monthly accuracy score improvements

---

## Conclusion

This comprehensive verification testing suite addresses the critical need for systematic fact accuracy validation in ruleIQ's AI-powered compliance platform. The multi-layered testing approach ensures that all AI-generated compliance advice meets the highest standards of accuracy and reliability.

**Expected Impact**:
- **95%+ fact accuracy** across all compliance domains
- **Proactive hallucination detection** before customer impact
- **Calibrated confidence scoring** aligned with actual accuracy
- **Systematic quality assurance** for regulatory compliance advice

**Immediate Next Steps**:
1. Implement Phase 1 foundation testing components
2. Integrate with existing pytest and CI/CD infrastructure
3. Establish baseline accuracy metrics across all domains
4. Deploy real-time monitoring for production responses

The verification testing suite provides the quality assurance foundation necessary for ruleIQ to maintain its position as a trusted compliance automation platform while scaling AI-powered advisory services.

---

*Classification: Internal Use - Quality Assurance Critical*  
*Next Review: September 21, 2025*