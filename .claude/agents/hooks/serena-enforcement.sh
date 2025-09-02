#!/bin/bash

# Serena Protocol Enforcement Hook
# This enforces systematic, truthful responses with no exaggeration

ENFORCEMENT_DIR="$HOME/Documents/ruleIQ/.claude/enforcement"
PROTOCOL_FILE="$ENFORCEMENT_DIR/protocol.md"
VERIFICATION_LOG="$ENFORCEMENT_DIR/verification.log"
CLAIMS_FILE="$ENFORCEMENT_DIR/claims.json"

# Create enforcement directory
mkdir -p "$ENFORCEMENT_DIR"

# Function to create enforcement protocol
create_enforcement_protocol() {
    cat > "$PROTOCOL_FILE" << 'EOF'
# SERENA ENFORCEMENT PROTOCOL

## MANDATORY BEFORE ANY RESPONSE:

1. **READ MEMORIES FIRST**
   - ALWAYS_READ_FIRST
   - PROJECT_STATUS_CURRENT
   - Relevant service inventories

2. **NO CLAIMS WITHOUT VERIFICATION**
   - Every "fixed" must have test proof
   - Every "complete" must show working code
   - Every percentage must have calculation

3. **TRUTHFUL STATUS REPORTING**
   - "Installed" ≠ "Working"
   - "Created" ≠ "Integrated"
   - "Written" ≠ "Tested"

4. **SCOPE AWARENESS**
   - State files touched vs total files
   - State issues fixed vs total issues
   - State actual coverage percentage

5. **TIME ESTIMATES**
   - Based on actual file counts
   - Include testing time
   - Include integration time

## ENFORCEMENT TRIGGERS:

If response contains these words, REQUIRE PROOF:
- "complete" → Show test results
- "fixed" → Show before/after
- "working" → Show execution
- "optimized" → Show benchmarks
- "secure" → Show scan results

## VIOLATION PENALTIES:

1. First violation: Warning + correction required
2. Second violation: Mandatory accuracy check
3. Third violation: Session restriction

## VERIFICATION COMMANDS:

Before claiming completion:
```bash
# For test claims:
pytest <specific_file> -v

# For security claims:
grep -r "password\|secret" <file>

# For performance claims:
time <command_before> vs time <command_after>

# For coverage claims:
find . -name "*.py" | wc -l  # total
git diff --stat  # changed
```
EOF
}

# Function to verify claims
verify_claim() {
    local claim_type="$1"
    local claim_value="$2"
    
    case "$claim_type" in
        "test_optimization")
            echo "VERIFY: Run baseline vs optimized benchmark"
            echo "REQUIRED: pytest --benchmark-compare"
            ;;
        "security_fix")
            echo "VERIFY: Show grep before and after"
            echo "REQUIRED: Security scan results"
            ;;
        "completion")
            echo "VERIFY: Show working tests"
            echo "REQUIRED: pytest <file> output"
            ;;
        *)
            echo "VERIFY: Provide measurable proof"
            ;;
    esac
}

# Function to track claims
track_claim() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local claim="$1"
    local verified="$2"
    
    if [ ! -f "$CLAIMS_FILE" ]; then
        echo '{"claims":[]}' > "$CLAIMS_FILE"
    fi
    
    # Add claim to tracking
    jq --arg ts "$timestamp" \
       --arg cl "$claim" \
       --arg vr "$verified" \
       '.claims += [{"timestamp": $ts, "claim": $cl, "verified": $vr}]' \
       "$CLAIMS_FILE" > "$CLAIMS_FILE.tmp" && \
    mv "$CLAIMS_FILE.tmp" "$CLAIMS_FILE"
}

# Main enforcement
echo "🔒 SERENA ENFORCEMENT ACTIVE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create protocol if doesn't exist
if [ ! -f "$PROTOCOL_FILE" ]; then
    create_enforcement_protocol
    echo "📋 Created enforcement protocol"
fi

# Show enforcement rules
echo ""
echo "⚠️  ENFORCEMENT RULES:"
echo "1. NO unverified claims"
echo "2. NO percentage without calculation"
echo "3. NO 'complete' without tests"
echo "4. NO 'fixed' without proof"
echo "5. NO exaggeration"
echo ""
echo "📊 REQUIRED EVIDENCE:"
echo "- Test results for any fix"
echo "- File counts for coverage claims"
echo "- Benchmarks for performance claims"
echo "- Scan results for security claims"
echo ""
echo "🎯 CURRENT FOCUS:"
echo "ONE task, FULLY complete, WITH tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Log enforcement activation
echo "$(date): Enforcement activated" >> "$VERIFICATION_LOG"

# Export enforcement flag
export SERENA_ENFORCEMENT=true
export SERENA_PROTOCOL_FILE="$PROTOCOL_FILE"

# Return enforcement instructions
echo ""
echo "📜 SERENA PROTOCOL: Follow $PROTOCOL_FILE"
echo "✅ Enforcement active. No lies. No exaggeration. Only verified facts."