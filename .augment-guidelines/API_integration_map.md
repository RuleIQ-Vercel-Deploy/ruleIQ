# ruleIQ API Endpoints Reference

## Authentication
- POST /api/auth/register
- POST /api/auth/token
- POST /api/auth/login
- POST /api/auth/refresh
- GET /api/users/me

## Core Features
- Business Profiles: /api/business-profiles/*
- Assessments: /api/assessments/*
- Evidence: /api/evidence/*
- Policies: /api/policies/*
- Chat: /api/chat/*
- Integrations: /api/integrations/*

## Response Format
Success: { data: {...}, message: "Success", status: 200 }
Error: { detail: "Error message", status: 400 }
Paginated: { items: [...], total: 100, page: 1, size: 20 }

## Authentication
- Use Bearer token in Authorization header
- Store tokens securely (httpOnly cookies preferred)
- Implement token refresh logic