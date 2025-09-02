"""
Self-Critic Command Interface for Agentic RAG System
Provides CLI-style commands for running fact-checks and self-criticism
"""

import sys
import json
import asyncio
import argparse
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.agentic_rag import AgenticRAGSystem
from services.rag_fact_checker import RAGFactChecker, QualityAssessment


class RAGSelfCriticCommands:
    """
    Command-line interface for RAG fact-checking and self-criticism

    Available Commands:
    - fact-check: Run comprehensive fact-checking on a RAG response
    - quick-check: Run fast fact-checking for real-time usage
    - critique: Run self-criticism analysis
    - assess: Run full quality assessment
    - benchmark: Run benchmark tests on sample queries
    """

    def __init__(self) -> None:
        self.rag_system = None
        self.fact_checker = None

    async def initialize(self) -> Optional[bool]:
        """Initialize RAG system and fact checker"""
        try:
            print("🔧 Initializing RAG Self-Critic System...")
            self.rag_system = AgenticRAGSystem()
            self.fact_checker = RAGFactChecker()
            print("✅ System initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize system: {e}")
            return False

    async def fact_check_command(
        self, query: str, max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Run fact-checking on a RAG query response

        Args:
            query: The question to ask the RAG system
            max_results: Maximum number of sources to use
        """
        print(f"🔍 Running fact-check for query: '{query}'")
        print("=" * 60)

        try:
            # Get RAG response
            print("📝 Generating RAG response...")
            rag_response = await self.rag_system.query_documentation(
                query=query, max_results=max_results
            )

            print(f"✅ RAG response generated ({len(rag_response.sources)} sources)")
            print(f"📊 Initial confidence: {rag_response.confidence}")

            # Run fact-checking
            print("\n🔬 Running comprehensive fact-check...")
            assessment = await self.fact_checker.comprehensive_fact_check(
                response_text=rag_response.answer,
                sources=rag_response.sources,
                original_query=query,
            )

            # Display results
            self._display_fact_check_results(assessment, rag_response)

            return {
                "query": query,
                "rag_response": rag_response.dict(),
                "fact_check_assessment": assessment.dict(),
                "approved": assessment.approved_for_use,
            }

        except Exception as e:
            print(f"❌ Fact-check failed: {e}")
            return {"error": str(e)}

    async def quick_check_command(self, query: str) -> Dict[str, Any]:
        """
        Run quick fact-checking for real-time usage

        Args:
            query: The question to ask the RAG system
        """
        print(f"⚡ Running quick fact-check for: '{query}'")
        print("=" * 50)

        try:
            # Get RAG response
            rag_response = await self.rag_system.query_documentation(
                query=query, max_results=3
            )

            # Run quick fact-check
            is_reliable = await self.fact_checker.quick_fact_check(
                response_text=rag_response.answer, sources=rag_response.sources
            )

            # Display results
            status = "✅ APPROVED" if is_reliable else "⚠️ SUSPICIOUS"
            print(f"\n{status}")
            print(f"📝 Response: {rag_response.answer[:200]}...")
            print(f"📊 RAG Confidence: {rag_response.confidence}")
            print(f"🔍 Fact-Check Result: {'PASS' if is_reliable else 'REVIEW NEEDED'}")

            return {
                "query": query,
                "response": rag_response.answer,
                "is_reliable": is_reliable,
                "rag_confidence": rag_response.confidence,
            }

        except Exception as e:
            print(f"❌ Quick check failed: {e}")
            return {"error": str(e)}

    async def critique_command(self, query: str) -> Dict[str, Any]:
        """
        Run self-criticism analysis on a RAG response

        Args:
            query: The question to ask the RAG system
        """
        print(f"🎯 Running self-critique for: '{query}'")
        print("=" * 50)

        try:
            # Get RAG response
            rag_response = await self.rag_system.query_documentation(query=query)

            # Run self-criticism (part of comprehensive fact-check)
            assessment = await self.fact_checker.comprehensive_fact_check(
                response_text=rag_response.answer,
                sources=rag_response.sources,
                original_query=query,
            )

            # Display critique results
            self._display_critique_results(assessment.self_critiques)

            return {
                "query": query,
                "critiques": [
                    critique.dict() for critique in assessment.self_critiques
                ],
                "overall_score": assessment.overall_score,
            }

        except Exception as e:
            print(f"❌ Critique failed: {e}")
            return {"error": str(e)}

    async def assess_command(self, query: str) -> Dict[str, Any]:
        """
        Run full quality assessment (fact-check + critique + scoring)

        Args:
            query: The question to ask the RAG system
        """
        print(f"📊 Running full quality assessment for: '{query}'")
        print("=" * 60)

        try:
            # Get RAG response
            rag_response = await self.rag_system.query_documentation(query=query)

            # Run comprehensive assessment
            assessment = await self.fact_checker.comprehensive_fact_check(
                response_text=rag_response.answer,
                sources=rag_response.sources,
                original_query=query,
            )

            # Display comprehensive results
            self._display_comprehensive_assessment(assessment, rag_response)

            return {
                "query": query,
                "rag_response": rag_response.dict(),
                "assessment": assessment.dict(),
            }

        except Exception as e:
            print(f"❌ Assessment failed: {e}")
            return {"error": str(e)}

    async def benchmark_command(self, num_queries: int = 5) -> Dict[str, Any]:
        """
        Run benchmark tests on sample queries

        Args:
            num_queries: Number of test queries to run
        """
        print(f"🏃 Running benchmark with {num_queries} test queries")
        print("=" * 50)

        # Sample test queries
        test_queries = [
            "How do I create a StateGraph in LangGraph?",
            "What is Pydantic AI and how does it work?",
            "How do I implement state persistence in LangGraph?",
            "What are the main components of Pydantic AI?",
            "How do I handle errors in LangGraph workflows?",
            "Can I use async functions with Pydantic AI?",
            "How do I implement conditional logic in LangGraph?",
            "What embedding models does Pydantic AI support?",
        ]

        results = []
        total_time = 0

        for i, query in enumerate(test_queries[:num_queries]):
            print(f"\n📝 Test {i+1}/{num_queries}: {query[:50]}...")

            start_time = datetime.now()

            try:
                # Run assessment
                result = await self.assess_command(query)
                success = "assessment" in result

                # Calculate time
                elapsed = (datetime.now() - start_time).total_seconds()
                total_time += elapsed

                results.append(
                    {
                        "query": query,
                        "success": success,
                        "time_seconds": elapsed,
                        "overall_score": result.get("assessment", {}).get(
                            "overall_score", 0.0
                        ),
                        "approved": result.get("assessment", {}).get(
                            "approved_for_use", False
                        ),
                    }
                )

                status = "✅" if success else "❌"
                print(f"{status} Completed in {elapsed:.2f}s")

            except Exception as e:
                print(f"❌ Failed: {e}")
                results.append({"query": query, "success": False, "error": str(e)})

        # Summary
        successful = sum(1 for r in results if r.get("success", False))
        avg_time = total_time / len(results) if results else 0
        avg_score = (
            sum(r.get("overall_score", 0) for r in results) / len(results)
            if results
            else 0
        )
        approval_rate = (
            sum(1 for r in results if r.get("approved", False)) / len(results)
            if results
            else 0
        )

        print("\n📊 Benchmark Summary:")
        print(
            f"   Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)"
        )
        print(f"   Average Time: {avg_time:.2f}s")
        print(f"   Average Score: {avg_score:.3f}")
        print(f"   Approval Rate: {approval_rate*100:.1f}%")

        return {
            "benchmark_results": results,
            "summary": {
                "success_rate": successful / len(results),
                "average_time": avg_time,
                "average_score": avg_score,
                "approval_rate": approval_rate,
            },
        }

    def _display_fact_check_results(
        self, assessment: QualityAssessment, rag_response
    ) -> None:
        """Display fact-checking results"""
        print("\n📋 Fact-Check Results:")
        print(f"   Overall Score: {assessment.overall_score:.3f}")
        print(f"   Reliability: {assessment.response_reliability:.3f}")
        print(f"   Source Quality: {assessment.source_quality_score:.3f}")
        print(
            f"   Status: {'✅ APPROVED' if assessment.approved_for_use else '⚠️ NEEDS REVIEW'}"
        )

        print("\n🔍 Factual Claims Analysis:")
        for i, fact_check in enumerate(assessment.fact_check_results):
            status = "✅" if fact_check.is_factual else "❌"
            confidence_emoji = {
                "high": "🟢",
                "medium": "🟡",
                "low": "🟠",
                "uncertain": "🔴",
            }.get(fact_check.confidence.value, "⚪")

            print(f"   {i+1}. {status} {confidence_emoji} {fact_check.claim[:80]}...")
            if fact_check.contradictions:
                print(f"      ⚠️ Contradictions: {len(fact_check.contradictions)}")

        if assessment.flagged_issues:
            print("\n🚨 Flagged Issues:")
            for issue in assessment.flagged_issues:
                print(f"   • {issue}")

        if assessment.recommendations:
            print("\n💡 Recommendations:")
            for rec in assessment.recommendations:
                print(f"   • {rec}")

    def _display_critique_results(self, critiques) -> None:
        """Display self-critique results"""
        print("\n🎯 Self-Critique Results:")

        for critique in critiques:
            score_emoji = (
                "🟢"
                if critique.score >= 0.8
                else "🟡" if critique.score >= 0.6 else "🔴"
            )
            print(f"   {critique.aspect.title()}: {score_emoji} {critique.score:.3f}")

            if critique.issues:
                print(f"      Issues: {critique.issues[0]}")
            if critique.suggestions:
                print(f"      Suggestion: {critique.suggestions[0]}")

    def _display_comprehensive_assessment(
        self, assessment: QualityAssessment, rag_response
    ) -> None:
        """Display comprehensive assessment results"""
        self._display_fact_check_results(assessment, rag_response)
        self._display_critique_results(assessment.self_critiques)

        print("\n📊 Final Assessment:")
        print(f"   Overall Quality: {assessment.overall_score:.3f}/1.0")
        print(f"   Response Reliability: {assessment.response_reliability:.3f}/1.0")
        print(f"   Processing Time: {rag_response.processing_time:.2f}s")
        print(
            f"   Final Status: {'✅ APPROVED FOR USE' if assessment.approved_for_use else '⚠️ REQUIRES REVIEW'}"
        )


async def main() -> None:
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="RAG Self-Critic Commands")
    parser.add_argument(
        "command",
        choices=["fact-check", "quick-check", "critique", "assess", "benchmark"],
        help="Command to run",
    )
    parser.add_argument(
        "--query", type=str, help="Query to test (required for most commands)"
    )
    parser.add_argument(
        "--max-results", type=int, default=5, help="Maximum number of sources"
    )
    parser.add_argument(
        "--num-queries", type=int, default=5, help="Number of queries for benchmark"
    )
    parser.add_argument("--output", type=str, help="Output file for results (JSON)")

    args = parser.parse_args()

    # Initialize system
    critic = RAGSelfCriticCommands()
    if not await critic.initialize():
        sys.exit(1)

    # Run command
    try:
        if args.command == "fact-check":
            if not args.query:
                print("❌ --query is required for fact-check command")
                sys.exit(1)
            result = await critic.fact_check_command(args.query, args.max_results)

        elif args.command == "quick-check":
            if not args.query:
                print("❌ --query is required for quick-check command")
                sys.exit(1)
            result = await critic.quick_check_command(args.query)

        elif args.command == "critique":
            if not args.query:
                print("❌ --query is required for critique command")
                sys.exit(1)
            result = await critic.critique_command(args.query)

        elif args.command == "assess":
            if not args.query:
                print("❌ --query is required for assess command")
                sys.exit(1)
            result = await critic.assess_command(args.query)

        elif args.command == "benchmark":
            result = await critic.benchmark_command(args.num_queries)

        # Save output if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n💾 Results saved to {args.output}")

    except KeyboardInterrupt:
        print("\n\n⏹️ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Command failed: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if critic.rag_system:
            critic.rag_system.close()


if __name__ == "__main__":
    asyncio.run(main())
