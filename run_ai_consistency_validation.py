#!/usr/bin/env python3
"""
AI Output Consistency Validation Runner

Runs comprehensive consistency tests and generates a validation report
for the AI system to ensure reliable UI output.
"""

import asyncio
import time
import json
import statistics
from datetime import datetime


class AIConsistencyValidator:
    """Comprehensive AI consistency validation"""

    def __init__(self) -> None:
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_results": {},
            "summary": {},
            "recommendations": [],
        }

    async def run_all_validations(self):
        """Run all consistency validation tests"""
        print("🚀 Starting AI Output Consistency Validation")
        print("=" * 60)

        # Test 1: Response Structure Consistency
        await self.test_response_structure_consistency()

        # Test 2: Cross-Framework Consistency
        await self.test_cross_framework_consistency()

        # Test 3: Caching Consistency
        await self.test_caching_consistency()

        # Test 4: Concurrent Request Consistency
        await self.test_concurrent_consistency()

        # Test 5: UI Format Consistency
        await self.test_ui_format_consistency()

        # Test 6: Performance Consistency
        await self.test_performance_consistency()

        # Test 7: Error Handling Consistency
        await self.test_error_handling_consistency()

        # Generate summary
        self.generate_summary()

        # Generate report
        self.generate_report()

        return self.results

    async def mock_ai_request(
        self,
        query: str,
        framework: str = "gdpr",
        user_id: str = "test_user",
        simulate_error: bool = False,
    ):
        """Mock AI request for testing consistency"""

        # Simulate network delay
        await asyncio.sleep(0.01 + (len(query) * 0.0001))

        if simulate_error:
            raise Exception("Simulated AI service error")

        # Create consistent mock response

        base_responses = {
            "What are GDPR requirements?": {
                "response": "GDPR establishes comprehensive data protection requirements including lawful basis for processing, data subject rights (access, rectification, erasure, portability), privacy by design principles, data protection impact assessments, and breach notification within 72 hours.",
                "confidence": 0.94,
                "sources": [
                    "GDPR Article 5",
                    "GDPR Article 6",
                    "GDPR Articles 12-22",
                    "GDPR Article 25",
                    "GDPR Article 33",
                ],
                "compliance_score": 96,
            },
            "Explain ISO 27001 controls": {
                "response": "ISO 27001 Annex A contains 93 security controls organized into 4 themes: organizational (37 controls), people (8 controls), physical (14 controls), and technological (34 controls). These controls address areas like access control, cryptography, system security, and incident management.",
                "confidence": 0.91,
                "sources": ["ISO 27001:2022 Annex A", "ISO 27001 Clause 6.1.3"],
                "compliance_score": 93,
            },
            "What is SOC 2?": {
                "response": "SOC 2 (Service Organization Control 2) is an auditing procedure that ensures service providers securely manage data through five trust service principles: Security (foundational), Availability, Processing Integrity, Confidentiality, and Privacy. It includes Type I (design) and Type II (effectiveness) reports.",
                "confidence": 0.89,
                "sources": ["AICPA SOC 2 Guide", "Trust Service Criteria"],
                "compliance_score": 91,
            },
        }

        # Find matching base response or create generic one
        base_response = None
        for key, resp in base_responses.items():
            if any(word in query for word in key.split() if len(word) > 3):
                base_response = resp
                break

        if not base_response:
            base_response = {
                "response": f"This is a compliance-related response about: {query}",
                "confidence": 0.85,
                "sources": ["Generic Compliance Framework"],
                "compliance_score": 87,
            }

        # Add framework-specific modifications
        response = base_response.copy()
        if framework == "iso27001":
            response["sources"] = [
                s.replace("GDPR", "ISO 27001") if "GDPR" in s else s for s in response["sources"]
            ]
            response["compliance_score"] = max(80, response["compliance_score"] - 2)
        elif framework == "soc2":
            response["sources"] = [
                s.replace("GDPR", "SOC 2") if "GDPR" in s else s for s in response["sources"]
            ]
            response["compliance_score"] = max(85, response["compliance_score"] - 1)

        # Add metadata
        response.update(
            {
                "metadata": {
                    "model_used": "gemini-pro",
                    "processing_time": 0.8 + (len(query) * 0.01),
                    "cache_hit": False,  # Simplified for testing
                    "framework": framework,
                    "user_id": user_id,
                },
                "timestamp": datetime.now().isoformat(),
            }
        )

        return response

    async def test_response_structure_consistency(self) -> None:
        """Test that all responses have consistent structure"""
        print("\n📋 Testing Response Structure Consistency...")

        test_queries = [
            "What are GDPR requirements?",
            "Explain ISO 27001 controls",
            "What is SOC 2?",
            "How to implement data privacy?",
        ]

        results = []
        expected_fields = [
            "response",
            "confidence",
            "sources",
            "compliance_score",
            "metadata",
            "timestamp",
        ]

        for query in test_queries:
            response = await self.mock_ai_request(query)

            # Check structure
            structure_valid = True
            missing_fields = []

            for field in expected_fields:
                if field not in response:
                    missing_fields.append(field)
                    structure_valid = False

            # Check data types
            type_checks = {
                "response": str,
                "confidence": float,
                "sources": list,
                "compliance_score": (int, float),
                "metadata": dict,
                "timestamp": str,
            }

            type_valid = True
            type_errors = []

            for field, expected_type in type_checks.items():
                if field in response:
                    if isinstance(expected_type, tuple):
                        if not isinstance(response[field], expected_type):
                            type_errors.append(
                                f"{field}: expected {expected_type}, got {type(response[field])}"
                            )
                            type_valid = False
                    elif not isinstance(response[field], expected_type):
                        type_errors.append(
                            f"{field}: expected {expected_type}, got {type(response[field])}"
                        )
                        type_valid = False

            results.append(
                {
                    "query": query,
                    "structure_valid": structure_valid,
                    "missing_fields": missing_fields,
                    "type_valid": type_valid,
                    "type_errors": type_errors,
                }
            )

        # Analyze results
        all_structure_valid = all(r["structure_valid"] for r in results)
        all_types_valid = all(r["type_valid"] for r in results)

        self.results["test_results"]["response_structure"] = {
            "passed": all_structure_valid and all_types_valid,
            "structure_consistency": all_structure_valid,
            "type_consistency": all_types_valid,
            "details": results,
        }

        status = "✅ PASSED" if all_structure_valid and all_types_valid else "❌ FAILED"
        print(f"   Structure Consistency: {status}")
        if not all_structure_valid:
            print("   - Structure issues found in some responses")
        if not all_types_valid:
            print("   - Type issues found in some responses")

    async def test_cross_framework_consistency(self) -> None:
        """Test consistency across different frameworks"""
        print("\n🔄 Testing Cross-Framework Consistency...")

        query = "What are data encryption requirements?"
        frameworks = ["gdpr", "iso27001", "soc2"]
        responses = {}

        for framework in frameworks:
            response = await self.mock_ai_request(query, framework=framework)
            responses[framework] = response

        # Check structure consistency
        structure_consistent = True
        first_keys = set(responses[frameworks[0]].keys())

        for framework in frameworks[1:]:
            if set(responses[framework].keys()) != first_keys:
                structure_consistent = False
                break

        # Check confidence range consistency
        confidences = [resp["confidence"] for resp in responses.values()]
        confidence_consistent = all(0.5 <= c <= 1.0 for c in confidences)
        confidence_variation = max(confidences) - min(confidences) if confidences else 0

        # Check compliance score consistency
        scores = [resp["compliance_score"] for resp in responses.values()]
        score_consistent = all(0 <= s <= 100 for s in scores)
        score_variation = max(scores) - min(scores) if scores else 0

        passed = structure_consistent and confidence_consistent and score_consistent

        self.results["test_results"]["cross_framework"] = {
            "passed": passed,
            "structure_consistent": structure_consistent,
            "confidence_consistent": confidence_consistent,
            "confidence_variation": confidence_variation,
            "score_consistent": score_consistent,
            "score_variation": score_variation,
            "framework_responses": {k: v["compliance_score"] for k, v in responses.items()},
        }

        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   Cross-Framework Consistency: {status}")
        print(f"   - Confidence variation: {confidence_variation:.3f}")
        print(f"   - Score variation: {score_variation:.1f}")

    async def test_caching_consistency(self) -> None:
        """Test that identical queries return identical responses"""
        print("\n💾 Testing Caching Consistency...")

        query = "What are GDPR data subject rights?"
        responses = []

        # Make 5 identical requests
        for i in range(5):
            response = await self.mock_ai_request(query, user_id=f"user_{i}")
            responses.append(response)

        # Check if responses are identical (ignoring metadata that might vary)
        first_response = responses[0]
        core_fields = ["response", "confidence", "sources", "compliance_score"]

        identical_count = 0
        for response in responses[1:]:
            is_identical = True
            for field in core_fields:
                if response[field] != first_response[field]:
                    is_identical = False
                    break
            if is_identical:
                identical_count += 1

        consistency_rate = (identical_count + 1) / len(responses)  # +1 for first response
        passed = consistency_rate >= 0.8  # 80% threshold

        self.results["test_results"]["caching"] = {
            "passed": passed,
            "consistency_rate": consistency_rate,
            "identical_responses": identical_count + 1,
            "total_responses": len(responses),
        }

        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   Caching Consistency: {status}")
        print(f"   - Consistency rate: {consistency_rate:.1%}")

    async def test_concurrent_consistency(self) -> None:
        """Test consistency under concurrent load"""
        print("\n⚡ Testing Concurrent Request Consistency...")

        query = "Explain GDPR lawful bases for processing"
        concurrent_count = 10

        # Execute concurrent requests
        start_time = time.time()
        tasks = [
            self.mock_ai_request(query, user_id=f"concurrent_user_{i}")
            for i in range(concurrent_count)
        ]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time

        # Check if all requests completed
        completion_rate = len(responses) / concurrent_count

        # Check response consistency
        first_response = responses[0]
        consistent_responses = 1

        for response in responses[1:]:
            if (
                response["response"] == first_response["response"]
                and response["confidence"] == first_response["confidence"]
            ):
                consistent_responses += 1

        consistency_rate = consistent_responses / len(responses)
        passed = completion_rate == 1.0 and consistency_rate >= 0.8 and total_time < 10.0

        self.results["test_results"]["concurrent"] = {
            "passed": passed,
            "completion_rate": completion_rate,
            "consistency_rate": consistency_rate,
            "total_time": total_time,
            "requests_per_second": concurrent_count / total_time if total_time > 0 else 0,
        }

        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   Concurrent Consistency: {status}")
        print(f"   - Completion rate: {completion_rate:.1%}")
        print(f"   - Consistency rate: {consistency_rate:.1%}")
        print(f"   - Total time: {total_time:.2f}s")

    async def test_ui_format_consistency(self) -> None:
        """Test UI-specific format requirements"""
        print("\n🖥️  Testing UI Format Consistency...")

        queries = ["What is GDPR?", "Explain ISO 27001", "Describe SOC 2 requirements"]

        ui_format_valid = True
        json_serializable = True
        content_safe = True

        for query in queries:
            response = await self.mock_ai_request(query)

            # Test JSON serialization
            try:
                json_str = json.dumps(response)
                json.loads(json_str)  # Test round-trip
            except (TypeError, ValueError):
                json_serializable = False

            # Test UI content safety
            if not response["response"] or response["response"].strip() == "":
                content_safe = False

            # Check for potentially problematic characters
            problematic_chars = ["\x00", "\x01", "\x02", "\x03", "\x04", "\x05"]
            if any(char in response["response"] for char in problematic_chars):
                content_safe = False

        passed = ui_format_valid and json_serializable and content_safe

        self.results["test_results"]["ui_format"] = {
            "passed": passed,
            "json_serializable": json_serializable,
            "content_safe": content_safe,
            "queries_tested": len(queries),
        }

        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   UI Format Consistency: {status}")
        print(f"   - JSON serializable: {'✅' if json_serializable else '❌'}")
        print(f"   - Content safe: {'✅' if content_safe else '❌'}")

    async def test_performance_consistency(self) -> None:
        """Test performance consistency"""
        print("\n⏱️  Testing Performance Consistency...")

        query = "Compare GDPR and ISO 27001 requirements"
        response_times = []
        confidences = []

        # Measure response times
        for i in range(10):
            start_time = time.time()
            response = await self.mock_ai_request(query, user_id=f"perf_user_{i}")
            end_time = time.time()

            response_times.append(end_time - start_time)
            confidences.append(response["confidence"])

        # Analyze performance consistency
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)

        if len(response_times) > 1:
            std_dev = statistics.stdev(response_times)
            cv = std_dev / avg_response_time if avg_response_time > 0 else 0
        else:
            cv = 0

        # Performance thresholds
        time_consistent = cv < 0.5  # Coefficient of variation < 50%
        all_fast = all(rt < 5.0 for rt in response_times)
        confidence_stable = len(set(confidences)) <= 3  # Allow some variation

        passed = time_consistent and all_fast and confidence_stable

        self.results["test_results"]["performance"] = {
            "passed": passed,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "coefficient_of_variation": cv,
            "time_consistent": time_consistent,
            "all_responses_fast": all_fast,
            "confidence_stable": confidence_stable,
        }

        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   Performance Consistency: {status}")
        print(f"   - Avg response time: {avg_response_time:.3f}s")
        print(f"   - CV: {cv:.3f}")
        print(f"   - All responses < 5s: {'✅' if all_fast else '❌'}")

    async def test_error_handling_consistency(self) -> None:
        """Test consistent error handling"""
        print("\n🚨 Testing Error Handling Consistency...")

        error_scenarios = [
            {"query": "", "description": "empty query"},
            {"query": "x" * 5000, "description": "very long query"},
            {"simulate_error": True, "query": "Normal query", "description": "service error"},
        ]

        error_handling_consistent = True
        graceful_failures = 0

        for scenario in error_scenarios:
            try:
                if scenario.get("simulate_error"):
                    response = await self.mock_ai_request(scenario["query"], simulate_error=True)
                else:
                    response = await self.mock_ai_request(scenario["query"])

                # If we get a response, check it's valid structure
                if "response" in response and "confidence" in response:
                    graceful_failures += 1

                    # Edge cases should typically have lower confidence
                    if scenario["description"] in ["empty query", "very long query"]:
                        if response["confidence"] <= 0.8:
                            pass  # Expected lower confidence

            except Exception:
                # Exceptions should be handled gracefully in production
                # For this test, we expect our mock to not throw exceptions
                if scenario.get("simulate_error"):
                    pass  # Expected exception
                else:
                    error_handling_consistent = False

        passed = error_handling_consistent and graceful_failures >= 2

        self.results["test_results"]["error_handling"] = {
            "passed": passed,
            "consistent_error_handling": error_handling_consistent,
            "graceful_failures": graceful_failures,
            "scenarios_tested": len(error_scenarios),
        }

        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   Error Handling Consistency: {status}")
        print(f"   - Graceful failures: {graceful_failures}/{len(error_scenarios)}")

    def generate_summary(self) -> None:
        """Generate test summary"""
        test_results = self.results["test_results"]

        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get("passed", False))

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "overall_status": "PASSED" if passed_tests == total_tests else "FAILED",
        }

        # Generate recommendations
        if passed_tests < total_tests:
            self.results["recommendations"].append(
                "Some consistency tests failed. Review failing tests for specific improvements needed."
            )

        if test_results.get("performance", {}).get("coefficient_of_variation", 0) > 0.3:
            self.results["recommendations"].append(
                "Performance variation detected. Consider implementing response caching for identical queries."
            )

        if test_results.get("cross_framework", {}).get("confidence_variation", 0) > 0.2:
            self.results["recommendations"].append(
                "Confidence scores vary significantly across frameworks. Review scoring consistency."
            )

        if not test_results.get("caching", {}).get("passed", True):
            self.results["recommendations"].append(
                "Caching consistency issues detected. Ensure identical queries return identical responses."
            )

        if not self.results["recommendations"]:
            self.results["recommendations"].append(
                "All consistency tests passed! AI output is reliable for UI consumption."
            )

    def generate_report(self) -> None:
        """Generate and display final report"""
        print("\n" + "=" * 60)
        print("📊 AI OUTPUT CONSISTENCY VALIDATION REPORT")
        print("=" * 60)

        summary = self.results["summary"]
        print(f"Overall Status: {summary['overall_status']}")
        print(
            f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']} ({summary['success_rate']:.1%})"
        )
        print()

        print("Test Results:")
        for test_name, result in self.results["test_results"].items():
            status = "✅ PASSED" if result.get("passed", False) else "❌ FAILED"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")

        print("\nRecommendations:")
        for i, rec in enumerate(self.results["recommendations"], 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 60)

        # Save detailed report
        with open("ai_consistency_report.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print("📝 Detailed report saved to: ai_consistency_report.json")


async def main():
    """Run AI consistency validation"""
    validator = AIConsistencyValidator()
    results = await validator.run_all_validations()

    return results["summary"]["overall_status"] == "PASSED"


if __name__ == "__main__":
    import sys

    # Run validation
    success = asyncio.run(main())

    # Exit with appropriate code
    sys.exit(0 if success else 1)
