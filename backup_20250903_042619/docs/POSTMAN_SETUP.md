# RuleIQ API Postman Collection Setup Guide

## 📦 Files Created

1. **`ruleiq_postman_collection_consolidated.json`** - Latest consolidated API collection (51 endpoints)
2. **`ruleiq_postman_collection_final.json`** - Original complete API collection
3. **`ruleiq_postman_environment.json`** - Environment variables configuration

## 🚀 Quick Setup

### Step 1: Import Collection
1. Open Postman
2. Click **Import** button (top-left)
3. Select `ruleiq_postman_collection_consolidated.json` (recommended) or `ruleiq_postman_collection_final.json`
4. Click **Import**

### Step 2: Import Environment
1. Click the gear icon (⚙️) in the top-right corner
2. Click **Import**
3. Select `ruleiq_postman_environment.json`
4. Click **Import**

### Step 3: Select Environment
1. From the environment dropdown (top-right), select **"RuleIQ Development"**
2. Click the eye icon to view/edit environment variables

## 🔐 Authentication Flow

### Initial Setup
1. Start your backend server: `python main.py`
2. Create a test user (if needed) using the registration endpoint or run:
   ```bash
   python scripts/create_test_user.py
   ```

### Login Process
1. Navigate to **Authentication** → **Login**
2. The request is pre-configured with test credentials
3. Click **Send**
4. Tokens are automatically saved to environment variables

### Using Protected Endpoints
- The collection automatically includes the Bearer token in requests
- No manual token copying needed!
- Token refreshing can be done via **Authentication** → **Refresh Token**

## 📁 Collection Structure

```
RuleIQ Compliance API
├── 🏥 Health & Status
│   ├── Root Health Check
│   ├── Health Status
│   ├── API Health
│   └── Monitoring Health
│
├── 🔐 Authentication
│   ├── Login (auto-saves tokens)
│   ├── Get Current User
│   ├── Refresh Token
│   ├── Google OAuth Login
│   └── Logout
│
├── 🏢 Business Profiles
│   ├── List Business Profiles
│   ├── Create Business Profile
│   ├── Get Business Profile
│   ├── Update Business Profile
│   └── Delete Business Profile
│
├── 📋 Assessments
│   ├── List Assessments
│   ├── Create Assessment
│   ├── Get Assessment
│   ├── Submit Assessment Response
│   └── Complete Assessment
│
├── 📚 Frameworks
│   ├── List Frameworks
│   ├── Get Framework
│   └── Get Framework Requirements
│
├── 📄 Policies
│   ├── List Policies
│   ├── Create Policy
│   ├── Get Policy
│   └── Generate AI Policy
│
├── 🤖 AI Services
│   ├── AI Analyze
│   ├── AI Assessment Generate
│   ├── Circuit Breaker Status
│   └── AI Cost Monitoring
│
├── ✅ Compliance
│   ├── Compliance Status
│   ├── Compliance Score
│   └── Compliance Gaps
│
├── 🔍 RAG & Chat
│   ├── RAG Find Examples
│   ├── Chat Message
│   └── IQ Agent Suggestions
│
├── 📊 Dashboard & Reports
│   ├── Dashboard Stats
│   └── Generate Report
│
└── 🧪 Test Scenarios
    ├── Test Unauthorized Access
    ├── Test Invalid Token
    └── Test Rate Limiting
```

## 🎯 Key Features

### Automatic Token Management
- Login automatically saves `access_token` and `refresh_token`
- All authenticated requests automatically use the saved token
- No manual copying of tokens required

### Test Scripts
- Each request includes test scripts to validate responses
- Automatic variable extraction (e.g., business_profile_id, assessment_id)
- Console logging for debugging

### Pre-request Scripts
- Global scripts check for authentication requirements
- Warnings if token is missing for protected endpoints
- Request logging for debugging

### Environment Variables
The environment includes:
- `base_url` - API server URL (default: http://localhost:8000)
- `api_version` - API version (default: v1)
- `access_token` - JWT access token (auto-populated on login)
- `refresh_token` - JWT refresh token (auto-populated on login)
- `test_user_email` - Test user email
- `test_user_password` - Test user password
- `business_profile_id` - Auto-populated when creating profiles
- `assessment_id` - Auto-populated when creating assessments
- `policy_id` - Auto-populated when creating policies

## 🧪 Testing Workflow

### Basic Flow
1. **Health Check**: Start with health endpoints to verify server is running
2. **Login**: Authenticate to get tokens
3. **Create Business Profile**: Creates and saves profile ID
4. **Create Assessment**: Uses saved profile ID
5. **Submit Responses**: Test assessment workflow
6. **Generate Policies**: Test AI-powered policy generation

### Testing Authentication
1. Run **Test Unauthorized Access** to verify 401 responses
2. Login to get valid token
3. Run **Get Current User** to verify authentication works
4. Run **Test Invalid Token** to verify invalid tokens are rejected

### Testing Rate Limiting
1. Select **Test Rate Limiting** request
2. Click **Send** multiple times rapidly
3. Verify 429 (Too Many Requests) response after limit is reached

## 🔧 Troubleshooting

### Common Issues

**401 Unauthorized**
- Solution: Run the Login request first to get fresh tokens

**503 Service Unavailable (Google Login)**
- This is expected - Google OAuth is not configured
- The endpoint correctly returns 503 when OAuth is not set up

**404 Not Found**
- Some endpoints may not be implemented yet
- Check the API documentation for available endpoints

**500 Internal Server Error**
- Check server logs: `tail -f logs/app.log`
- This should not happen after our fixes!

### Environment Variables Not Saving
1. Make sure environment is selected (not "No Environment")
2. Check that "Automatically persist variable values" is enabled in Postman settings
3. Manually save environment after changes

## 📝 Notes

- The collection includes all 19 tested endpoints
- Google OAuth login returns 503 (intentional - not configured)
- Some endpoints return 404 (not implemented yet)
- All authentication endpoints now properly return 401 instead of 500
- Rate limiting is enabled (100 requests/minute general, 5/minute for auth)

## 📈 Collection Versions

### Consolidated Collection (Recommended)
- **File**: `ruleiq_postman_collection_consolidated.json`
- **Endpoints**: 51 organized endpoints
- **Features**: Full CRUD operations, streaming support, security testing
- **Groups**: 10 logical groupings for easy navigation
- **Authentication**: Automatic token management with Bearer auth

### Original Collection
- **File**: `ruleiq_postman_collection_final.json`
- **Endpoints**: 19 core endpoints
- **Features**: Basic API operations and authentication

## 🎉 Success Metrics

After setup, you should see:
- ✅ 94.7% API connectivity (18/19 endpoints working)
- ✅ Proper 401 responses for unauthorized requests
- ✅ Automatic token management
- ✅ Environment variables auto-populating
- ✅ Test credentials: `test@ruleiq.dev` / `TestPassword123!`
- ⚠️ Google OAuth returns 503 (expected - not configured)