# OAuth2 Authentication Flow - Comprehensive Test Plan

## Overview
This test plan covers comprehensive testing of the OAuth2 authentication flow for the ruleIQ application running at http://localhost:3000.

## Test Environment
- Frontend: http://localhost:3000 (Next.js 15)
- Backend API: http://localhost:8000 (FastAPI)
- Authentication: JWT-based OAuth2 with refresh tokens
- Storage: Local storage with Zustand persistence

## Test Categories

### 1. Login Flow Tests
**Objective**: Verify complete login functionality with OAuth2 token handling

#### Test Cases:
1. **Successful Login with Valid Credentials**
   - Navigate to login page
   - Enter valid email/password
   - Verify token storage
   - Verify redirect to dashboard
   - Verify user state persistence

2. **Failed Login with Invalid Credentials**
   - Enter invalid credentials
   - Verify error message display
   - Verify no token storage
   - Verify no redirect occurs

3. **Form Validation**
   - Test empty email field
   - Test invalid email format
   - Test empty password field
   - Verify validation messages

4. **Loading States**
   - Verify loading indicator during login
   - Verify form disable during request

### 2. Token Management Tests
**Objective**: Verify OAuth2 token handling, storage, and refresh

#### Test Cases:
1. **Token Storage and Retrieval**
   - Login successfully
   - Verify access_token in localStorage
   - Verify refresh_token in localStorage
   - Verify token expiration handling

2. **Token Refresh Flow**
   - Simulate expired access token
   - Verify automatic refresh attempt
   - Verify new tokens stored
   - Verify seamless user experience

3. **Token Security**
   - Verify tokens are properly formatted
   - Verify secure storage mechanisms
   - Verify no token leakage in console/network

### 3. Protected Route Access Tests
**Objective**: Verify route protection and AuthGuard functionality

#### Test Cases:
1. **Authenticated User Access**
   - Login successfully
   - Navigate to protected routes
   - Verify access granted
   - Verify no redirects

2. **Unauthenticated User Redirect**
   - Clear authentication state
   - Attempt to access protected routes
   - Verify redirect to login
   - Verify redirect parameter preservation

3. **Session Persistence**
   - Login successfully
   - Refresh browser page
   - Verify authentication state persists
   - Verify no re-login required

### 4. Logout Flow Tests
**Objective**: Verify complete logout functionality

#### Test Cases:
1. **Manual Logout**
   - Login successfully
   - Click logout button
   - Verify tokens cleared from storage
   - Verify redirect to login page
   - Verify user state cleared

2. **Session Cleanup**
   - Verify all stored user data cleared
   - Verify API calls include logout endpoint
   - Verify subsequent protected route access denied

### 5. User State Management Tests
**Objective**: Verify user state consistency and updates

#### Test Cases:
1. **User Data Persistence**
   - Login successfully
   - Verify user data available in store
   - Verify user data persists across page refreshes
   - Verify user data format and completeness

2. **Authentication State Sync**
   - Verify isAuthenticated flag accuracy
   - Verify loading states consistency
   - Verify error state handling

### 6. Error Handling Tests
**Objective**: Verify comprehensive error handling

#### Test Cases:
1. **Network Errors**
   - Simulate network failures
   - Verify error messages displayed
   - Verify graceful degradation

2. **API Errors**
   - Test 401 (Unauthorized)
   - Test 403 (Forbidden)
   - Test 422 (Validation Error)
   - Test 500 (Server Error)

3. **Timeout Handling**
   - Simulate slow API responses
   - Verify timeout mechanisms
   - Verify user feedback

## Test Data

### Valid Test Credentials
- Email: test@example.com
- Password: password123

### Invalid Test Credentials
- Email: invalid@example.com
- Password: wrongpassword

## Expected Results

### Successful Authentication Flow:
1. Login form accepts valid credentials
2. API returns access_token and refresh_token
3. Tokens stored securely in localStorage
4. User redirected to dashboard
5. Protected routes accessible
6. User state persists across page refreshes

### Security Requirements:
1. Tokens properly formatted (JWT)
2. Secure storage implementation
3. Automatic token refresh
4. Proper logout cleanup
5. Protected route enforcement

## Test Execution Checklist

- [ ] Frontend server running (localhost:3000)
- [ ] Backend API server running (localhost:8000)
- [ ] Test credentials available
- [ ] Browser dev tools ready for inspection
- [ ] Network tab monitoring enabled
- [ ] Local storage inspection ready

## Browser Testing Notes
- Test in Chrome/Chromium for dev tools access
- Monitor Network tab for API calls
- Check Application tab for localStorage
- Monitor Console for errors/warnings
- Test both desktop and mobile viewports