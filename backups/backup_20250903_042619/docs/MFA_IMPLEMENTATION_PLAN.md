# Multi-Factor Authentication (MFA) Implementation Plan

## Overview

This document outlines the implementation plan for Multi-Factor Authentication (MFA) in the ruleIQ platform, addressing the TODO item in `api/middleware/rbac_config.py`.

## Phase 1: Infrastructure Setup ✅ READY

### Database Schema Extensions
- Add MFA-related tables:
  - `user_mfa_settings` (user preferences, enabled methods)
  - `user_mfa_tokens` (TOTP secrets, backup codes)
  - `user_mfa_sessions` (MFA verification sessions)

### Configuration Updates ✅ COMPLETED
- Updated RBAC security policies with MFA configuration
- Added MFA method preferences
- Added backup code support configuration

## Phase 2: Implementation Components

### 2.1 TOTP (Time-based One-Time Passwords)
**Priority**: High
**Estimated Effort**: 2-3 days

**Components:**
- TOTP secret generation using `pyotp`
- QR code generation for authenticator apps
- TOTP validation middleware
- Recovery code generation (10 single-use codes)

**Implementation Points:**
- `services/mfa_service.py` - Core MFA logic
- `api/routers/mfa.py` - MFA endpoints
- `api/middleware/mfa_middleware.py` - Request validation

### 2.2 SMS-based MFA
**Priority**: Medium
**Estimated Effort**: 1-2 days

**Dependencies:**
- SMS provider integration (Twilio/AWS SNS)
- Phone number verification
- Rate limiting for SMS codes

**Implementation:**
- 6-digit SMS codes with 5-minute expiration
- Anti-fraud measures (rate limiting, phone validation)

### 2.3 Frontend Integration
**Priority**: High
**Estimated Effort**: 2-3 days

**Components:**
- MFA setup wizard
- TOTP QR code display
- MFA challenge forms
- Backup code display/download
- Account recovery flows

## Phase 3: Security Enhancements

### 3.1 Risk-Based Authentication
- Device fingerprinting
- IP geolocation analysis
- Behavioral pattern detection
- Conditional MFA requirements

### 3.2 Administrative Controls
- Force MFA enrollment for admin roles
- MFA audit logging
- Emergency MFA bypass (with audit trail)
- Bulk MFA enforcement policies

## Implementation Timeline

### Week 1: Database & Core Services
- [ ] Database schema migration
- [ ] MFA service implementation
- [ ] TOTP integration with `pyotp`

### Week 2: API & Middleware
- [ ] MFA API endpoints
- [ ] Authentication middleware updates  
- [ ] Admin enforcement logic

### Week 3: Frontend & Testing
- [ ] MFA setup UI components
- [ ] Challenge/response flows
- [ ] Comprehensive testing suite

### Week 4: Security Hardening
- [ ] Rate limiting implementation
- [ ] Audit logging integration
- [ ] Security testing & penetration testing

## Security Considerations

### TOTP Implementation
- Secrets stored encrypted in database
- Rate limiting: 3 attempts per 30 seconds
- Window tolerance: ±1 time step (30 seconds)
- Backup codes: 10 single-use, encrypted storage

### Session Management
- MFA verification creates secure session flag
- Re-challenge for sensitive operations
- Session invalidation on logout
- Cross-device session management

### Recovery Mechanisms
- Backup codes for TOTP recovery
- Admin-assisted recovery process
- Account recovery audit trail
- Emergency bypass procedures

## Database Schema

```sql
-- MFA Settings per user
CREATE TABLE user_mfa_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    totp_enabled BOOLEAN DEFAULT FALSE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    phone_number VARCHAR(20),
    backup_codes_generated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- TOTP secrets and backup codes
CREATE TABLE user_mfa_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    token_type VARCHAR(20) NOT NULL, -- 'totp_secret', 'backup_code'
    encrypted_value TEXT NOT NULL,
    used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- MFA verification sessions
CREATE TABLE user_mfa_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    session_token VARCHAR(255) NOT NULL,
    method_used VARCHAR(20) NOT NULL, -- 'totp', 'sms', 'backup_code'
    verified_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    ip_address INET,
    user_agent TEXT
);
```

## API Endpoints

### Setup Endpoints
- `POST /auth/mfa/setup/totp` - Generate TOTP secret and QR
- `POST /auth/mfa/setup/sms` - Setup SMS MFA
- `POST /auth/mfa/verify-setup` - Verify initial MFA setup

### Authentication Endpoints  
- `POST /auth/mfa/challenge` - Request MFA challenge
- `POST /auth/mfa/verify` - Verify MFA response
- `GET /auth/mfa/backup-codes` - Generate backup codes

### Management Endpoints
- `GET /auth/mfa/status` - Get user MFA status
- `DELETE /auth/mfa/disable` - Disable MFA (with verification)
- `POST /auth/mfa/reset` - Admin MFA reset

## Integration Points

### Current Authentication Flow
1. User login with username/password ✅ Existing
2. **NEW**: Check if MFA required for user/role
3. **NEW**: Present MFA challenge if required
4. **NEW**: Verify MFA response
5. Issue JWT token with MFA verification flag ✅ Existing pattern

### Middleware Integration
```python
# In api/middleware/auth_middleware.py
async def require_mfa_verification(request: Request):
    """Middleware to enforce MFA for sensitive operations"""
    if not request.state.user.mfa_verified:
        if rbac_config.requires_mfa(request.state.user.role):
            raise HTTPException(403, "MFA verification required")
```

## Testing Strategy

### Unit Tests
- TOTP generation and validation
- Backup code generation/validation
- SMS code generation
- Database operations

### Integration Tests  
- Complete MFA setup flow
- Authentication with MFA
- Recovery scenarios
- Admin enforcement

### Security Tests
- Rate limiting effectiveness
- Time window attacks
- Backup code enumeration
- Session fixation

## Compliance Impact

### SOC 2 Type II Benefits
- Enhanced access controls (CC6.1)
- Multi-factor authentication (CC6.2) 
- Session management (CC6.3)

### ISO 27001 Benefits
- Access control policy (A.9.1)
- User access management (A.9.2)
- Authentication information management (A.9.4)

## Deployment Strategy

### Phase 2 Rollout
1. **Soft Launch**: Optional MFA for all users
2. **Admin Enforcement**: Required MFA for admin roles
3. **Gradual Rollout**: Required MFA for business users
4. **Full Enforcement**: MFA required for all users

### Rollback Plan
- Feature flags for MFA enforcement
- Database rollback scripts
- Emergency MFA bypass capability
- User communication strategy

## Success Metrics

### Security Metrics
- MFA adoption rate (target: 90%+)
- Successful authentications with MFA
- Failed MFA attempts (fraud detection)
- Account recovery requests

### User Experience Metrics
- MFA setup completion rate
- Average setup time
- Support tickets related to MFA
- User satisfaction scores

---

**Status**: Planning Complete - Ready for Implementation
**Next Action**: Database schema implementation
**Priority**: Medium-High (Security Enhancement)
**Risk Level**: Low (well-established patterns)