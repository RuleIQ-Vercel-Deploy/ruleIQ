# SonarQube Analysis Guide for ruleIQ

## Project Configuration
- **Project Key:** `ruliq-compliance-platform`
- **SonarQube User:** `omara1-bakri`

## Step 1: Store Your Token Securely

### Option A: Using Doppler (Recommended)
```bash
# Store your SonarQube token in Doppler
doppler secrets set SONAR_TOKEN="your_token_here"
doppler secrets set SONAR_HOST_URL="http://localhost:9000"  # or your SonarQube URL
```

### Option B: Environment Variable (Temporary)
```bash
# For current session only
export SONAR_TOKEN="your_token_here"
export SONAR_HOST_URL="http://localhost:9000"
```

## Step 2: Install SonarQube Scanner

### Option A: Using Docker (Easiest)
```bash
# No installation needed, run directly:
docker run \
  --rm \
  --network="host" \
  -e SONAR_HOST_URL="http://localhost:9000" \
  -e SONAR_TOKEN="your_token_here" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli
```

### Option B: Install Locally
```bash
# Download scanner
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-linux-x64.zip
unzip sonar-scanner-cli-6.2.1.4610-linux-x64.zip
sudo mv sonar-scanner-6.2.1.4610-linux-x64 /opt/sonar-scanner

# Add to PATH
echo 'export PATH="/opt/sonar-scanner/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Step 3: Run Analysis

### Using Doppler (Recommended)
```bash
# From project root (/home/omar/Documents/ruleIQ)
doppler run -- sonar-scanner \
  -Dsonar.host.url="$(doppler secrets get SONAR_HOST_URL --plain)" \
  -Dsonar.token="$(doppler secrets get SONAR_TOKEN --plain)" \
  -Dsonar.projectKey=ruliq-compliance-platform
```

### Direct Command
```bash
# From project root
sonar-scanner \
  -Dsonar.host.url="http://localhost:9000" \
  -Dsonar.token="YOUR_TOKEN_HERE" \
  -Dsonar.projectKey=ruliq-compliance-platform \
  -Dsonar.login=omara1-bakri
```

### Using Docker
```bash
# From project root
docker run \
  --rm \
  --network="host" \
  -e SONAR_HOST_URL="http://localhost:9000" \
  -e SONAR_TOKEN="YOUR_TOKEN_HERE" \
  -e SONAR_SCANNER_OPTS="-Dsonar.projectKey=ruliq-compliance-platform" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli
```

## Step 4: Generate Coverage Reports (Optional but Recommended)

### Python Coverage
```bash
# Run tests with coverage
cd /home/omar/Documents/ruleIQ
pytest --cov=api --cov=services --cov-report=xml --cov-report=html

# The coverage.xml file will be picked up by SonarQube
```

### Frontend Coverage
```bash
cd frontend
npm run test:coverage
# This generates frontend/coverage/lcov.info
```

## Step 5: View Results

1. Open your SonarQube instance: `http://localhost:9000`
2. Login with your credentials (`omara1-bakri`)
3. Navigate to Projects → `ruliq-compliance-platform`
4. Review:
   - Code Quality metrics
   - Security Hotspots
   - Code Smells
   - Technical Debt
   - Coverage (if reports were generated)

## Automation Scripts

### Create a Makefile target
Add to your Makefile:
```makefile
sonar-scan:
	@echo "Running SonarQube analysis..."
	@doppler run -- sonar-scanner \
		-Dsonar.host.url="$$(doppler secrets get SONAR_HOST_URL --plain)" \
		-Dsonar.token="$$(doppler secrets get SONAR_TOKEN --plain)" \
		-Dsonar.projectKey=ruliq-compliance-platform

sonar-scan-with-coverage: test-coverage
	@echo "Running SonarQube with coverage..."
	@$(MAKE) sonar-scan
```

### Create a shell script
Save as `run-sonar.sh`:
```bash
#!/bin/bash
set -e

echo "🔍 Starting SonarQube Analysis for ruleIQ..."

# Check if token is set
if [ -z "$SONAR_TOKEN" ]; then
    echo "❌ Error: SONAR_TOKEN not set"
    echo "Run: export SONAR_TOKEN='your_token_here'"
    exit 1
fi

# Run analysis
sonar-scanner \
  -Dsonar.host.url="${SONAR_HOST_URL:-http://localhost:9000}" \
  -Dsonar.token="$SONAR_TOKEN" \
  -Dsonar.projectKey=ruliq-compliance-platform \
  -Dsonar.login=omara1-bakri

echo "✅ Analysis complete! Check results at: ${SONAR_HOST_URL:-http://localhost:9000}"
```

Make it executable:
```bash
chmod +x run-sonar.sh
```

## Troubleshooting

### Common Issues

1. **Token Authentication Failed**
   - Verify token is correct and not expired
   - Check if token has 'Execute Analysis' permission

2. **Project Not Found**
   - Ensure project key matches: `ruliq-compliance-platform`
   - Project might need to be created first in SonarQube UI

3. **Scanner Not Found**
   - Verify scanner is in PATH: `which sonar-scanner`
   - Use Docker method if installation issues persist

4. **Connection Refused**
   - Check SonarQube is running: `curl http://localhost:9000`
   - Verify correct URL in SONAR_HOST_URL

5. **Out of Memory (Large Project)**
   - Increase memory: `export SONAR_SCANNER_OPTS="-Xmx2048m"`

## CI/CD Integration

### GitHub Actions
See `.github/workflows/sonarqube.yml` for automated analysis on push.

### GitLab CI
```yaml
sonarqube-check:
  image: sonarsource/sonar-scanner-cli:latest
  variables:
    SONAR_USER_HOME: "${CI_PROJECT_DIR}/.sonar"
    GIT_DEPTH: "0"
  cache:
    key: "${CI_JOB_NAME}"
    paths:
      - .sonar/cache
  script:
    - sonar-scanner
```

## Next Steps

After your first analysis:
1. Review the Quality Gate status
2. Fix Critical and Blocker issues first
3. Address Security Hotspots
4. Improve code coverage
5. Set up branch analysis for PRs

## Support

- SonarQube Docs: https://docs.sonarqube.org/
- Project Key: `ruliq-compliance-platform`
- User: `omara1-bakri`