# AI Output Consistency Testing Suite

This directory contains comprehensive tests to ensure the ruleIQ AI system produces consistent, reliable output for UI consumption.

## 🎯 Purpose

The AI consistency testing suite validates that:

1. **Response Structure Consistency** - All AI responses maintain consistent field structure and data types
2. **Cross-Framework Consistency** - Responses are consistent across different compliance frameworks (GDPR, ISO 27001, SOC 2)
3. **Caching Consistency** - Identical queries return identical responses when cached
4. **Concurrent Request Consistency** - System handles multiple simultaneous requests reliably
5. **UI Format Consistency** - Responses are properly formatted for frontend consumption
6. **Performance Consistency** - Response times remain consistent within acceptable ranges
7. **Error Handling Consistency** - Edge cases and errors are handled gracefully and consistently

## 📁 Test Files

### Core Test Files

- **`test_ai_consistency_simple.py`** - Main consistency test suite with mock AI assistant
  - `TestAIOutputConsistency` - Core AI output validation tests
  - `TestUIFormatConsistency` - UI-specific format validation tests

- **`test_ui_integration_consistency.py`** - UI integration specific tests
  - `TestUIResponseFormatConsistency` - UI response format validation
  - `TestUIComponentIntegration` - Chat and dashboard widget integration tests
  - `TestUIStateConsistency` - Application state management tests

- **`conftest.py`** - Shared test configuration and fixtures

### Validation Scripts

- **`run_ai_consistency_validation.py`** - Comprehensive validation runner
  - Runs all consistency validation tests
  - Generates detailed JSON report
  - Provides pass/fail status and recommendations

- **`scripts/test-ai-consistency.sh`** - Production test runner script
  - Multiple test modes: full, quick, validation-only, production
  - Automated report generation
  - CI/CD pipeline integration ready

## 🚀 Running Tests

### Quick Start

```bash
# Run all consistency tests
source .venv/bin/activate
python -m pytest tests/consistency/ -v

# Run comprehensive validation
python run_ai_consistency_validation.py

# Use the test script (recommended)
./scripts/test-ai-consistency.sh
```

### Test Modes

```bash
# Full test suite (default)
./scripts/test-ai-consistency.sh full

# Quick essential tests only
./scripts/test-ai-consistency.sh quick

# Comprehensive validation only
./scripts/test-ai-consistency.sh validation-only

# Production readiness tests
./scripts/test-ai-consistency.sh production
```

### Environment Variables

```bash
# Disable report generation
GENERATE_REPORT=false ./scripts/test-ai-consistency.sh

# Custom test configuration
TEST_TIMEOUT=30 ./scripts/test-ai-consistency.sh
```

## 📊 Test Results and Reporting

### Automated Reports

Tests generate detailed reports including:

- **JSON Report** (`ai_consistency_report.json`) - Machine-readable test results
- **Markdown Report** (`ai_consistency_test_report_YYYYMMDD_HHMMSS.md`) - Human-readable summary
- **Console Output** - Real-time test progress and results

### Key Metrics Tracked

1. **Response Structure Validity** - All required fields present with correct types
2. **Confidence Score Consistency** - Scores remain within valid ranges (0.5-1.0)
3. **Compliance Score Consistency** - Scores remain within valid ranges (0-100)
4. **Response Time Consistency** - Low coefficient of variation in response times
5. **Cache Hit Rate** - Identical queries return identical cached responses
6. **Concurrent Request Success Rate** - All concurrent requests complete successfully
7. **JSON Serialization Success Rate** - All responses can be serialized/deserialized
8. **Error Handling Success Rate** - Edge cases handled gracefully

## 🧪 Test Scenarios

### Response Structure Tests
- Validates presence of required fields: `response`, `confidence`, `sources`, `compliance_score`, `metadata`, `timestamp`
- Checks correct data types for all fields
- Ensures consistent structure across different query types

### Cross-Framework Tests
- Tests GDPR, ISO 27001, and SOC 2 framework responses
- Validates consistent response format across frameworks
- Checks framework-specific content accuracy

### Caching Tests
- Runs identical queries multiple times
- Validates response consistency (should be identical when cached)
- Measures cache hit rate and performance

### Concurrent Load Tests
- Executes multiple simultaneous AI requests
- Validates all requests complete successfully
- Checks response consistency under concurrent load
- Measures performance degradation

### UI Format Tests
- Validates JSON serialization/deserialization
- Checks for UI-breaking characters
- Ensures content safety for frontend display
- Validates required UI metadata presence

### Performance Tests
- Measures response time consistency (coefficient of variation)
- Validates all responses complete within acceptable timeframes (<5 seconds)
- Checks memory usage patterns
- Monitors for performance regression

### Error Handling Tests
- Tests empty query handling
- Tests oversized query handling
- Tests off-topic query handling
- Tests service error recovery
- Validates graceful failure modes

## 🔧 Configuration

### Test Thresholds

```python
PERFORMANCE_THRESHOLDS = {
    "max_response_time": 5.0,  # seconds
    "min_confidence": 0.7,
    "min_compliance_score": 70,
    "max_memory_growth": 50 * 1024 * 1024,  # 50MB
    "max_response_time_variation": 0.5  # coefficient of variation
}
```

### Expected Response Structure

```python
EXPECTED_RESPONSE_STRUCTURE = {
    "response": str,
    "confidence": float,
    "sources": list,
    "compliance_score": (int, float),
    "metadata": dict,
    "timestamp": str
}
```

### Test Frameworks

Tests validate consistency across these compliance frameworks:
- `gdpr` - General Data Protection Regulation
- `iso27001` - ISO 27001 Information Security Management
- `soc2` - SOC 2 Service Organization Control
- `hipaa` - Health Insurance Portability and Accountability Act
- `ccpa` - California Consumer Privacy Act

## 📈 CI/CD Integration

### GitHub Actions Integration

```yaml
- name: Run AI Consistency Tests
  run: |
    source .venv/bin/activate
    ./scripts/test-ai-consistency.sh production
    
- name: Upload Test Reports
  uses: actions/upload-artifact@v3
  with:
    name: ai-consistency-reports
    path: ai_consistency_*.json
```

### Pre-deployment Validation

```bash
# Required before any AI system deployment
./scripts/test-ai-consistency.sh production
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated: `source .venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

2. **Test Failures**
   - Check console output for specific failure details
   - Review generated JSON report for detailed error information
   - Verify AI service mock configuration

3. **Performance Issues**
   - Monitor system resources during test execution
   - Check for memory leaks in long-running tests
   - Validate network connectivity for integration tests

### Debug Mode

```bash
# Enable verbose pytest output
python -m pytest tests/consistency/ -v -s --tb=long

# Run with detailed logging
PYTHONPATH=. python run_ai_consistency_validation.py --debug
```

## 📚 Reference

### Key Test Classes

- `TestAIOutputConsistency` - Core AI response validation
- `TestAIPerformanceConsistency` - Performance and reliability testing
- `TestUIFormatConsistency` - UI integration validation
- `TestUIComponentIntegration` - Component-specific testing
- `AIConsistencyValidator` - Comprehensive validation orchestrator

### Mock AI Assistant

The test suite uses a `MockAIAssistant` class that simulates real AI behavior without requiring actual API calls:

```python
assistant = MockAIAssistant()
response = await assistant.process_message(
    message="What are GDPR requirements?",
    framework="gdpr",
    user_id="test_user"
)
```

## 🔄 Continuous Improvement

### Regular Maintenance

1. **Weekly**: Review test results and performance metrics
2. **Monthly**: Update test scenarios based on production AI behavior
3. **Quarterly**: Comprehensive review of test coverage and thresholds
4. **As needed**: Add new test scenarios for new AI features or frameworks

### Monitoring Integration

Consider integrating these tests with production monitoring:

1. **Response Time Monitoring** - Alert on response time degradation
2. **Confidence Score Tracking** - Monitor confidence score distributions
3. **Error Rate Monitoring** - Track error handling effectiveness
4. **Cache Performance** - Monitor cache hit rates and performance

---

This comprehensive testing suite ensures the ruleIQ AI system delivers consistent, reliable output that integrates seamlessly with the frontend UI across all supported compliance frameworks.