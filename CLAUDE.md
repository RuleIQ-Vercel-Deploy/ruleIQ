# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComplianceGPT is an AI-powered compliance automation platform for UK SMBs. The system guides businesses through compliance scoping, generates policies, creates implementation plans, tracks evidence collection, and provides readiness assessments.

## Architecture

The project follows a service-oriented architecture with clear separation between database models and business logic:

- **Database Layer**: SQLAlchemy models in `/database/` define entities like business profiles, compliance frameworks, assessment sessions, and evidence items
- **Service Layer**: Business logic in `/services/` provides authenticated and public functions for each domain
- **Data Models**: Uses PostgreSQL with SQLAlchemy, configured in `database/db_setup.py`

### Key Architecture Patterns

- Services use `@authenticated` and `@public` decorators from the `sql-alchemy.access` framework
- Database models inherit from SQLAlchemy Base and use PostgreSQL-specific types (UUID, JSONB)
- Business logic is encapsulated in service functions that handle CRUD operations and domain-specific workflows
- All services import from `core.*` modules (likely external framework components)

### Core User Flows

1. **Onboarding**: Business assessment through guided questionnaire, framework recommendation
2. **Policy Generation**: AI-generated compliance policies tailored to business profile
3. **Implementation Planning**: Step-by-step plans with timelines and resource estimates
4. **Evidence Collection**: Interactive checklists with automation guidance for cloud tools
5. **Readiness Assessment**: Real-time compliance scoring and gap analysis

## Database Setup

Configure PostgreSQL connection via `DATABASE_URL` environment variable:
```
postgresql+psycopg2://username:password@localhost:5432/database_name
```

Dependencies are managed via `requirements.txt` with SQLAlchemy and PostgreSQL support.

## Development Commands

The project uses Python with SQLAlchemy. No specific build, test, or lint commands are defined in the current codebase - check with the project maintainer for the appropriate commands to run during development.

## AI Configuration

The project uses Google Generative AI (Gemini) for compliance content generation:
- Model: `gemini-2.5-flash-preview-05-20`
- Configuration located in `/config/ai_config.py`
- Requires `GOOGLE_API_KEY` environment variable

## Development Guidelines

- **Dependencies**: Never add new dependencies without explicit approval from the user
- **AI Models**: Only use the specified Gemini model for text-based compliance generation
- **File Creation**: Prefer editing existing files over creating new ones unless absolutely necessary

## Current Status - Database Setup

**PAUSED FOR COLUMN SPECIFICATIONS**

Progress completed:
- ✅ Virtual environment created and requirements installed
- ✅ AI configuration set up with Google Gemini API
- ✅ Database connection string configured for Neon
- ✅ Examined existing database models in /database/ directory
- ✅ Created core module structure to match service imports
- ✅ Created sqlalchemy_access framework to replace invalid sql-alchemy.access

Current issue:
- Services use custom ORM framework (.sql() methods) that doesn't exist
- Need column specifications from user to complete database setup

Next steps (when resumed):
1. Get column specifications for all database tables
2. Update database models with correct column names and types
3. Rewrite service functions to use standard SQLAlchemy queries
4. Test database connectivity and initialization
5. Complete database setup and run init_db.py