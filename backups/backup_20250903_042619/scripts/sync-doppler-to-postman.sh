#!/bin/bash

# Sync Doppler secrets to Postman environment file
# This script fetches secrets from Doppler and creates a Postman-compatible environment file

set -e

echo "🔄 Syncing Doppler secrets to Postman environment..."

# Check if Doppler CLI is installed
if ! command -v doppler &> /dev/null; then
    echo "❌ Doppler CLI is not installed. Please install it first."
    exit 1
fi

# Check if jq is installed for JSON processing
if ! command -v jq &> /dev/null; then
    echo "❌ jq is not installed. Installing..."
    sudo apt-get update && sudo apt-get install -y jq
fi

# Get the environment name from Doppler
DOPPLER_ENV=$(doppler configs get --json 2>/dev/null | jq -r '.config // "dev"')
if [ -z "$DOPPLER_ENV" ]; then
    DOPPLER_ENV="dev"
fi
echo "📍 Current Doppler environment: $DOPPLER_ENV"

# Fetch all secrets from Doppler
echo "🔑 Fetching secrets from Doppler..."
SECRETS=$(doppler secrets download --no-file --format json)

# Create output directory if it doesn't exist
mkdir -p postman

# Generate timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

# Create Postman environment file with Doppler secrets
cat > postman/environment-doppler-synced.json << EOF
{
  "id": "doppler-synced-${DOPPLER_ENV}",
  "name": "RuleIQ ${DOPPLER_ENV} (Doppler Synced)",
  "values": [
EOF

# Add base configuration
cat >> postman/environment-doppler-synced.json << EOF
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "default",
      "enabled": true
    },
    {
      "key": "api_version",
      "value": "$(echo $SECRETS | jq -r '.API_VERSION // "v1"')",
      "type": "default",
      "enabled": true
    },
    {
      "key": "api_url",
      "value": "{{base_url}}/api/{{api_version}}",
      "type": "default",
      "enabled": true
    }
EOF

# Process each Doppler secret and add to environment
FIRST=true
echo "$SECRETS" | jq -r 'to_entries[] | @base64' | while read -r secret; do
    _jq() {
        echo ${secret} | base64 --decode | jq -r ${1}
    }
    
    KEY=$(_jq '.key')
    VALUE=$(_jq '.value')
    
    # Convert to lowercase and replace underscores for Postman
    POSTMAN_KEY=$(echo "$KEY" | tr '[:upper:]' '[:lower:]' | tr '_' '-')
    
    # Determine if this is a secret or regular value
    TYPE="default"
    if [[ "$KEY" == *"SECRET"* ]] || [[ "$KEY" == *"KEY"* ]] || [[ "$KEY" == *"TOKEN"* ]] || [[ "$KEY" == *"PASSWORD"* ]]; then
        TYPE="secret"
    fi
    
    # Add comma for all except first processed secret
    echo "    ," >> postman/environment-doppler-synced.json
    
    # Add the secret to the environment file
    cat >> postman/environment-doppler-synced.json << EOF
    {
      "key": "doppler_${POSTMAN_KEY}",
      "value": "${VALUE}",
      "type": "${TYPE}",
      "enabled": true
    }
EOF
done

# Add runtime variables (empty by default)
cat >> postman/environment-doppler-synced.json << EOF
,
    {
      "key": "access_token",
      "value": "",
      "type": "default",
      "enabled": true
    },
    {
      "key": "refresh_token",
      "value": "",
      "type": "default",
      "enabled": true
    },
    {
      "key": "current_user_id",
      "value": "",
      "type": "default",
      "enabled": true
    },
    {
      "key": "current_session_id",
      "value": "",
      "type": "default",
      "enabled": true
    }
  ],
  "_postman_variable_scope": "environment",
  "_postman_exported_at": "${TIMESTAMP}",
  "_postman_exported_using": "Doppler-Sync/1.0.0"
}
EOF

echo "✅ Postman environment file created: postman/environment-doppler-synced.json"

# Create a Newman-compatible environment file
echo "🔧 Creating Newman-compatible environment file..."

cat > postman/newman-environment-doppler.json << EOF
{
  "name": "RuleIQ ${DOPPLER_ENV} (Newman)",
  "values": [
EOF

# Add base URL - use backend port for API testing
APP_URL="http://localhost:8000"
API_VERSION=$(echo "$SECRETS" | jq -r '.API_VERSION // "v1"')

cat >> postman/newman-environment-doppler.json << EOF
    {
      "key": "base_url",
      "value": "${APP_URL}",
      "enabled": true
    },
    {
      "key": "api_version",
      "value": "${API_VERSION}",
      "enabled": true
    }
EOF

# Add critical secrets for Newman
for KEY in DATABASE_URL JWT_SECRET_KEY GOOGLE_AI_API_KEY OPENAI_API_KEY ENCRYPTION_KEY; do
    VALUE=$(echo "$SECRETS" | jq -r ".${KEY} // \"\"")
    if [ -n "$VALUE" ]; then
        NEWMAN_KEY=$(echo "$KEY" | tr '[:upper:]' '[:lower:]')
        cat >> postman/newman-environment-doppler.json << EOF
,
    {
      "key": "${NEWMAN_KEY}",
      "value": "${VALUE}",
      "enabled": true
    }
EOF
    fi
done

cat >> postman/newman-environment-doppler.json << EOF

  ]
}
EOF

echo "✅ Newman environment file created: postman/newman-environment-doppler.json"

# Summary
echo ""
echo "📊 Sync Summary:"
echo "  - Doppler Environment: $DOPPLER_ENV"
echo "  - Secrets Synced: $(echo "$SECRETS" | jq 'keys | length')"
echo "  - Postman File: postman/environment-doppler-synced.json"
echo "  - Newman File: postman/newman-environment-doppler.json"
echo ""
echo "📌 Import Instructions:"
echo "  1. Open Postman"
echo "  2. Go to Environments"
echo "  3. Click Import"
echo "  4. Select: postman/environment-doppler-synced.json"
echo ""
echo "🔐 Security Notes:"
echo "  - These files contain sensitive data"
echo "  - Do NOT commit them to version control"
echo "  - Add them to .gitignore if not already there"

# Check if files are in .gitignore
if ! grep -q "environment-doppler-synced.json" .gitignore 2>/dev/null; then
    echo "postman/environment-doppler-synced.json" >> .gitignore
    echo "postman/newman-environment-doppler.json" >> .gitignore
    echo "  ✅ Added synced environment files to .gitignore"
fi

echo ""
echo "✅ Doppler-Postman sync complete!"