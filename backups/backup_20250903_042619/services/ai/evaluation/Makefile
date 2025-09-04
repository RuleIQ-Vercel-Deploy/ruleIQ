# Golden Dataset System Makefile
# Manages ingestion, retrieval, and testing of golden datasets for AI evaluation

.PHONY: help install test-neo4j ingest-golden api-start api-stop test-retrieval clean-golden all

# Default target
help:
	@echo "Golden Dataset Management Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install required dependencies"
	@echo "  make test-neo4j       - Test Neo4j connection and setup"
	@echo ""
	@echo "Data Management:"
	@echo "  make ingest-golden    - Ingest sample golden dataset into Neo4j"
	@echo "  make clean-golden     - Clear all golden dataset from Neo4j"
	@echo ""
	@echo "API Operations:"
	@echo "  make api-start        - Start the Retrieval API server"
	@echo "  make api-stop         - Stop the Retrieval API server"
	@echo "  make test-retrieval   - Test all Retrieval API endpoints"
	@echo ""
	@echo "Complete Workflows:"
	@echo "  make all              - Run complete setup and test workflow"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install sentence-transformers neo4j fastapi uvicorn
	@echo "✅ Dependencies installed"

# Test Neo4j connection
test-neo4j:
	@echo "🔌 Testing Neo4j connection..."
	@python3 -c "import os; os.environ['NEO4J_URI']='bolt://localhost:7688'; \
		os.environ['NEO4J_USER']='neo4j'; os.environ['NEO4J_PASSWORD']='ruleiq123'; \
		from neo4j import GraphDatabase; \
		driver = GraphDatabase.driver('bolt://localhost:7688', auth=('neo4j', 'ruleiq123')); \
		with driver.session() as s: \
			result = s.run('RETURN 1 as test').single(); \
			print('✅ Neo4j connection successful!' if result else '❌ Connection failed'); \
		driver.close()"

# Ingest sample golden dataset
ingest-golden:
	@echo "📥 Ingesting golden dataset..."
	@python3 -c "import os; import sys; \
		os.environ['NEO4J_URI']='bolt://localhost:7688'; \
		os.environ['NEO4J_USER']='neo4j'; \
		os.environ['NEO4J_PASSWORD']='ruleiq123'; \
		sys.path.insert(0, '../../..'); \
		from services.ai.evaluation.tools.ingestion_fixed import GoldenDatasetIngestion; \
		ingestion = GoldenDatasetIngestion(); \
		result = ingestion.ingest_from_file('data/sample_golden_dataset.json'); \
		print(f'✅ Ingested {result[\"documents_processed\"]} documents, {result[\"chunks_created\"]} chunks') if result['success'] \
		else print(f'❌ Ingestion failed: {result[\"errors\"]}')"

# Start Retrieval API
api-start:
	@echo "🚀 Starting Retrieval API on port 8001..."
	@if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then \
		echo "⚠️  API already running on port 8001"; \
	else \
		nohup python3 tools/retrieval_api.py > /tmp/golden_api.log 2>&1 & \
		echo $$! > /tmp/golden_api.pid; \
		sleep 3; \
		if curl -s http://localhost:8001/health >/dev/null 2>&1; then \
			echo "✅ API started successfully (PID: $$(cat /tmp/golden_api.pid))"; \
		else \
			echo "❌ Failed to start API"; \
			cat /tmp/golden_api.log; \
		fi \
	fi

# Stop Retrieval API
api-stop:
	@echo "🛑 Stopping Retrieval API..."
	@if [ -f /tmp/golden_api.pid ]; then \
		kill $$(cat /tmp/golden_api.pid) 2>/dev/null || true; \
		rm -f /tmp/golden_api.pid; \
		echo "✅ API stopped"; \
	else \
		pkill -f "retrieval_api.py" 2>/dev/null || true; \
		echo "✅ API processes terminated"; \
	fi

# Test Retrieval API
test-retrieval: api-start
	@echo "🧪 Testing Retrieval API..."
	@sleep 2
	@python3 ../../../tests/test_golden_retrieval_api.py

# Clean golden dataset from Neo4j
clean-golden:
	@echo "🗑️  Cleaning golden dataset..."
	@python3 -c "import os; \
		os.environ['NEO4J_URI']='bolt://localhost:7688'; \
		os.environ['NEO4J_USER']='neo4j'; \
		os.environ['NEO4J_PASSWORD']='ruleiq123'; \
		from neo4j import GraphDatabase; \
		driver = GraphDatabase.driver('bolt://localhost:7688', auth=('neo4j', 'ruleiq123')); \
		with driver.session() as s: \
			result = s.run('MATCH (d:GoldenDocument) DETACH DELETE d'); \
			s.run('MATCH (c:GoldenChunk) WHERE NOT (()-[:HAS_CHUNK]->(c)) DELETE c'); \
			print('✅ Golden dataset cleaned'); \
		driver.close()"

# Complete workflow
all: install test-neo4j clean-golden ingest-golden test-retrieval
	@echo ""
	@echo "🎉 Golden Dataset System fully operational!"
	@echo ""
	@echo "Next steps:"
	@echo "  - Access API at http://localhost:8001"
	@echo "  - View API docs at http://localhost:8001/docs"
	@echo "  - Use 'make api-stop' to stop the API when done"