# SonarCloud Integration

This directory contains all SonarCloud-related configuration, documentation, and utilities for the ruleIQ project.

## 📁 Directory Structure

```
sonarcloud/
├── README.md                      # This file
├── sonar-project.properties       # Main SonarCloud configuration
├── SONARQUBE_SETUP.md            # Initial setup documentation
├── SONARCLOUD_SPRINT_PLAN.md    # Quality improvement sprint plan
├── check_sonar_results.py        # Script to check analysis results
├── update_archon_tasks.py        # Script to update Archon tasks from analysis
└── complete_archon_task.py       # Script to mark Archon tasks complete
```

## 🚀 Quick Start

### Running SonarCloud Analysis

```bash
# From project root
npx sonarqube-scanner
```

Or with explicit token:
```bash
SONAR_TOKEN=78c39861ad8fa298fc7b3184cfe6573012b9af49 npx sonarqube-scanner
```

### Check Analysis Results

```bash
# Check current quality metrics
python sonarcloud/check_sonar_results.py
```

## 📊 Current Status

- **Project Key:** `ruliq-compliance-platform`
- **Organization:** `omara1-bakri`
- **Quality Gate:** FAILED ❌
- **Total Issues:** 4,521
- **Test Coverage:** 0%

## 🔗 Important Links

- **SonarCloud Dashboard:** https://sonarcloud.io/summary/overall?id=ruliq-compliance-platform
- **Organization:** https://sonarcloud.io/organizations/omara1-bakri
- **Quality Gate:** https://sonarcloud.io/project/quality_gate?id=ruliq-compliance-platform

## 🎯 Quality Goals

Based on our sprint plan (see `SONARCLOUD_SPRINT_PLAN.md`):

1. **Immediate:** Fix all 62 blocker issues
2. **Week 1:** Address 16 security vulnerabilities
3. **Week 2:** Review 369 security hotspots
4. **Week 3:** Reduce duplication to <3%
5. **Week 4:** Achieve 80%+ test coverage

## 🛠️ Utility Scripts

### check_sonar_results.py
Fetches and displays current SonarCloud metrics including:
- Quality gate status
- Issue counts by type and severity
- Code coverage and duplication metrics
- Top rule violations

### update_archon_tasks.py
Creates/updates Archon project management tasks based on SonarCloud analysis:
- Archives completed tasks
- Creates new tasks for identified issues
- Prioritizes by severity and impact

### complete_archon_task.py
Marks Archon tasks as complete when issues are resolved.

## 📈 Progress Tracking

Track our quality improvement progress:

| Metric | Initial | Current | Target |
|--------|---------|---------|--------|
| Total Issues | 4,898 | 4,521 | <500 |
| Blocker Issues | 62 | 62 | 0 |
| Critical Issues | 1,514 | 1,514 | <50 |
| Security Rating | E | E | B |
| Reliability Rating | E | E | B |
| Test Coverage | 0% | 0% | >80% |
| Duplication | 5.9% | 5.9% | <3% |

## 🔐 Security Note

The SonarCloud token is currently hardcoded in scripts for development. 
For production, use environment variables:

```bash
export SONAR_TOKEN=your-token-here
```

## 📝 Configuration

The main configuration file `sonar-project.properties` includes:
- Project metadata
- Source and test directories
- Language-specific settings
- Exclusion patterns
- Quality profiles

**Note:** A symlink to `sonar-project.properties` exists in the project root as required by the SonarCloud scanner.

## 🤝 Integration with CI/CD

To integrate with GitHub Actions, add to `.github/workflows/sonarcloud.yml`:

```yaml
name: SonarCloud
on:
  push:
    branches: [ main ]
  pull_request:
    types: [opened, synchronize, reopened]
jobs:
  sonarcloud:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: SonarCloud Scan
      uses: SonarSource/sonarcloud-github-action@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

## 📚 Additional Resources

- [SonarCloud Documentation](https://docs.sonarcloud.io/)
- [Quality Gate Configuration](https://docs.sonarcloud.io/improving/quality-gates/)
- [Security Hotspot Review](https://docs.sonarcloud.io/digging-deeper/security-hotspots/)
- [Test Coverage Import](https://docs.sonarcloud.io/enriching/test-coverage/)