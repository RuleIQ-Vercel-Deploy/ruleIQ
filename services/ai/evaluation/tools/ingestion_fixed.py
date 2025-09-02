"""Golden Dataset ingestion tool for Neo4j - Fixed version."""

import os

# Ensure correct Neo4j settings before any other imports
if not os.getenv("NEO4J_URI"):
    os.environ["NEO4J_URI"] = "bolt://localhost:7688"
if not os.getenv("NEO4J_USER"):
    os.environ["NEO4J_USER"] = "neo4j"
if not os.getenv("NEO4J_PASSWORD"):
    os.environ["NEO4J_PASSWORD"] = "ruleiq123"

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import numpy as np

from services.ai.evaluation.schemas.common import (
    GoldenDoc,
    GoldenChunk,
    SourceMeta,
    RegCitation,
    ExpectedOutcome,
)


class Neo4jConnectionFixed:
    """Fixed Neo4j connection that uses correct defaults."""

    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize with correct Neo4j settings."""
        if self._driver is None:
            from neo4j import GraphDatabase

            self.uri = "bolt://localhost:7688"  # Force correct port
            self.user = "neo4j"  # Force correct user
            self.password = "ruleiq123"  # Force correct password

            print(f"[Neo4jConnectionFixed] Connecting to: {self.uri}")

            self._driver = GraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )

    def get_driver(self):
        """Get Neo4j driver instance."""
        return self._driver

    def close(self):
        """Close the driver connection."""
        if self._driver:
            self._driver.close()
            self._driver = None


class DocumentProcessor:
    """Process and validate golden dataset documents."""

    def load_golden_dataset(self, file_path: str) -> List[GoldenDoc]:
        """Load golden dataset from JSON file."""
        # Sanitize file path to prevent path traversal attacks
        import os
        safe_path = os.path.abspath(os.path.normpath(file_path))
        # Ensure the path is within allowed directories
        if not safe_path.startswith(os.path.abspath(".")):
            raise ValueError("Invalid file path: attempted path traversal")
        
        with open(safe_path, "r") as f:
            data = json.load(f)

        documents = []
        for doc_data in data.get("documents", []):
            # Parse source_meta
            source_meta_data = doc_data.get("source_meta", {})
            if "fetched_at" in source_meta_data:
                # Parse ISO format datetime
                source_meta_data["fetched_at"] = datetime.fromisoformat(
                    source_meta_data["fetched_at"].replace("Z", "+00:00")
                )
            source_meta = SourceMeta(**source_meta_data)

            # Create document
            doc = GoldenDoc(
                doc_id=doc_data["doc_id"],
                content=doc_data["content"],
                source_meta=source_meta,
                reg_citations=doc_data.get("reg_citations"),
                expected_outcomes=doc_data.get("expected_outcomes"),
            )
            documents.append(doc)

        return documents

    def validate_document(self, doc: Any) -> bool:
        """Validate document schema."""
        if isinstance(doc, GoldenDoc):
            return bool(doc.doc_id and doc.content)
        return False


class EmbeddingService:
    """Generate embeddings for golden dataset."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """Initialize with local sentence-transformers model."""
        self.model_name = model_name
        self.model = None
        self.dimension = 384

    def _load_model(self):
        """Lazy load the model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(self.model_name)
                print(f"✅ Loaded embedding model: {self.model_name}")
            except ImportError:
                print("⚠️ sentence-transformers not installed, using mock embeddings")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        self._load_model()

        if self.model:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        else:
            # Mock embedding for testing
            return np.random.rand(self.dimension).tolist()


class ChunkingService:
    """Chunk documents for golden dataset."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """Initialize chunking parameters."""
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: GoldenDoc) -> List[GoldenChunk]:
        """Chunk a document into smaller pieces."""
        content = doc.content
        chunks = []

        # Simple character-based chunking
        start = 0
        chunk_index = 0

        while start < len(content):
            end = min(start + self.chunk_size, len(content))

            # Try to break at sentence boundary
            if end < len(content):
                last_period = content.rfind(".", start, end)
                if last_period > start:
                    end = last_period + 1

            chunk_text = content[start:end].strip()

            if chunk_text:
                chunk = GoldenChunk(
                    chunk_id=f"{doc.doc_id}_chunk_{chunk_index}",
                    doc_id=doc.doc_id,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    source_meta=doc.source_meta,  # Pass the source_meta from document
                    metadata={
                        "source": (
                            doc.source_meta.origin if doc.source_meta else "unknown"
                        ),
                        "start_char": start,
                        "end_char": end,
                    },
                )
                chunks.append(chunk)
                chunk_index += 1

            # Move to next chunk with overlap
            start = end - self.overlap if end < len(content) else end

        return chunks


class GoldenDatasetIngestion:
    """Main ingestion pipeline for golden datasets."""

    def __init__(self):
        """Initialize ingestion components."""
        self.processor = DocumentProcessor()
        self.embedding_service = EmbeddingService()
        self.chunking_service = ChunkingService()
        self.neo4j = Neo4jConnectionFixed()

    def ingest_from_file(self, file_path: str) -> Dict[str, Any]:
        """Ingest golden dataset from file."""
        result = {
            "success": False,
            "documents_processed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "errors": [],
        }

        try:
            # Load documents
            documents = self.processor.load_golden_dataset(file_path)
            print(f"📚 Loaded {len(documents)} documents")

            driver = self.neo4j.get_driver()

            # Create index if not exists
            with driver.session() as session:
                try:
                    session.run(
                        """
                        CREATE VECTOR INDEX golden_chunk_embeddings IF NOT EXISTS
                        FOR (c:GoldenChunk)
                        ON (c.embedding)
                        OPTIONS {
                            indexConfig: {
                                `vector.dimensions`: 384,
                                `vector.similarity_function`: 'cosine'
                            }
                        }
                    """
                    )
                    print("✅ Vector index verified")
                except Exception as e:
                    print(f"⚠️ Index check: {e}")

            # Process each document
            for doc in documents:
                try:
                    # Validate document
                    if not self.processor.validate_document(doc):
                        result["errors"].append(f"Invalid document: {doc.doc_id}")
                        continue

                    # Chunk document
                    chunks = self.chunking_service.chunk_document(doc)

                    # Generate embeddings for chunks (store separately, not on chunk object)
                    chunk_embeddings = []
                    for chunk in chunks:
                        embedding = self.embedding_service.generate_embedding(
                            chunk.content
                        )
                        chunk_embeddings.append(embedding)
                        result["embeddings_generated"] += 1

                    # Store in Neo4j
                    with driver.session() as session:
                        # Create document node
                        session.run(
                            """
                            MERGE (d:GoldenDocument {doc_id: $doc_id})
                            SET d.content = $content,
                                d.source = $source,
                                d.created_at = datetime()
                        """,
                            doc_id=doc.doc_id,
                            content=doc.content,
                            source=(
                                doc.source_meta.origin if doc.source_meta else "unknown"
                            ),
                        )

                        # Create chunk nodes with embeddings
                        for chunk, embedding in zip(chunks, chunk_embeddings):
                            session.run(
                                """
                                MATCH (d:GoldenDocument {doc_id: $doc_id})
                                CREATE (c:GoldenChunk {
                                    chunk_id: $chunk_id,
                                    content: $content,
                                    embedding: $embedding,
                                    chunk_index: $chunk_index,
                                    created_at: datetime()
                                })
                                CREATE (d)-[:HAS_CHUNK]->(c)
                            """,
                                doc_id=doc.doc_id,
                                chunk_id=chunk.chunk_id,
                                content=chunk.content,
                                embedding=embedding,
                                chunk_index=chunk.chunk_index,
                            )
                            result["chunks_created"] += 1

                    result["documents_processed"] += 1
                    print(f"✅ Processed document: {doc.doc_id}")

                except Exception as e:
                    error_msg = f"Failed to ingest document: {doc.doc_id} - {str(e)}"
                    result["errors"].append(error_msg)
                    print(f"❌ {error_msg}")

            result["success"] = result["documents_processed"] > 0

        except Exception as e:
            result["errors"].append(f"Ingestion pipeline error: {str(e)}")
            print(f"❌ Pipeline error: {e}")

        return result

    def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity."""
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)

        driver = self.neo4j.get_driver()
        results = []

        with driver.session() as session:
            result = session.run(
                """
                CALL db.index.vector.queryNodes(
                    'golden_chunk_embeddings',
                    $limit,
                    $query_embedding
                ) YIELD node, score
                MATCH (d:GoldenDocument)-[:HAS_CHUNK]->(node)
                RETURN node.chunk_id as chunk_id,
                       node.content as content,
                       d.doc_id as doc_id,
                       d.source as source,
                       score
                ORDER BY score DESC
            """,
                limit=limit,
                query_embedding=query_embedding,
            )

            for record in result:
                results.append(
                    {
                        "chunk_id": record["chunk_id"],
                        "content": record["content"],
                        "doc_id": record["doc_id"],
                        "source": record["source"],
                        "score": record["score"],
                    }
                )

        return results
