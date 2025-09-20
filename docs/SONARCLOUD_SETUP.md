# SonarCloud Setup Guide

## Quick Start

### Step 1: Generate SonarCloud Token

1. Go to https://sonarcloud.io
2. Click your profile picture → **My Account**
3. Navigate to **Security** tab
4. Under **Generate Tokens**, enter name: `github-actions-ci`
5. Click **Generate**
6. **IMPORTANT: Copy the token immediately** (you won't see it again!)

### Step 2: Choose Your Setup Method

#### Method A: Manual Run (Fastest for Testing)
1. Go to https://github.com/OmarA1-Bakri/ruleIQ/actions
2. Click **"SonarCloud Analysis"** workflow
3. Click **Run workflow** button
4. Paste your token in the `sonar_token` field
5. Click green **Run workflow** button

#### Method B: GitHub Secrets (Automatic for Every Run)
1. Go to https://github.com/OmarA1-Bakri/ruleIQ/settings/secrets/actions
2. Click **New repository secret**
3. Name: `SONAR_TOKEN`
4. Value: *paste your SonarCloud token*
5. Click **Add secret**

#### Method C: Doppler Integration (Optional)
1. Store token in Doppler:
   ```bash
   doppler secrets set SONAR_TOKEN="your-token-here"
   ```
2. Ensure these GitHub Secrets exist:
   - `DOPPLER_TOKEN`
   - `DOPPLER_PROJECT`
   - `DOPPLER_CONFIG`

## Verification

### Check Workflow Logs
1. Go to **Actions** tab after running workflow
2. Click on the running/completed workflow
3. Look for one of these messages:
   - ✅ "Using SONAR_TOKEN from workflow input"
   - ✅ "Using SONAR_TOKEN from GitHub Secrets"
   - ✅ "Loaded SONAR_TOKEN from Doppler"

### Check SonarCloud Dashboard
Visit: https://sonarcloud.io/project/overview?id=ruliq-compliance-platform

You should see:
- Code analysis results
- Coverage metrics
- Code quality ratings
- Security hotspots

## PR Decoration Requirements

For automatic PR comments:
1. Install SonarCloud GitHub App: https://github.com/apps/sonarcloud
2. Bind project to repository in SonarCloud settings
3. Ensure default branch in SonarCloud is set to `main`

## Security Best Practices

⚠️ **NEVER**:
- Commit tokens to code
- Share tokens publicly
- Use exposed tokens (revoke immediately if exposed)

✅ **ALWAYS**:
- Use GitHub Secrets for production
- Rotate tokens periodically
- Revoke unused tokens

## Troubleshooting

### Token Not Working
1. Check token hasn't expired
2. Verify organization membership
3. Ensure token has correct permissions

### Analysis Not Appearing
1. Check project key matches: `ruliq-compliance-platform`
2. Verify organization: `omara1-bakri`
3. Ensure workflow completed successfully

### Coverage Not Showing
1. Verify tests are running in workflow
2. Check coverage report paths in `sonar-project.properties`
3. Ensure coverage files are generated before SonarCloud scan

## Configuration Files

- **Workflow**: `.github/workflows/sonarcloud.yml`
- **Project Config**: `sonar-project.properties`
- **Project Key**: `ruliq-compliance-platform`
- **Organization**: `omara1-bakri`