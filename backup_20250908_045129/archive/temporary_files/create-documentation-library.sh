#!/bin/bash

# Create Documentation Library for ruleIQ Production Readiness
# This script copies all key documentation into an organized structure

set -e

echo "📚 Creating Documentation Library..."

# Create directory structure
mkdir -p documentation-library/{01-core,02-technical,03-testing,04-context,05-historical,06-final-reports}

# Copy Core Documentation
echo "📋 Copying Core Documentation..."
cp docs/INFRASTRUCTURE_SETUP.md documentation-library/01-core/01-infrastructure-setup.md
cp docs/SECURITY_PERFORMANCE_SETUP.md documentation-library/01-core/02-security-performance-setup.md
cp docs/TESTING_GUIDE.md documentation-library/01-core/03-testing-guide.md

# Copy Technical Documentation
echo "🏛️ Copying Technical Documentation..."
cp docs/context/ARCHITECTURE_CONTEXT.md documentation-library/02-technical/01-architecture-context.md
cp docs/context/DATABASE_CONTEXT.md documentation-library/02-technical/02-database-context.md
cp docs/context/FRONTEND_CONTEXT.md documentation-library/02-technical/03-frontend-context.md
cp docs/context/API_CONTEXT.md documentation-library/02-technical/04-api-context.md
cp docs/context/AI_SERVICES_CONTEXT.md documentation-library/02-technical/05-ai-services-context.md
cp frontend/DESIGN_TOKENS.md documentation-library/02-technical/06-design-tokens.md

# Copy Testing Documentation
echo "🧪 Copying Testing Documentation..."
cp frontend/tests/README.md documentation-library/03-testing/01-testing-overview.md
cp frontend/tests/e2e/README.md documentation-library/03-testing/02-e2e-testing.md
cp frontend/tests/e2e/E2E_TEST_SETUP_GUIDE.md documentation-library/03-testing/03-e2e-setup-guide.md
cp frontend/tests/e2e/E2E_TEST_CONFIGURATION.md documentation-library/03-testing/04-e2e-configuration.md
cp frontend/tests/e2e/E2E_TEST_FIX_SUMMARY.md documentation-library/03-testing/05-e2e-fix-summary.md
cp frontend/tests/visual/VISUAL_TESTING_GUIDE.md documentation-library/03-testing/06-visual-testing-guide.md
cp frontend/tests/accessibility/MANUAL_TESTING_GUIDE.md documentation-library/03-testing/07-accessibility-guide.md
cp frontend/tests/MEMORY_LEAK_DETECTION_GUIDE.md documentation-library/03-testing/08-memory-leak-guide.md
cp frontend/TEST_STATUS_SUMMARY.md documentation-library/03-testing/09-test-status-summary.md
cp frontend/QUALITY_ASSURANCE_GUIDE.md documentation-library/03-testing/10-quality-assurance.md

# Copy Context & Analysis
echo "📊 Copying Context & Analysis..."
cp docs/context/PROJECT_STATUS.md documentation-library/04-context/01-project-status.md
cp docs/context/ANALYSIS_REPORT.md documentation-library/04-context/02-analysis-report.md
cp docs/context/CHANGE_LOG.md documentation-library/04-context/03-change-log.md
cp docs/context/CONTEXT_SPECIFICATION.md documentation-library/04-context/04-context-specification.md
cp docs/context/SERENA_INTEGRATION_CONTEXT.md documentation-library/04-context/05-serena-integration.md

# Copy Historical Documentation
echo "📚 Copying Historical Documentation..."
cp historical/documentation/AI_CHECKLIST.md documentation-library/05-historical/01-ai-checklist.md
cp historical/documentation/AI_CONTEXT.md documentation-library/05-historical/02-ai-context.md
cp historical/documentation/API_INTEGRATION_ARCHITECTURE.md documentation-library/05-historical/03-api-integration-architecture.md
cp historical/documentation/AUDIT_IMPLEMENTATION_SUMMARY.md documentation-library/05-historical/04-audit-implementation-summary.md
cp historical/documentation/CRITICAL_FIXES_CHECKLIST.md documentation-library/05-historical/05-critical-fixes-checklist.md
cp historical/documentation/CRITICAL_FIXES_SETUP.md documentation-library/05-historical/06-critical-fixes-setup.md
cp historical/documentation/CRITICAL_OPTIMIZATIONS_IMPLEMENTED.md documentation-library/05-historical/07-critical-optimizations.md
cp historical/documentation/DATABASE_FIXES_SUMMARY.md documentation-library/05-historical/08-database-fixes-summary.md
cp historical/documentation/FOUNDATION_IMPLEMENTATION_SUMMARY.md documentation-library/05-historical/09-foundation-implementation.md
cp historical/documentation/HANDOVER.md documentation-library/05-historical/10-handover.md
cp historical/documentation/MCP_INTEGRATION_DESIGN.md documentation-library/05-historical/11-mcp-integration-design.md
cp historical/documentation/PHASE5_COMPLETION_REPORT.md documentation-library/05-historical/12-phase5-completion-report.md
cp historical/documentation/SERENA_MCP_INTEGRATION.md documentation-library/05-historical/13-serena-mcp-integration.md
cp historical/documentation/TEST_FIXES_HANDOVER.md documentation-library/05-historical/14-test-fixes-handover.md
cp historical/documentation/TEST_GROUPS_SUMMARY.md documentation-library/05-historical/15-test-groups-summary.md
cp historical/documentation/TEST_HANDOVER.md documentation-library/05-historical/16-test-handover.md
cp historical/documentation/TEST_USER_CREDENTIALS.md documentation-library/05-historical/17-test-user-credentials.md
cp historical/documentation/The-Final-39-Test-Failures.md documentation-library/05-historical/18-final-39-test-failures.md

# Copy Final Reports & Summaries
echo "📋 Copying Final Reports..."
cp frontend/WEEK_1_IMPLEMENTATION_SUMMARY.md documentation-library/06-final-reports/01-week1-implementation-summary.md
cp frontend/TEST_FIX_SUMMARY.md documentation-library/06-final-reports/02-test-fix-summary.md
cp frontend/TEST_FIX_COMPLETE_SUMMARY.md documentation-library/06-final-reports/03-test-fix-complete-summary.md
cp frontend/TEST_STATUS_FINAL.md documentation-library/06-final-reports/04-test-status-final.md
cp frontend/PRODUCTION_QUICK_REFERENCE.md documentation-library/06-final-reports/05-production-quick-reference.md
cp frontend/PRODUCTION_READINESS_TASKS.md documentation-library/06-final-reports/06-production-readiness-tasks.md
cp frontend/PRODUCTION_BUILD_PROMPTS.md documentation-library/06-final-reports/07-production-build-prompts.md
cp frontend/accessibility-audit-report.md documentation-library/06-final-reports/08-accessibility-audit-report.md
cp frontend/AI_TEST_FIX_SUMMARY.md documentation-library/06-final-reports/09-ai-test-fix-summary.md
cp ALL_DOCUMENTATION.md documentation-library/06-final-reports/10-complete-documentation-index.md

# Copy API documentation
cp docs/api/ai-endpoints.md documentation-library/02-technical/07-ai-endpoints.md

# Copy configuration files
cp docs/context/monitor_config.json documentation-library/04-context/06-monitor-config.json
cp docs/context/README.md documentation-library/04-context/07-context-readme.md

echo "✅ Documentation Library Created Successfully!"
echo ""
echo "📖 Library Structure:"
echo "├── 01-core/                    # Core infrastructure & setup docs"
echo "├── 02-technical/               # Architecture & technical specifications"
echo "├── 03-testing/                 # Testing guides & procedures"
echo "├── 04-context/                 # Project context & analysis"
echo "├── 05-historical/              # Legacy & historical documentation"
echo "└── 06-final-reports/           # Final reports & summaries"
echo ""
echo "📊 Total Files: $(find documentation-library -name "*.md" | wc -l) documents"
echo "📍 Location: $(pwd)/documentation-library/"