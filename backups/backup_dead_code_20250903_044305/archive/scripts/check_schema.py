#!/usr/bin/env python3
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Check actual database schema vs model schema.
"""
import os
import sys
from sqlalchemy import create_engine, inspect

# Set environment
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = (
    os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/compliance_test?sslmode=require")
)


def main() -> None:
    logger.info("=== Schema Comparison Analysis ===")
    """Main"""

    # Database connection
    db_url = os.environ["DATABASE_URL"]
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "+psycopg2")
    elif "postgresql://" in db_url and "+psycopg2" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    engine = create_engine(db_url, echo=False)
    inspector = inspect(engine)

    # Check assessment_leads table schema
    logger.info("1. Actual assessment_leads table schema in database:")
    columns = inspector.get_columns("assessment_leads")
    for col in columns:
        logger.info(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")

    logger.info(f"\nFound {len(columns)} columns in assessment_leads table")

    # Check what the model expects
    logger.info("\n2. AssessmentLead model expected columns:")
    sys.path.insert(0, "/home/omar/Documents/ruleIQ")

    from database.assessment_lead import AssessmentLead

    # Get model metadata
    model_table = AssessmentLead.__table__
    logger.info(f"Model table name: {model_table.name}")

    for col in model_table.columns:
        logger.info(f"  - {col.name}: {col.type} (nullable: {col.nullable})")

    logger.info(f"\nModel expects {len(model_table.columns)} columns")

    # Compare
    logger.info("\n3. Schema comparison:")
    db_columns = {col["name"] for col in columns}
    model_columns = {col.name for col in model_table.columns}

    missing_in_db = model_columns - db_columns
    extra_in_db = db_columns - model_columns

    if missing_in_db:
        logger.info("❌ Columns missing in database:")
        for col in missing_in_db:
            logger.info(f"    - {col}")

    if extra_in_db:
        logger.info("ℹ️  Extra columns in database:")
        for col in extra_in_db:
            logger.info(f"    - {col}")

    if not missing_in_db and not extra_in_db:
        logger.info("✅ Schema matches perfectly!")

    # Check other freemium tables
    freemium_tables = [
        "freemium_assessment_sessions",
        "ai_question_bank",
        "lead_scoring_events",
        "conversion_events",
    ]

    for table_name in freemium_tables:
        logger.info(f"\n4. Checking {table_name} schema:")
        try:
            columns = inspector.get_columns(table_name)
            logger.info(f"  ✅ {table_name}: {len(columns)} columns")
        except Exception as e:
            logger.info(f"  ❌ {table_name}: Error - {e}")


if __name__ == "__main__":
    main()
