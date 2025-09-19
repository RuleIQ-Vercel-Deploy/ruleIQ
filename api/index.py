"""
Vercel serverless handler for RuleIQ API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import (
    assessments, auth, business_profiles, chat, compliance,
    evidence, frameworks, freemium, policies, readiness,
    reports, security, uk_compliance, users, rbac_auth
)
from api.routers.admin import admin_router
from config.settings import settings

# Create FastAPI app
app = FastAPI(
    title="RuleIQ API",
    version="1.0.0",
    description="Compliance automation platform API"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(assessments.router, prefix="/api/assessments", tags=["Assessments"])
app.include_router(frameworks.router, prefix="/api/frameworks", tags=["Frameworks"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(policies.router, prefix="/api/policies", tags=["Policies"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(freemium.router, prefix="/api/freemium", tags=["Freemium"])
app.include_router(business_profiles.router, prefix="/api/business-profiles", tags=["Business Profiles"])
app.include_router(readiness.router, prefix="/api/readiness", tags=["Readiness"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(uk_compliance.router, prefix="/api/uk-compliance", tags=["UK Compliance"])
app.include_router(rbac_auth.router, prefix="/api/rbac", tags=["RBAC"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
def read_root():
    return {"message": "RuleIQ API is running on Vercel"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Vercel expects 'app' as the handler
handler = app