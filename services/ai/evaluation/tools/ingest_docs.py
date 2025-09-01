#!/usr/bin/env python3
"""Document ingestion tool for golden datasets.

This script handles the complete ingestion pipeline:
1. Load manifest via _load_manifest_clean
2. Fetch each URL → extract text
3. Chunk ≈1000 tokens
4. Embed via BAAI/bge-small-en-v1.5  
5. Upsert to Neo4j
"""

import json
import hashlib
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from services.ai.evaluation.tools.ingestion import (
    DocumentProcessor,
    ChunkProcessor, 
    EmbeddingGenerator,
    GraphIngestion,
    GoldenDatasetIngestion
)
from services.ai.evaluation.schemas.common import (
    GoldenDoc,
    SourceMeta
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ManifestProcessor:
    """Process manifest files for document ingestion."""
    
    def __init__(self, manifest_path: str):
        """Initialize with manifest path."""
        self.manifest_path = Path(manifest_path)
        self.manifest_data = None
        
    def _load_manifest_clean(self) -> Dict[str, Any]:
        """Load and clean manifest file."""
        logger.info(f"Loading manifest from {self.manifest_path}")
        
        with open(self.manifest_path, 'r') as f:
            # Handle potential formatting issues
            content = f.read()
            # Remove any trailing commas in JSON arrays/objects
            import re
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)
            
            self.manifest_data = json.loads(content)
            
        # Support both 'items' and 'documents' keys
        docs = self.manifest_data.get('items', self.manifest_data.get('documents', []))
        logger.info(f"Loaded manifest with {len(docs)} documents")
        return self.manifest_data
    
    def get_priority_documents(self, min_priority: int = 4) -> List[Dict[str, Any]]:
        """Get documents with priority >= min_priority."""
        if not self.manifest_data:
            self._load_manifest_clean()
            
        # Support both 'items' and 'documents' keys
        docs = self.manifest_data.get('items', self.manifest_data.get('documents', []))
        priority_docs = [
            doc for doc in docs
            if doc.get('priority', 0) >= min_priority
        ]
        
        logger.info(f"Found {len(priority_docs)} documents with priority >= {min_priority}")
        return priority_docs

class DocumentFetcher:
    """Fetch and extract text from URLs."""
    
    def __init__(self):
        """Initialize document fetcher."""
        self.session = None
        self._setup_session()
        
    def _setup_session(self):
        """Setup HTTP session with retries."""
        import requests
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        
        self.session = requests.Session()
        # Add user agent to avoid blocks
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def fetch_document(self, url: str, doc_type: str = "html") -> Optional[str]:
        """Fetch document from URL and extract text."""
        logger.info(f"Fetching {doc_type} document from {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            if doc_type == "pdf":
                return self._extract_pdf_text(response.content)
            else:
                return self._extract_html_text(response.text)
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _extract_html_text(self, html: str) -> str:
        """Extract text from HTML using BeautifulSoup."""
        from bs4 import BeautifulSoup
        
        try:
            # Parse with BeautifulSoup for text extraction
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get text and clean up whitespace
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting HTML text: {e}")
            # Fallback to simple BeautifulSoup extraction
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
    
    def _extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF using pypdf."""
        import io
        from pypdf import PdfReader
        
        try:
            pdf_file = io.BytesIO(pdf_content)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    
            return ' '.join(text_parts)
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""

class GoldenDatasetBuilder:
    """Build golden dataset from manifest documents."""
    
    def __init__(self):
        """Initialize builder components."""
        self.fetcher = DocumentFetcher()
        self.doc_processor = DocumentProcessor()
        self.chunk_processor = ChunkProcessor(chunk_size=1000, overlap=100)
        self.embedding_generator = EmbeddingGenerator()
        self.graph_ingestion = GraphIngestion()
        
    def process_manifest_document(self, doc_info: Dict[str, Any]) -> Optional[GoldenDoc]:
        """Process a single document from manifest."""
        url = doc_info.get('url', '')
        title = doc_info.get('title', '')
        # Determine doc type from URL if not specified
        doc_type = doc_info.get('type', 'pdf' if url.endswith('.pdf') else 'html')
        
        # Fetch document content
        content = self.fetcher.fetch_document(url, doc_type)
        if not content:
            logger.warning(f"Failed to fetch content for {title}")
            return None
            
        # Create source metadata
        source_meta = SourceMeta(
            origin=url,
            domain=self._extract_domain(url),
            trust_score=doc_info.get('priority', 3) / 5.0,  # Normalize to 0-1
            sha256=hashlib.sha256(content.encode()).hexdigest(),
            fetched_at=datetime.utcnow()
        )
        
        # Create golden document
        doc_id = f"doc_{hashlib.md5(url.encode()).hexdigest()[:12]}"
        
        # Extract category from tags or use 'general'
        tags = doc_info.get('tags', [])
        category = tags[0] if tags else 'general'
        
        golden_doc = GoldenDoc(
            doc_id=doc_id,
            content=self.doc_processor.preprocess_content(content),
            source_meta=source_meta,
            reg_citations=[category],
            expected_outcomes=[{
                "category": category,
                "confidence": doc_info.get('priority', 3) / 5.0
            }]
        )
        
        return golden_doc
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    
    def ingest_document(self, golden_doc: GoldenDoc) -> bool:
        """Ingest a golden document into Neo4j."""
        try:
            # Generate embedding for document
            doc_embedding = self.embedding_generator.generate_embedding(
                golden_doc.content[:2000]  # Use first 2000 chars for doc embedding
            )
            
            # Ingest document
            if not self.graph_ingestion.ingest_document(golden_doc, doc_embedding):
                return False
                
            # Chunk the document
            chunks = self.chunk_processor.chunk_document(golden_doc)
            logger.info(f"Created {len(chunks)} chunks for document {golden_doc.doc_id}")
            
            # Generate embeddings for chunks
            chunk_texts = [chunk.content for chunk in chunks]
            chunk_embeddings = self.embedding_generator.generate_embeddings_batch(chunk_texts)
            
            # Ingest chunks
            success_count = 0
            for chunk, embedding in zip(chunks, chunk_embeddings):
                if self.graph_ingestion.ingest_chunk(chunk, embedding):
                    success_count += 1
                    
            logger.info(f"Successfully ingested {success_count}/{len(chunks)} chunks")
            
            # Create chunk relationships
            if chunks:
                self.graph_ingestion.create_chunk_relationships(chunks)
                
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting document {golden_doc.doc_id}: {e}")
            return False

def main():
    """Main ingestion pipeline."""
    parser = argparse.ArgumentParser(description='Ingest documents for golden dataset')
    parser.add_argument(
        '--manifest',
        type=str,
        default='/home/omar/Documents/ruleIQ/data/manifests/compliance_ml_manifest.json',
        help='Path to manifest file'
    )
    parser.add_argument(
        '--min-priority',
        type=int,
        default=4,
        help='Minimum priority for documents to ingest (default: 4)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of documents to process'
    )
    
    args = parser.parse_args()
    
    # Initialize components
    manifest_processor = ManifestProcessor(args.manifest)
    builder = GoldenDatasetBuilder()
    
    # Get priority documents
    priority_docs = manifest_processor.get_priority_documents(args.min_priority)
    
    if args.limit:
        priority_docs = priority_docs[:args.limit]
        
    logger.info(f"Processing {len(priority_docs)} documents")
    
    # Process each document
    success_count = 0
    failed_docs = []
    
    for idx, doc_info in enumerate(priority_docs, 1):
        logger.info(f"Processing document {idx}/{len(priority_docs)}: {doc_info.get('title', 'Unknown')}")
        
        # Process document
        golden_doc = builder.process_manifest_document(doc_info)
        if not golden_doc:
            failed_docs.append(doc_info.get('title', 'Unknown'))
            continue
            
        # Ingest into Neo4j
        if builder.ingest_document(golden_doc):
            success_count += 1
        else:
            failed_docs.append(doc_info.get('title', 'Unknown'))
    
    # Summary
    logger.info("=" * 50)
    logger.info(f"Ingestion complete!")
    logger.info(f"Successfully processed: {success_count}/{len(priority_docs)} documents")
    
    if failed_docs:
        logger.warning(f"Failed documents: {', '.join(failed_docs)}")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())