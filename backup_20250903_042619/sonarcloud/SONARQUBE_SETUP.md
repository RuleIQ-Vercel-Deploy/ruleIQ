# SonarQube Setup Guide for ruleIQ

## 🎯 Overview

This guide helps you set up SonarQube analysis for the ruleIQ compliance platform, including both local development with SonarLint and CI/CD integration.

## 📋 Prerequisites

- VS Code installed
- Docker (for local SonarQube server, optional)
- SonarQube Server or SonarCloud account
- GitHub repository with secrets configured

## 🔧 VS Code Extension Setup

### Step 1: Install SonarLint Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "SonarLint"
4. Install the official "SonarLint" extension by SonarSource
5. Install recommended extensions from `.vscode/extensions.json`

### Step 2: Configure SonarLint Connection

#### Option A: SonarCloud (Recommended)

1. Open VS Code settings (Ctrl+,)
2. Search for "sonarlint"
3. Find "SonarLint: Connected Mode"
4. Add connection:
   ```json
   {
     "connectionId": "ruleiq-sonarcloud",
     "serverUrl": "https://sonarcloud.io",
     "token": "YOUR_SONARCLOUD_TOKEN",
     "organizationKey": "ruleiq-compliance-platform"
   }
   ```

#### Option B: Self-hosted SonarQube

1. Configure connection:
   ```json
   {
     "connectionId": "ruleiq-sonarqube",
     "serverUrl": "https://your-sonarqube-server.com",
     "token": "YOUR_SONAR_TOKEN"
   }
   ```

### Step 3: Bind Project

1. Open Command Palette (Ctrl+Shift+P)
2. Run "SonarLint: Add SonarQube/SonarCloud project binding"
3. Select your connection
4. Choose project key: `ruleiq-compliance-platform`

## 🌐 SonarQube Server Setup

### Option 1: Local Docker Setup

```bash
# Run SonarQube locally
docker run -d --name sonarqube \
  -p 9000:9000 \
  -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
  sonarqube:latest

# Access at http://localhost:9000
# Default credentials: admin/admin
```

### Option 2: SonarCloud (Easiest)

1. Go to [SonarCloud.io](https://sonarcloud.io)
2. Sign in with GitHub
3. Import your ruleIQ repository
4. Get your organization key and project key
5. Generate a token for CI/CD

## 🔐 GitHub Secrets Configuration

Add these secrets to your GitHub repository:

```bash
# For SonarCloud
SONAR_TOKEN=your_sonarcloud_token
SONAR_ORGANIZATION=your_org_key

# For self-hosted SonarQube
SONAR_TOKEN=your_sonar_token
SONAR_HOST_URL=https://your-sonarqube-server.com
```

## 📝 Configuration Files Explained

### `sonar-project.properties`

Main configuration file with:

- Project identification
- Source code paths
- Exclusion patterns
- Language-specific settings
- Coverage report paths

### `.sonarcloud.properties`

SonarCloud-specific settings:

- Branch analysis configuration
- Pull request integration
- GitHub links

### `.vscode/settings.json`

VS Code workspace settings:

- SonarLint connection
- Python/TypeScript configurations
- Code formatting rules

## 🚀 Running Analysis

### Local Analysis (VS Code)

- SonarLint will automatically analyze open files
- Issues appear as squiggly underlines
- Hover for detailed explanations
- Use Problems panel to see all issues

### CI/CD Analysis

- Analysis runs automatically on push/PR
- GitHub workflow in `.github/workflows/sonarqube.yml`
- Results appear in SonarQube dashboard
- Quality Gate blocks merging if failed

### Manual Local Scan

```bash
# Install SonarQube scanner
npm install -g sonarqube-scanner

# Run analysis
sonar-scanner \
  -Dsonar.projectKey=ruleiq-compliance-platform \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=your_token
```

## 📊 Quality Gates

Default quality conditions:

- **Coverage**: > 80%
- **Duplicated Lines**: < 3%
- **Maintainability Rating**: A
- **Reliability Rating**: A
- **Security Rating**: A
- **Security Hotspots**: 100% reviewed

## 🛠 Troubleshooting

### Common Issues

1. **SonarLint not connecting**

   - Check token permissions
   - Verify server URL
   - Restart VS Code

2. **Analysis failing in CI**

   - Check GitHub secrets
   - Verify sonar-project.properties syntax
   - Check runner permissions

3. **Python analysis issues**

   - Ensure virtual environment is activated
   - Check Python path in settings
   - Verify coverage reports generated

4. **TypeScript analysis issues**
   - Check tsconfig.json path
   - Ensure Node.js version compatibility
   - Verify ESLint reports generated

### Debug Commands

```bash
# Check SonarQube scanner version
sonar-scanner --version

# Validate project properties
sonar-scanner -Dsonar.analysis.mode=preview

# Test connection
curl -u your_token: https://sonarcloud.io/api/authentication/validate
```

## 📈 Benefits

### Development Benefits

- **Real-time feedback** on code quality
- **Security vulnerability** detection
- **Code smell** identification
- **Consistent coding standards**

### Team Benefits

- **Quality metrics** tracking
- **Technical debt** monitoring
- **Code coverage** reporting
- **Pull request** quality gates

## 🔄 Next Steps

1. **Configure Quality Profiles** for your team's standards
2. **Set up notifications** for quality gate failures
3. **Create custom rules** for project-specific requirements
4. **Integrate with IDE** for all team members
5. **Monitor technical debt** trends over time

## 📚 Resources

- [SonarLint Documentation](https://docs.sonarqube.org/latest/user-guide/sonarlint/)
- [SonarCloud Documentation](https://docs.sonarcloud.io/)
- [SonarQube Community](https://community.sonarsource.com/)
- [Quality Gates Guide](https://docs.sonarqube.org/latest/user-guide/quality-gates/)

---

**Need help?** Check the troubleshooting section or reach out to the development team.
