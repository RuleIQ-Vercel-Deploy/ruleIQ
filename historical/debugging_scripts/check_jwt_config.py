#!/usr/bin/env python3
"""
JWT Configuration Checker
Checks for common JWT configuration issues
"""

import os
import re
from pathlib import Path

print("JWT Configuration Check")
print("="*50)

# Check 1: Environment files
env_files = [".env", ".env.local", ".env.test", "env.template"]
jwt_vars_found = {}

for env_file in env_files:
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            
        # Look for any JWT-related variables
        jwt_patterns = [
            r'^(JWT_SECRET)\s*=\s*(.*)$',
            r'^(JWT_SECRET_KEY)\s*=\s*(.*)$',
            r'^(SECRET_KEY)\s*=\s*(.*)$'
        ]
        
        for pattern in jwt_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                for var_name, var_value in matches:
                    if env_file not in jwt_vars_found:
                        jwt_vars_found[env_file] = []
                    # Strip quotes if present
                    var_value = var_value.strip()
                    if (var_value.startswith('"') and var_value.endswith('"')) or \
                       (var_value.startswith("'") and var_value.endswith("'")):
                        var_value = var_value[1:-1]
                    jwt_vars_found[env_file].append((var_name, var_value[:20] + "..."))

# Display results
print("\nEnvironment Files Check:")
for env_file, vars_found in jwt_vars_found.items():
    print(f"\n{env_file}:")
    for var_name, var_value in vars_found:
        print(f"  {var_name} = {var_value}")

if not jwt_vars_found:
    print("\n✗ No JWT-related variables found in any environment files!")

# Check 2: What the code expects
print("\n\nCode Expectations:")
print("- config/settings.py expects: JWT_SECRET")
print("- Default value: 'dev-secret-key-change-in-production'")

# Check 3: Current environment
print("\n\nCurrent Environment Variables:")
env_vars = ["JWT_SECRET", "JWT_SECRET_KEY", "SECRET_KEY"]
for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"✓ {var} is set (length: {len(value)})")
    else:
        print(f"✗ {var} is NOT set")

# Check 4: Recommendations
print("\n\nRecommendations:")
print("1. Ensure .env.local contains: JWT_SECRET=your-actual-secret-here")
print("2. Do NOT use JWT_SECRET_KEY (that's a different variable)")
print("3. The secret should be at least 32 characters long")
print("4. Don't include quotes in the .env file unless they're part of the secret")
print("5. Restart the server after changing environment variables")

# Check 5: Test token creation
print("\n\nTesting Token Creation:")
try:
    from jose import jwt
    from datetime import datetime, timedelta
    
    # Try with current environment
    test_secret = os.getenv("JWT_SECRET", "dev-jwt-secret-key-change-for-production")
    payload = {"sub": "test", "exp": datetime.utcnow() + timedelta(minutes=5)}
    
    token = jwt.encode(payload, test_secret, algorithm="HS256")
    decoded = jwt.decode(token, test_secret, algorithms=["HS256"])
    
    print(f"✓ Token creation/verification works with current setup")
    print(f"  Using secret: {test_secret[:10]}...")
except ImportError:
    print("✗ python-jose not installed")
    print("  Install with: pip install python-jose[cryptography]")
except Exception as e:
    print(f"✗ Token creation failed: {e}")
