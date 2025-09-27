#!/bin/bash
# Cloud Run Startup Diagnostics Script
# Helps identify why the container failed to start

set -e

PROJECT_ID=${PROJECT_ID:-$(gcloud config get project 2>/dev/null)}
SERVICE_NAME=${SERVICE_NAME:-ruleiq-backend}
REGION=${REGION:-europe-west2}

echo "🔍 Cloud Run Startup Diagnostics"
echo "================================"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo

# 1. Check service status
echo "📊 Service Status:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.conditions[0].message,status.conditions[0].type,status.conditions[0].status)" 2>/dev/null || echo "Service not found"
echo

# 2. Get recent logs (startup failures)
echo "📋 Recent Container Logs (last 10 minutes):"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
  --limit=50 --format="value(timestamp,severity,textPayload)" \
  --freshness=10m 2>/dev/null || echo "No logs found"
echo

# 3. Check revisions and traffic
echo "🚦 Current Revisions:"
gcloud run revisions list --service=$SERVICE_NAME --region=$REGION --format="table(metadata.name,status.conditions[0].type,status.conditions[0].status,spec.containerConcurrency)" 2>/dev/null || echo "No revisions found"
echo

# 4. Get latest revision details
LATEST_REVISION=$(gcloud run revisions list --service=$SERVICE_NAME --region=$REGION --format="value(metadata.name)" --limit=1 2>/dev/null | head -1)
if [[ -n "$LATEST_REVISION" ]]; then
    echo "🔧 Latest Revision Details ($LATEST_REVISION):"
    gcloud run revisions describe $LATEST_REVISION --region=$REGION --format="yaml(spec.container)" 2>/dev/null || echo "Could not get revision details"
fi
echo

# 5. Test locally with same command
echo "🧪 Testing Container Locally:"
echo "You can test the same container locally with:"
echo "docker run -p 8080:8080 -e DOPPLER_TOKEN=\$DOPPLER_TOKEN gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"
echo

# 6. Common fixes
echo "🔨 Common Fixes:"
echo "1. Container exits immediately:"
echo "   - Check CMD/ENTRYPOINT in Dockerfile"
echo "   - Ensure app binds to 0.0.0.0:\$PORT not localhost"
echo "   - Verify DOPPLER_TOKEN secret is accessible"
echo ""
echo "2. Import/startup errors:"  
echo "   - Test locally: doppler run -- python -c 'from api.main import app'"
echo "   - Check Python path and dependencies in container"
echo ""
echo "3. Port binding issues:"
echo "   - Cloud Run sets PORT env var, ensure app uses it"
echo "   - App should bind to 0.0.0.0:\$PORT not 127.0.0.1:8000"
echo ""
echo "4. Secret access:"
echo "   - Verify DOPPLER_TOKEN secret exists in Secret Manager"
echo "   - Check Cloud Run service account has access to secrets"