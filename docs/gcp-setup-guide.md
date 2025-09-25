# Google Cloud Platform Setup Guide for RuleIQ

## Prerequisites
1. Google Cloud account with billing enabled
2. `gcloud` CLI installed locally
3. Docker installed locally

## Step 1: Create a New Project (if needed)
```bash
gcloud projects create ruleiq-backend --name="RuleIQ Backend"
gcloud config set project ruleiq-backend
```

## Step 2: Enable Required APIs
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudresourcemanager.googleapis.com
```

## Step 3: Create Service Account for GitHub Actions
```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deploy"

# Get the service account email
SA_EMAIL=$(gcloud iam service-accounts list \
  --filter="displayName:GitHub Actions Deploy" \
  --format="value(email)")

# Grant necessary roles
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create ~/gcp-key.json \
  --iam-account="${SA_EMAIL}"
```

## Step 4: Add Secrets to GitHub

Add these secrets to your GitHub repository:

1. **GCP_PROJECT_ID**: Your Google Cloud project ID
2. **GCP_SA_KEY_PRODUCTION**: Contents of ~/gcp-key.json
3. **GCP_SA_KEY_STAGING**: Same as production (or different if using separate projects)
4. **DOPPLER_TOKEN**: Your existing Doppler token

## Step 5: Configure Doppler (if not already done)

Ensure your Doppler project has all the necessary environment variables for:
- Database connection (DATABASE_URL)
- API keys (OPENAI_API_KEY, etc.)
- Any other secrets

## Step 6: Initial Manual Deployment (Optional)

Test the deployment manually:

```bash
# Build the Docker image
docker build -t gcr.io/[PROJECT_ID]/ruleiq-backend:test .

# Push to Container Registry
docker push gcr.io/[PROJECT_ID]/ruleiq-backend:test

# Deploy to Cloud Run
gcloud run deploy ruleiq-backend \
  --image gcr.io/[PROJECT_ID]/ruleiq-backend:test \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

## Step 7: Frontend Deployment (App Engine)

For the frontend, create `frontend/app.yaml`:
```yaml
runtime: nodejs20
env: standard

instance_class: F2

env_variables:
  NODE_ENV: "production"
  NEXT_PUBLIC_API_URL: "https://ruleiq-backend-xxxxx-uc.a.run.app"

handlers:
  - url: /.*
    script: auto
    secure: always

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

## Notes

- Cloud Run automatically scales to zero when not in use (cost-effective)
- The backend will run on Cloud Run (containerized)
- The frontend can run on App Engine or Cloud Run
- All secrets are managed through Doppler
- No 250MB limit like Vercel

## Costs Estimate

- Cloud Run: ~$0.00002400 per vCPU-second
- Container Registry: ~$0.026 per GB per month
- Egress: First 1GB free, then ~$0.12 per GB
- App Engine: ~$0.05 per hour for F2 instance

## Next Steps

Once you've set up GCP:
1. Run the GitHub Actions workflow to deploy
2. Configure custom domain (optional)
3. Set up monitoring and alerts
4. Configure Cloud Armor for DDoS protection (optional)