# JWT Authentication Issue - Root Cause and Solution

## The Real Problem

After analyzing the code changes, I found the actual issues that prevented the JWT authentication from working:

### 1. **Critical Bug: Hardcoded JWT Secret in api/auth.py**
I accidentally added this line that overrides the environment variable:
```python
settings.jwt_secret = "dev-jwt-secret-key-change-for-production"
```
This forces the server to always use the hardcoded secret, ignoring the actual JWT_SECRET from the environment.

### 2. **JWT Library Mismatch**
- Server uses: `from jose import jwt` (python-jose library)
- Original test used: `import jwt` (PyJWT library)
- These libraries can produce incompatible tokens

### 3. **Possible Environment Variable Name Mismatch**
- The code expects: `JWT_SECRET`
- The env.template shows: `JWT_SECRET_KEY`
- If .env.local uses the wrong variable name, the secret won't load

## The Solution

I've created several scripts to diagnose and fix the issue:

### 1. **check_jwt_config.py** - Diagnostic Tool
Run this first to check your configuration:
```bash
python check_jwt_config.py
```

This will:
- Check all .env files for JWT variables
- Show what variable names are being used
- Verify if JWT_SECRET is in the current environment
- Test token creation with current settings

### 2. **simple_jwt_test.py** - Minimal Test Script
A clean test that uses the correct library:
```bash
python simple_jwt_test.py
```

### 3. **verify_jwt_fix.py** - Complete Verification
A comprehensive script that:
- Kills existing servers
- Starts a fresh server
- Tests authentication
- Provides clear success/failure feedback

```bash
python verify_jwt_fix.py
```

## Manual Fix Steps

1. **Ensure .env.local has the correct variable:**
   ```
   JWT_SECRET=your-actual-secret-key-here
   ```
   (NOT JWT_SECRET_KEY)

2. **Remove the hardcoded secret from api/auth.py** (I've already fixed this)

3. **Install python-jose if needed:**
   ```bash
   pip install python-jose[cryptography]
   ```

4. **Restart the server cleanly:**
   ```bash
   pkill -f uvicorn
   uvicorn api.main:app --reload
   ```

5. **Run the test:**
   ```bash
   python simple_jwt_test.py
   ```

## Common Issues

1. **Wrong variable name**: Make sure it's `JWT_SECRET`, not `JWT_SECRET_KEY`
2. **Quotes in .env file**: Don't wrap the secret in quotes unless they're part of the value
3. **Server caching**: Always kill and restart the server after changes
4. **Missing library**: Ensure python-jose[cryptography] is installed

## Verification

The authentication is working when:
- The `/debug/config` endpoint shows the correct JWT secret
- The test script returns a 200 status code
- You see "Authentication successful!" in the output

## Important Note

The `/debug/config` endpoint I added should be **removed before production** as it reveals partial JWT secret information.
