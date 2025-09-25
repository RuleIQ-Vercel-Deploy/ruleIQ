# PR Management System

A comprehensive system for managing and cleaning up pull requests in the ruleIQ repository.

## Overview

This PR management system provides automated and semi-automated tools to handle 20+ open pull requests efficiently. It categorizes, analyzes, and processes PRs based on their type, risk level, and readiness for merge.

## Quick Start

### Prerequisites

```bash
# Install required Python packages
pip install requests pyyaml tabulate

# Ensure GitHub CLI is installed (optional but recommended)
gh auth login

# Or set GitHub token as environment variable
export GITHUB_TOKEN=your_token_here
```

### Basic Usage

```bash
# Analyze all open PRs
python pr_analyzer.py

# Run full cleanup in dry-run mode (default)
python pr_cleanup_orchestrator.py

# Run full cleanup in live mode (actually merges PRs)
python pr_cleanup_orchestrator.py --live

# Process only Dependabot PRs
python dependabot_handler.py

# Review security PRs
python security_pr_reviewer.py

# Check CI status for all PRs
python ci_status_checker.py
```

## PR Categories

### 1. Dependabot PRs (#107-#121)
- **Total**: 15 PRs
- **Strategy**: Automated processing
- **Action**: Auto-merge if CI passes and no major version bumps
- **Priority**: Medium

Example PRs:
- #121: Bump @types/node (visualization-backend)
- #120: Bump eslint (frontend)
- #119: Bump next (frontend)
- #118: Bump pytest (backend)

### 2. Security PRs (#104-#106)
- **Total**: 3 PRs (Aikido security fixes)
- **Strategy**: Manual review required
- **Action**: High priority review and merge
- **Priority**: Critical

Security PRs:
- #104: Aikido Security: Fixes for 2 vulnerabilities
- #105: Aikido Security: Fixes for 2 vulnerabilities
- #106: Aikido Security: Fixes for 2 vulnerabilities

### 3. Feature PRs (#122)
- **Total**: 1 massive PR
- **Size**: 54,851 additions, 31,871 deletions across 357 files
- **Strategy**: Staged merge approach
- **Action**: Break down and review carefully
- **Priority**: Low (due to size and complexity)

### 4. Other PRs (#93)
- **Total**: 1 PR (Copilot security fix)
- **Strategy**: Case-by-case evaluation
- **Action**: Manual review
- **Priority**: Medium

## Components

### 1. GitHub API Client (`github_api_client.py`)
Core API integration with:
- Rate limiting and retry logic
- Caching for improved performance
- Dry-run mode for testing
- Support for both REST API and GitHub CLI

### 2. PR Analyzer (`pr_analyzer.py`)
Comprehensive analysis providing:
- PR categorization by type
- Risk assessment
- Conflict detection
- Dependency analysis
- Priority scoring

### 3. Dependabot Handler (`dependabot_handler.py`)
Automated processing with:
- Security update prioritization
- Major version bump detection
- Batch processing limits
- CI validation

### 4. Security PR Reviewer (`security_pr_reviewer.py`)
Security-focused review including:
- Vulnerability assessment
- Security scan validation
- Risk evaluation
- Compliance checks

### 5. Feature PR Reviewer (`feature_pr_reviewer.py`)
Large PR analysis with:
- Component breakdown
- Impact assessment
- Test coverage analysis
- Breaking change detection

### 6. CI Status Checker (`ci_status_checker.py`)
Real-time CI monitoring:
- Status tracking for all checks
- Failure pattern analysis
- Fix recommendations
- Required check validation

### 7. PR Decision Matrix (`pr_decision_matrix.py`)
Systematic decision-making:
- Scoring algorithms
- Automated decisions for low-risk PRs
- Confidence scoring
- Action recommendations

### 8. Branch Cleanup (`branch_cleanup.py`)
Post-merge maintenance:
- Merged branch deletion
- Remote reference pruning
- Repository optimization
- Protected branch handling

### 9. PR Cleanup Orchestrator (`pr_cleanup_orchestrator.py`)
Main coordinator executing:
1. Comprehensive analysis
2. CI status verification
3. Security PR processing
4. Dependabot handling
5. Feature PR review
6. Decision making
7. Branch cleanup

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
repository:
  owner: "OmarA1-Bakri"
  name: "ruleIQ"

pr_categories:
  dependabot:
    auto_merge: true
    max_major_version_bumps: 0
    batch_size: 5

  security:
    priority: "critical"
    auto_merge: false

  feature:
    max_file_changes: 100
    required_reviews: 2

dry_run:
  enabled: true  # Set to false for production
```

## Decision Matrix

The system uses a scoring algorithm to determine actions:

| Decision | Score | Action |
|----------|-------|--------|
| auto_merge | ≥80% | Automatically merge |
| ready_for_merge | ≥64% | Quick review then merge |
| needs_review | ≥48% | Thorough review required |
| manual_review | <48% | Manual intervention needed |
| blocked | N/A | Fix required factors first |

## Safety Measures

1. **Dry Run Mode**: Default operation mode for testing
2. **CI Validation**: All required checks must pass
3. **Conflict Detection**: PRs with conflicts are not auto-merged
4. **Major Version Protection**: Major bumps require manual review
5. **Security Priority**: Security fixes get immediate attention
6. **Audit Logging**: All actions are logged and reported
7. **Rollback Procedures**: Each action has recovery steps

## Reports

The system generates multiple reports:

- `pr_analysis_report.md` - Comprehensive PR analysis
- `dependabot_processing_report.md` - Dependabot handling results
- `security_review_report.md` - Security PR assessments
- `ci_status_report.md` - CI/CD status overview
- `orchestration_report.md` - Complete cleanup summary

## Workflow Examples

### Example 1: Clean Up All Dependabot PRs

```bash
# First, analyze current state
python pr_analyzer.py

# Process Dependabot PRs in dry-run
python dependabot_handler.py

# If satisfied, run in live mode
GITHUB_TOKEN=your_token python dependabot_handler.py --live
```

### Example 2: Review and Merge Security PRs

```bash
# Review security PRs
python security_pr_reviewer.py

# Check CI status
python ci_status_checker.py

# If all checks pass, merge manually or use orchestrator
python pr_cleanup_orchestrator.py --live
```

### Example 3: Full Repository Cleanup

```bash
# Complete cleanup workflow
python pr_cleanup_orchestrator.py

# Review the report
cat orchestration_report.md

# If everything looks good, run live
python pr_cleanup_orchestrator.py --live

# Clean up branches
python branch_cleanup.py
```

## Troubleshooting

### Common Issues

1. **Rate Limiting**
   - Solution: Use GitHub token for higher limits
   - The system automatically handles rate limits with retry logic

2. **CI Failures**
   - Solution: Use `ci_status_checker.py` to identify issues
   - System provides fix recommendations

3. **Merge Conflicts**
   - Solution: Conflicts must be resolved manually
   - System identifies and reports conflicting PRs

4. **Authentication Errors**
   - Solution: Ensure GitHub token is set correctly
   - Use `gh auth status` to verify GitHub CLI auth

### Debug Mode

Enable detailed logging:

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG
python pr_cleanup_orchestrator.py
```

## Best Practices

1. **Always Start with Dry Run**: Test operations before live execution
2. **Review Reports**: Check generated reports before proceeding
3. **Priority Order**: Process security > dependabot > features > others
4. **Batch Limits**: Respect configured batch sizes to avoid issues
5. **Monitor CI**: Ensure CI passes before merging
6. **Document Decisions**: Keep records of manual interventions

## Architecture

```
┌─────────────────────────────────────┐
│    PR Cleanup Orchestrator          │
└─────────────┬───────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐      ┌───────▼──────┐
│Analyzer│      │GitHub Client │
└───┬────┘      └───────┬──────┘
    │                   │
┌───▼─────────────────────▼────┐
│   Component Processors       │
├──────────────────────────────┤
│ • Dependabot Handler         │
│ • Security Reviewer          │
│ • Feature Reviewer           │
│ • CI Status Checker          │
│ • Decision Matrix            │
│ • Branch Cleanup             │
└──────────────────────────────┘
```

## Contributing

When extending the system:

1. Follow existing patterns for new components
2. Add appropriate error handling
3. Support dry-run mode
4. Generate reports for actions
5. Update configuration schema
6. Add comprehensive logging

## License

This PR management system is part of the ruleIQ project.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review generated reports for details
3. Enable debug logging for more information
4. Consult the team for complex scenarios