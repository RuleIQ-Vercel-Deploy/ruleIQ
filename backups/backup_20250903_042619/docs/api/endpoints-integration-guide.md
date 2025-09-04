# API Endpoints Summary - Frontend Integration Guide

## ✅ Working Endpoints

### Authentication
- **POST** `/api/v1/auth/login`
  - Request: `{ "email": "test@ruleiq.dev", "password": "TestPassword123!" }`
  - Response: `{ "access_token": "...", "token_type": "bearer" }`
  - Status: ✅ Working

- **POST** `/api/v1/auth/register`
  - Request: `{ "email": "user@example.com", "password": "SecurePass123!" }`
  - Response: `{ "user": {...}, "tokens": { "access_token": "...", "refresh_token": "..." } }`
  - Status: ✅ Working

### Business Profiles
- **GET** `/api/v1/business-profiles/`
  - Headers: `Authorization: Bearer {token}`
  - Response: Business profile object or 404 if not created
  - Status: ✅ Working

- **POST** `/api/v1/business-profiles/`
  - Headers: `Authorization: Bearer {token}`
  - Request: 
    ```json
    {
      "company_name": "string",
      "industry": "string",
      "employee_count": 10,  // REQUIRED
      "handles_personal_data": false,
      "processes_payments": false,
      "stores_health_data": false,
      "provides_financial_services": false,
      "operates_critical_infrastructure": false,
      "has_international_operations": false
    }
    ```
  - Status: ✅ Working

### Frameworks
- **GET** `/api/v1/frameworks/`
  - Headers: `Authorization: Bearer {token}`
  - Response: Array of framework objects
  - Status: ✅ Working (Returns 10 frameworks)

- **GET** `/api/v1/frameworks/all-public`
  - Headers: `Authorization: Bearer {token}`
  - Response: Array of all public frameworks
  - Status: ✅ Working

## ⚠️ Endpoints Needing Attention

### Framework Recommendations
- **GET** `/api/v1/frameworks/recommendations`
  - Status: ❌ Returns 500 error
  - Issue: Internal server error, needs backend fix

## Frontend Integration Checklist

### 1. Authentication Flow
- [ ] Store the `access_token` from login/register response
- [ ] Include `Authorization: Bearer {token}` header in all requests
- [ ] Handle 401 responses by redirecting to login

### 2. Business Profile Flow
- [ ] Check if user has profile (GET `/api/v1/business-profiles/`)
- [ ] If 404, show profile creation form
- [ ] Include `employee_count` as required field (integer)
- [ ] Use correct field names (e.g., `handles_personal_data` not `handles_persona`)

### 3. Frameworks Flow
- [ ] Use `/api/v1/frameworks/` for user-specific frameworks
- [ ] Use `/api/v1/frameworks/all-public` for all available frameworks
- [ ] Framework recommendations endpoint needs backend fix

## Test Credentials
- Email: `test@ruleiq.dev`
- Password: `TestPassword123!`

## Common Issues & Solutions

### Issue: 403 Forbidden
**Solution**: Ensure Authorization header is included with Bearer token

### Issue: 422 Validation Error
**Solution**: Check required fields, especially `employee_count` for business profiles

### Issue: 404 on business-profiles
**Solution**: Normal for new users - they need to create a profile first

## API Base URL
- Development: `http://localhost:8000`
- All endpoints prefix: `/api/v1/`

## Testing Scripts

The following scripts are available in the `scripts/` directory for API testing:

- **`scripts/test_api_endpoints_integration.py`** - Comprehensive API endpoint testing
- **`scripts/create_test_user.py`** - Create/update test user credentials
- **`scripts/test_api_connections.py`** - Basic API connectivity tests

Run with: `source .venv/bin/activate && python scripts/[script_name].py`

## Next Steps for Frontend
1. Update API client to use correct endpoints
2. Ensure all requests include Authorization header
3. Handle profile creation flow for new users
4. Update field names to match schema (especially for business profiles)