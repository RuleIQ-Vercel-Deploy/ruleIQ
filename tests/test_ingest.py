#!/usr/bin/env python3
"""Test document ingestion directly (external service dependent).

Notes:
- Marked as external and docker; skipped if required env vars not set.
- Does not set or rely on hardcoded secrets.
"""

import os
import sys
import pytest
from neo4j import GraphDatabase

# Ensure local project importability if needed
sys.path.insert(0, ".")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7688")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")  # must be provided securely


@pytest.mark.external
@pytest.mark.docker
@pytest.mark.skipif(
    not NEO4J_PASSWORD,
    reason="NEO4J_PASSWORD not set; skipping external Neo4j-dependent test",
)
def test_connection():
    """Test Neo4j connection using environment-provided credentials."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 as num")
            assert result.single()["num"] == 1
    finally:
        driver.close()


@pytest.mark.external
@pytest.mark.docker
@pytest.mark.skipif(
    not NEO4J_PASSWORD,
    reason="NEO4J_PASSWORD not set; skipping external Neo4j-dependent test",
)
def test_ingest_one_document_from_manifest(monkeypatch):
    """Ingest a single priority document from manifest into Neo4j.

    Skips if manifest path not available or env not configured.
    """
    # Defer heavy imports until after skip conditions
    from services.ai.evaluation.tools.ingest_docs import (
        ManifestProcessor,
        GoldenDatasetBuilder,
    )

    manifest_path = os.getenv(
        "GOLDEN_MANIFEST_PATH",
        "/home/omar/Documents/ruleIQ/data/manifests/compliance_ml_manifest.json",
    )
    if not os.path.exists(manifest_path):
        pytest.skip(f"Manifest not found at {manifest_path}")

    # Build
    processor = ManifestProcessor(manifest_path)
    builder = GoldenDatasetBuilder()

    # Ensure builder uses env-provided connection (no hardcoding)
    conn = builder.graph_ingestion.connection
    # If connection object exposes setters, ensure it picks env values
    if hasattr(conn, "uri"):
        conn.uri = NEO4J_URI
    if hasattr(conn, "user"):
        conn.user = NEO4J_USER
    if hasattr(conn, "password"):
        conn.password = NEO4J_PASSWORD

    # Select a document deterministically if possible
    docs = processor.get_priority_documents(5)
    if not docs:
        pytest.skip("No priority documents found in manifest")

    # Prefer PDFs from trusted domains to reduce flakiness
    candidate = next(
        (d for d in docs if d.get("url", "").endswith(".pdf")), docs[0]
    )

    golden_doc = builder.process_manifest_document(candidate)
    assert golden_doc is not None
    assert isinstance(golden_doc.content, str) and len(golden_doc.content) > 0

    # Ingest (smoke)
    success = builder.ingest_document(golden_doc)
    assert success is True
