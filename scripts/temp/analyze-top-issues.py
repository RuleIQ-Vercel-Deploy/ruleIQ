#!/usr/bin/env python3
"""Analyze and categorize top ruff issues"""
import logging
logger = logging.getLogger(__name__)

RULE_DESCRIPTIONS = {
    "COM812": "Missing trailing comma in Python 3.6+ (flake8-commas)",
    "FA100": "Missing from __future__ import annotations (flake8-future-annotations)",
    "T201": "logger.info() found - use logging instead (flake8-print)",
    "D400": "First line should end with a period (pydocstyle)",
    "D415": "First line should end with a period, question mark, or exclamation point (pydocstyle)",
    "G004": "Logging statement uses f-string (flake8-logging-format)",
    "D212": "Multi-line docstring summary should start at the first line (pydocstyle)",
    "ANN201": "Missing return type annotation for public function (flake8-annotations)",
    "BLE001": "Do not catch blind exception: Exception (flake8-blind-except)",
    "Q000": "Single quotes found but double quotes preferred (flake8-quotes)",
}

logger.info("Top SonarCloud/Ruff Issues to Fix:\n")
logger.info("=" * 60)

issues = [
    ("COM812", 6378),
    ("FA100", 5422),
    ("T201", 4556),
    ("D400", 3384),
    ("D415", 3380),
    ("G004", 1863),
    ("D212", 1495),
    ("ANN201", 1065),
    ("BLE001", 1046),
    ("Q000", 847),
]

for code, count in issues:
    desc = RULE_DESCRIPTIONS.get(code, "Unknown rule")
    logger.info(f"{code}: {count:,} violations")
    logger.info(f"  → {desc}\n")

logger.info("\nPriority Order for Fixes:")
logger.info("1. FA100 - Add future annotations import (5,422 violations)")
logger.info("2. T201 - Replace print() with logging (4,556 violations)")
logger.info("3. ANN201 - Add return type annotations (1,065 violations)")
logger.info("4. BLE001 - Fix blind exception catching (1,046 violations)")
logger.info("5. G004 - Fix logging f-strings (1,863 violations)")
