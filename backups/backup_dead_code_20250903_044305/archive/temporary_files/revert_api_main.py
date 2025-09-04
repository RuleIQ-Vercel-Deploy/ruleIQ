#!/usr/bin/env python3
"""Revert api/main.py to simpler approach"""
import logging
logger = logging.getLogger(__name__)


# Read the current main.py
with open("api/main.py", "r") as f:
    content = f.read()

# Remove the api_v1 sub-application approach
content = content.replace(
    """# Create a sub-application for API v1 with docs
api_v1 = FastAPI(
    title="ruleIQ API v1",
    description="AI-powered compliance and risk management platform - API v1",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json"
)

# Configure CORS for API v1
api_v1.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Rate-Limit-Remaining"]
)

""",
    "",
)

# Revert router includes back to main app
content = content.replace(
    "# Include all routers in API v1\napi_v1.include_router",
    "# Include all routers\napp.include_router",
)
content = content.replace("api_v1.include_router", "app.include_router")
content = content.replace('prefix="/auth"', 'prefix="/api/v1/auth"')
content = content.replace('prefix="/users"', 'prefix="/api/v1/users"')
content = content.replace('prefix="/assessments"', 'prefix="/api/v1/assessments"')
content = content.replace('prefix="/ai-assessments"', 'prefix="/api/v1/ai-assessments"')
content = content.replace(
    'prefix="/ai-optimization"', 'prefix="/api/v1/ai-optimization"'
)
content = content.replace(
    'prefix="/business-profiles"', 'prefix="/api/v1/business-profiles"'
)
content = content.replace('prefix="/chat"', 'prefix="/api/v1/chat"')
content = content.replace('prefix="/compliance"', 'prefix="/api/v1/compliance"')
content = content.replace('prefix="/evidence"', 'prefix="/api/v1/evidence"')
content = content.replace(
    'prefix="/evidence-collection"', 'prefix="/api/v1/evidence-collection"'
)
content = content.replace(
    'prefix="/foundation-evidence"', 'prefix="/api/v1/foundation-evidence"'
)
content = content.replace('prefix="/frameworks"', 'prefix="/api/v1/frameworks"')
content = content.replace('prefix="/implementation"', 'prefix="/api/v1/implementation"')
content = content.replace('prefix="/integrations"', 'prefix="/api/v1/integrations"')
content = content.replace('prefix="/monitoring"', 'prefix="/api/v1/monitoring"')
content = content.replace('prefix="/policies"', 'prefix="/api/v1/policies"')
content = content.replace('prefix="/readiness"', 'prefix="/api/v1/readiness"')
content = content.replace('prefix="/reporting"', 'prefix="/api/v1/reporting"')
content = content.replace('prefix="/security"', 'prefix="/api/v1/security"')

# Remove the mount line
content = content.replace(
    '\n# Mount API v1 sub-application\napp.mount("/api/v1", api_v1)', ""
)

# Write back
with open("api/main.py", "w") as f:
    f.write(content)

logger.info("Reverted to simpler approach")
