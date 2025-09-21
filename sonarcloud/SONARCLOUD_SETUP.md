# SonarCloud Setup for ruleIQ

## Configuration Details
- **Project Key:** `ruliq-compliance-platform`
- **Token:** Stored in Doppler as `SONAR_TOKEN`
- **Cloud URL:** https://sonarcloud.io
- **Username:** `omara1-bakri`

## Prerequisites

### 1. Install SonarScanner CLI
```bash
# Option A: Using npm (recommended)
npm install -g sonarqube-scanner

# Option B: Download directly
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-linux-x64.zip
unzip sonar-scanner-cli-6.2.1.4610-linux-x64.zip
sudo mv sonar-scanner-6.2.1.4610-linux-x64 /opt/sonar-scanner
export PATH="/opt/sonar-scanner/bin:$PATH"
```

### 2. Verify Installation
```bash
sonar-scanner --version
```

## Update Configuration for Cloud

Update your `sonar-project.properties` with cloud-specific settings:

```properties
# Required for SonarCloud
sonar.organization=your-organization-key  # UPDATE THIS
sonar.host.url=https://sonarcloud.io
```

## Running Analysis

### Option 1: Using Doppler (Recommended)
```bash
# From project root
cd /home/omar/Documents/ruleIQ

# Run analysis
doppler run -- sonar-scanner \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.token="$(doppler secrets get SONAR_TOKEN --plain)" \
  -Dsonar.projectKey=ruliq-compliance-platform \
  -Dsonar.organization=your-organization-key
```

### Option 2: Direct Command
```bash
sonar-scanner \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.token=${SONAR_TOKEN} \
  -Dsonar.projectKey=ruliq-compliance-platform \
  -Dsonar.organization=your-organization-key
```

### Option 3: Using NPM Package
```bash
# If installed via npm
sonarqube-scanner \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.token=${SONAR_TOKEN} \
  -Dsonar.projectKey=ruliq-compliance-platform \
  -Dsonar.organization=your-organization-key
```

## GitHub Actions Integration

Create `.github/workflows/sonarcloud.yml`:

```yaml
name: SonarCloud Analysis
on:
  push:
    branches: [ main, develop ]
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  sonarcloud:
    name: SonarCloud
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Shallow clones disabled for better analysis

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest --cov=api --cov=services --cov-report=xml

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install frontend dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Run frontend tests
        working-directory: ./frontend
        run: npm run test:coverage

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

## Add GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add these secrets:
   - `SONAR_TOKEN`: (Your SonarCloud token - get from SonarCloud security settings)
   - `SONAR_ORGANIZATION`: your-organization-key

## Alternative: Using SonarCloud Auto-Configuration

If you have admin access to SonarCloud:

1. Login to https://sonarcloud.io
2. Click "+" → "Analyze new project"
3. Select your GitHub repository
4. Follow the automatic setup wizard
5. SonarCloud will create the configuration for you

## Create Analysis Script

Save as `run-sonarcloud.sh`:

```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 Starting SonarCloud Analysis for ruleIQ...${NC}"

# Check organization key
if [ -z "$SONAR_ORGANIZATION" ]; then
    echo -e "${RED}❌ Error: SONAR_ORGANIZATION not set${NC}"
    echo "Please set your organization key:"
    echo "  export SONAR_ORGANIZATION='your-org-key'"
    exit 1
fi

# Get token from Doppler
SONAR_TOKEN=$(doppler secrets get SONAR_TOKEN --plain 2>/dev/null)
if [ -z "$SONAR_TOKEN" ]; then
    echo -e "${RED}❌ Error: Could not retrieve SONAR_TOKEN from Doppler${NC}"
    exit 1
fi

# Run Python tests with coverage (optional)
echo -e "${YELLOW}Running Python tests with coverage...${NC}"
pytest --cov=api --cov=services --cov-report=xml --cov-report=term || true

# Run frontend tests with coverage (optional)
echo -e "${YELLOW}Running frontend tests with coverage...${NC}"
cd frontend && npm run test:coverage || true
cd ..

# Run SonarCloud analysis
echo -e "${YELLOW}Running SonarCloud analysis...${NC}"
sonar-scanner \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.token="$SONAR_TOKEN" \
  -Dsonar.projectKey=ruliq-compliance-platform \
  -Dsonar.organization="$SONAR_ORGANIZATION" \
  -Dsonar.sources=. \
  -Dsonar.exclusions="**/node_modules/**,**/.venv/**,**/venv/**" \
  -Dsonar.python.coverage.reportPaths=coverage.xml \
  -Dsonar.javascript.lcov.reportPaths=frontend/coverage/lcov.info

echo -e "${GREEN}✅ Analysis complete!${NC}"
echo -e "${GREEN}View results at: https://sonarcloud.io/project/overview?id=ruliq-compliance-platform${NC}"
```

Make executable:
```bash
chmod +x run-sonarcloud.sh
```

## Verifying Connection

Test your connection:
```bash
# Test authentication
curl -u ${SONAR_TOKEN}: \
  https://sonarcloud.io/api/authentication/validate

# Should return: {"valid":true}
```

## Project Badge

Add to your README.md:
```markdown
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ruliq-compliance-platform&metric=alert_status)](https://sonarcloud.io/dashboard?id=ruliq-compliance-platform)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ruliq-compliance-platform&metric=coverage)](https://sonarcloud.io/dashboard?id=ruliq-compliance-platform)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=ruliq-compliance-platform&metric=sqale_index)](https://sonarcloud.io/dashboard?id=ruliq-compliance-platform)
```

## Troubleshooting

### Common Issues

1. **Organization Key Missing**
   - Find it at: https://sonarcloud.io/organizations
   - Or in your SonarCloud account settings

2. **Project Not Found**
   - May need to import project first at https://sonarcloud.io
   - Ensure project key matches exactly: `ruliq-compliance-platform`

3. **Authentication Failed**
   - Verify token has "Execute Analysis" permission
   - Token might be for wrong organization

4. **No Code Analysis**
   - Check file exclusions in sonar-project.properties
   - Verify source directories are correct

## Next Steps

1. **Get your organization key** from SonarCloud
2. **Run the scanner** with the organization key
3. **View results** at: https://sonarcloud.io/project/overview?id=ruliq-compliance-platform
4. **Set up CI/CD** with GitHub Actions
5. **Configure Quality Gates** in SonarCloud dashboard

## Important Notes

- SonarCloud is free for open-source projects
- Private projects require a paid plan
- Analysis runs automatically on PR/push with GitHub Actions
- Results visible at: https://sonarcloud.io/organizations/YOUR-ORG/projects