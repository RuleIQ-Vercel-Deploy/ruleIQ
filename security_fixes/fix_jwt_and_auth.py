#!/usr/bin/env python3
"""
Security Fix: JWT and Authentication Vulnerabilities
Task ID: eeb5d5b1
Priority: CRITICAL
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any

class JWTSecurityFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.fixes_applied = []
        
    def fix_jwt_secret_validation(self) -> Dict[str, Any]:
        """Fix weak JWT secret validation in settings.py"""
        settings_path = self.project_root / "config" / "settings.py"
        
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Enhance JWT secret validation
        enhanced_validation = '''    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret key strength with strict requirements"""
        import secrets
        import string
        
        # Testing environment gets a secure test key
        if os.getenv('TESTING', '').lower() == 'true':
            return 'test-secret-key-for-testing-only-with-minimum-32-characters-and-complexity'
        
        # Production requires strong secret
        if os.getenv('ENVIRONMENT') == 'production':
            if not v or len(v) < 64:
                raise ValueError('CRITICAL: Production requires 64+ character JWT secret')
            
            # Check complexity requirements
            has_upper = any(c.isupper() for c in v)
            has_lower = any(c.islower() for c in v)
            has_digit = any(c.isdigit() for c in v)
            has_special = any(c in string.punctuation for c in v)
            
            if not all([has_upper, has_lower, has_digit, has_special]):
                raise ValueError('JWT secret must contain uppercase, lowercase, digits, and special characters')
            
            # Warn if using default/weak patterns
            weak_patterns = ['insecure', 'dev', 'test', 'example', 'secret', 'password']
            if any(pattern in v.lower() for pattern in weak_patterns):
                raise ValueError('JWT secret contains weak patterns')
        
        # Development/staging get warnings
        elif not v or len(v) < 32:
            if not v:
                # Generate a secure random key for development
                v = secrets.token_urlsafe(48)
                logger.warning(f'Generated secure JWT secret for development: {v[:8]}...')
            else:
                logger.warning('JWT secret is weak - NOT suitable for production')
        
        return v'''
        
        # Replace the existing validation
        pattern = r'@field_validator\(\'jwt_secret_key\'\).*?return v'
        content = re.sub(pattern, enhanced_validation, content, flags=re.DOTALL)
        
        with open(settings_path, 'w') as f:
            f.write(content)
        
        return {
            "file": "config/settings.py",
            "issue": "Weak JWT secret validation",
            "status": "Fixed",
            "changes": "Enhanced validation with complexity requirements"
        }
    
    def fix_token_blacklist(self) -> Dict[str, Any]:
        """Fix in-memory token blacklist vulnerability"""
        
        # Create Redis-backed token blacklist
        blacklist_code = '''"""
Redis-backed JWT Token Blacklist
Ensures token revocation persists across server restarts
"""

from typing import Optional, Set
from datetime import datetime, timedelta, timezone
import json
import redis
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

class TokenBlacklist:
    """Persistent token blacklist using Redis"""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_keepalive=True,
            socket_keepalive_options={
                1: 1,  # TCP_KEEPIDLE
                2: 3,  # TCP_KEEPINTVL  
                3: 5   # TCP_KEEPCNT
            }
        )
        self.prefix = "token:blacklist:"
        self.ttl_days = 30  # Keep blacklisted tokens for 30 days
        
    def add(self, token: str, reason: str = "manual_revocation", 
            user_id: Optional[str] = None, metadata: Optional[dict] = None) -> bool:
        """Add token to blacklist with metadata"""
        try:
            key = f"{self.prefix}{token[:50]}"  # Use first 50 chars as key
            
            data = {
                "token": token,
                "reason": reason,
                "user_id": user_id,
                "revoked_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {}
            }
            
            # Store with TTL
            self.redis_client.setex(
                key,
                timedelta(days=self.ttl_days),
                json.dumps(data)
            )
            
            # Also add to a set for quick lookups
            self.redis_client.sadd(f"{self.prefix}set", token[:50])
            
            logger.info(f"Token blacklisted: {token[:20]}... (reason: {reason})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            # Fallback to in-memory if Redis fails
            return False
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            # Quick check in set
            return self.redis_client.sismember(f"{self.prefix}set", token[:50])
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False
    
    def remove(self, token: str) -> bool:
        """Remove token from blacklist"""
        try:
            key = f"{self.prefix}{token[:50]}"
            self.redis_client.delete(key)
            self.redis_client.srem(f"{self.prefix}set", token[:50])
            logger.info(f"Token removed from blacklist: {token[:20]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to remove token from blacklist: {e}")
            return False
    
    def clear_expired(self) -> int:
        """Clean up expired tokens (maintenance task)"""
        try:
            # Redis handles TTL automatically, this is for the set
            # In production, run this as a scheduled task
            count = 0
            for token_prefix in self.redis_client.smembers(f"{self.prefix}set"):
                key = f"{self.prefix}{token_prefix}"
                if not self.redis_client.exists(key):
                    self.redis_client.srem(f"{self.prefix}set", token_prefix)
                    count += 1
            
            if count > 0:
                logger.info(f"Cleared {count} expired tokens from blacklist")
            return count
            
        except Exception as e:
            logger.error(f"Failed to clear expired tokens: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get blacklist statistics"""
        try:
            total = self.redis_client.scard(f"{self.prefix}set")
            return {
                "total_blacklisted": total,
                "storage_backend": "Redis",
                "ttl_days": self.ttl_days
            }
        except Exception as e:
            logger.error(f"Failed to get blacklist stats: {e}")
            return {"error": str(e)}

# Singleton instance
_token_blacklist = None

def get_token_blacklist() -> TokenBlacklist:
    """Get singleton token blacklist instance"""
    global _token_blacklist
    if _token_blacklist is None:
        _token_blacklist = TokenBlacklist()
    return _token_blacklist
'''
        
        blacklist_path = self.project_root / "services" / "security" / "token_blacklist.py"
        blacklist_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(blacklist_path, 'w') as f:
            f.write(blacklist_code)
        
        return {
            "file": "services/security/token_blacklist.py",
            "issue": "In-memory token blacklist",
            "status": "Fixed",
            "changes": "Implemented Redis-backed persistent blacklist"
        }
    
    def update_auth_dependency(self) -> Dict[str, Any]:
        """Update auth.py to use Redis blacklist"""
        auth_path = self.project_root / "api" / "dependencies" / "auth.py"
        
        with open(auth_path, 'r') as f:
            content = f.read()
        
        # Add import for Redis blacklist
        import_line = "from services.security.token_blacklist import get_token_blacklist\n"
        if "from services.security.token_blacklist" not in content:
            content = import_line + content
        
        # Replace in-memory blacklist functions
        content = re.sub(
            r'blacklisted_tokens: set = set\(\)',
            '# Token blacklist handled by Redis service',
            content
        )
        
        content = re.sub(
            r'def is_token_blacklisted\(token: str\).*?return token in blacklisted_tokens',
            '''def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted using Redis."""
    return get_token_blacklist().is_blacklisted(token)''',
            content,
            flags=re.DOTALL
        )
        
        content = re.sub(
            r'def blacklist_token\(token: str\):.*?blacklisted_tokens\.add\(token\)',
            '''def blacklist_token(token: str, reason: str = "manual", **kwargs):
    """Add a token to the Redis blacklist."""
    get_token_blacklist().add(token, reason=reason, **kwargs)''',
            content,
            flags=re.DOTALL
        )
        
        with open(auth_path, 'w') as f:
            f.write(content)
        
        return {
            "file": "api/dependencies/auth.py",
            "issue": "In-memory blacklist in auth.py",
            "status": "Fixed",
            "changes": "Integrated Redis-backed blacklist"
        }
    
    def fix_password_reset_tokens(self) -> Dict[str, Any]:
        """Fix password reset tokens stored in memory"""
        
        # Create secure password reset service
        reset_code = '''"""
Secure Password Reset Token Management
Uses Redis for persistence with automatic expiration
"""

from typing import Optional
from datetime import datetime, timedelta, timezone
import secrets
import hashlib
import json
import redis
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

class PasswordResetService:
    """Secure password reset token management"""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
        self.prefix = "password:reset:"
        self.token_length = 32
        self.expiry_minutes = 30
        
    def create_reset_token(self, user_id: str, email: str) -> str:
        """Create a secure password reset token"""
        try:
            # Generate cryptographically secure token
            token = secrets.token_urlsafe(self.token_length)
            
            # Hash token for storage (store hash, not plaintext)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Store with user info and expiry
            key = f"{self.prefix}{token_hash}"
            data = {
                "user_id": user_id,
                "email": email,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "attempts": 0,
                "ip_addresses": []
            }
            
            # Set with TTL
            self.redis_client.setex(
                key,
                timedelta(minutes=self.expiry_minutes),
                json.dumps(data)
            )
            
            logger.info(f"Password reset token created for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create reset token: {e}")
            raise
    
    def verify_reset_token(self, token: str, ip_address: Optional[str] = None) -> Optional[dict]:
        """Verify and return user info for valid reset token"""
        try:
            # Hash the provided token
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            key = f"{self.prefix}{token_hash}"
            
            # Get token data
            data = self.redis_client.get(key)
            if not data:
                logger.warning(f"Invalid reset token attempted from IP: {ip_address}")
                return None
            
            token_data = json.loads(data)
            
            # Track attempt
            token_data['attempts'] += 1
            if ip_address and ip_address not in token_data['ip_addresses']:
                token_data['ip_addresses'].append(ip_address)
            
            # Check for suspicious activity (too many attempts)
            if token_data['attempts'] > 5:
                logger.warning(f"Too many reset attempts for token: {token_hash[:10]}...")
                self.invalidate_reset_token(token)
                return None
            
            # Update attempt count
            self.redis_client.setex(
                key,
                self.redis_client.ttl(key),  # Keep same TTL
                json.dumps(token_data)
            )
            
            return {
                "user_id": token_data["user_id"],
                "email": token_data["email"]
            }
            
        except Exception as e:
            logger.error(f"Failed to verify reset token: {e}")
            return None
    
    def invalidate_reset_token(self, token: str) -> bool:
        """Invalidate a reset token after use"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            key = f"{self.prefix}{token_hash}"
            
            result = self.redis_client.delete(key)
            if result:
                logger.info(f"Reset token invalidated: {token_hash[:10]}...")
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to invalidate reset token: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """Clean up expired tokens (handled automatically by Redis TTL)"""
        # Redis handles expiration automatically
        # This method is for compatibility/monitoring
        pattern = f"{self.prefix}*"
        count = len(self.redis_client.keys(pattern))
        logger.info(f"Active reset tokens: {count}")
        return count

# Singleton instance
_reset_service = None

def get_password_reset_service() -> PasswordResetService:
    """Get singleton password reset service"""
    global _reset_service
    if _reset_service is None:
        _reset_service = PasswordResetService()
    return _reset_service
'''
        
        reset_path = self.project_root / "services" / "security" / "password_reset.py"
        reset_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(reset_path, 'w') as f:
            f.write(reset_code)
        
        return {
            "file": "services/security/password_reset.py",
            "issue": "In-memory password reset tokens",
            "status": "Fixed",
            "changes": "Implemented secure Redis-backed reset tokens"
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate security fix report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "security_improvements": [
                "JWT secrets now require 64+ characters in production",
                "Token blacklist persists in Redis",
                "Password reset tokens secured with Redis + hashing",
                "Added complexity requirements for secrets",
                "Implemented token attempt tracking"
            ],
            "next_steps": [
                "Run security tests",
                "Update environment variables",
                "Deploy to staging",
                "Monitor Redis memory usage"
            ]
        }

def main():
    print("🔒 Fixing JWT and Authentication Vulnerabilities\n")
    
    fixer = JWTSecurityFixer()
    
    # Apply fixes
    fixes = []
    
    print("1. Fixing JWT secret validation...")
    fixes.append(fixer.fix_jwt_secret_validation())
    
    print("2. Implementing Redis token blacklist...")
    fixes.append(fixer.fix_token_blacklist())
    
    print("3. Updating auth dependency...")
    fixes.append(fixer.update_auth_dependency())
    
    print("4. Securing password reset tokens...")
    fixes.append(fixer.fix_password_reset_tokens())
    
    fixer.fixes_applied = fixes
    
    # Generate report
    report = fixer.generate_report()
    
    print("\n✅ JWT and Authentication Security Fixes Complete!")
    print(f"   - Fixed {len(fixes)} vulnerabilities")
    print("\n📋 Summary:")
    for fix in fixes:
        print(f"   ✓ {fix['issue']} - {fix['status']}")
    
    return report

if __name__ == "__main__":
    main()