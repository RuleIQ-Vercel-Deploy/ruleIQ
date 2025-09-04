#!/bin/bash

echo "🔐 RuleIQ Security Audit - Starting Comprehensive Scan"
echo "=================================================="
echo ""

# Navigate to project directory
cd /home/omar/Documents/ruleIQ

# Run the comprehensive security audit
echo "📊 Running vulnerability scanner..."
python3 security_vulnerability_audit.py

echo ""
echo "✅ Security audit complete. Review the reports:"
echo "   - SECURITY_AUDIT_REPORT.md (summary)"
echo "   - security_audit_report.json (detailed)"