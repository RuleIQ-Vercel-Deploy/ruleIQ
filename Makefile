# Makefile for ruleIQ
# Provides test, migration, and run commands with Doppler-based secrets management.

SHELL := /bin/sh
.DEFAULT_GOAL := help

# Project settings
PROJECT_NAME     ?= ruleIQ
PYTHON           ?= python
VENV             ?= .venv
VENV_BIN         ?= $(VENV)/bin
ACTIVATE          = . $(VENV_BIN)/activate

# Doppler configuration
DOPPLER_PROJECT  ?= ruleiq
DOPPLER_CONFIG   ?= dev
# Back-compat: allow CONF to override the config if provided
CONF             ?= $(DOPPLER_CONFIG)
DOPPLER_CONFIG    = $(CONF)

DOPPLER_RUN       = doppler run -p $(DOPPLER_PROJECT) -c $(DOPPLER_CONFIG) --

# -------------------------------------------------------------------
# Help
# -------------------------------------------------------------------
.PHONY: help
help: ## Show available make targets
	@echo "Make targets for $(PROJECT_NAME)"
	@echo
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  %-30s %s\n", $1, $2}' $(MAKEFILE_LIST)
	@echo
	@echo "Configuration:"
	@echo "  DOPPLER_PROJECT=$(DOPPLER_PROJECT) DOPPLER_CONFIG=$(DOPPLER_CONFIG)"

# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------
.PHONY: install-test-deps test-fast test-integration test-performance test-full test-ci test-ai test-security test-e2e \
        test-parallel test-sequential list-test-modes test-info test-quick test-dev test-all test-unit test-api test-database \
        test-slow test-smoke test-coverage test-coverage-fast test-benchmark clean-test test-watch test-profile test-py311 \
        test-py312 test-py313 test-memory test-stress test-file test-pattern test-docker test-report test-continuous

install-test-deps: ## Install test dependencies
	pip install pytest-xdist pytest-parallel pytest-benchmark pytest-timeout pytest-asyncio

# Chunked test execution modes
test-fast: ## Run fast unit tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_tests_chunked.py --mode fast

test-integration: ## Run integration tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_tests_chunked.py --mode integration

test-performance: ## Run performance tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_tests_chunked.py --mode performance

test-ai: ## Run AI and compliance tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_tests_chunked.py --mode ai

test-security: ## Run security and auth tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_tests_chunked.py --mode security

test-e2e: ## Run end-to-end tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_tests_chunked.py --mode e2e

test-full: ## Run full test suite
	@$(ACTIVATE) && $(PYTHON) scripts/run_tests_chunked.py --mode full

test-ci: ## Run CI-optimized test suite
	@$(ACTIVATE) && $(PYTHON) scripts/run_tests_chunked.py --mode ci

# Traditional pytest execution
test-parallel: ## Run all tests with pytest-xdist
	$(PYTHON) -m pytest -n auto --dist=worksteal --tb=short --maxfail=5

test-sequential: ## Run all tests sequentially
	$(PYTHON) -m pytest --tb=short --maxfail=5

# Utilities
list-test-modes: ## List available test modes
	$(PYTHON) scripts/run_tests_chunked.py --list-modes

test-info: ## Show system info for test optimization
	@$(PYTHON) -c "import psutil; print(f'CPUs: {psutil.cpu_count()}, Memory: {psutil.virtual_memory().total/(1024**3):.1f}GB, Available: {psutil.virtual_memory().available/(1024**3):.1f}GB')"

# Development shortcuts
test-quick: test-fast ## Alias: quick unit tests
test-dev: test-integration ## Alias: integration tests
test-all: test-full ## Alias: full suite

# Markers
test-unit: ## Run tests marked 'unit'
	$(PYTHON) -m pytest -m unit -n auto --dist=worksteal

test-api: ## Run tests marked 'api'
	$(PYTHON) -m pytest -m api -n 2 --dist=worksteal

test-database: ## Run tests marked 'database'
	$(PYTHON) -m pytest -m database -n 1

test-slow: ## Run tests marked 'slow'
	$(PYTHON) -m pytest -m slow -n 1

test-smoke: ## Run smoke tests
	$(PYTHON) -m pytest -m smoke -n auto --dist=worksteal

# Coverage
test-coverage: ## Run tests with coverage report
	$(PYTHON) -m pytest --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=70 --cov-branch

test-coverage-fast: ## Run unit tests with coverage (fast)
	$(PYTHON) -m pytest tests/unit/ -m unit --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=70 --cov-branch

# Benchmark
test-benchmark: ## Run benchmark tests
	$(PYTHON) -m pytest tests/performance/ --benchmark-only --benchmark-sort=mean

# Cleanup
clean-test: ## Remove test artifacts
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -f coverage.xml coverage.json
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Watch (requires pytest-watch)
test-watch: ## Watch mode (requires pytest-watch)
	ptw --runner "python -m pytest -n auto --dist=worksteal"

# Profiling
test-profile: ## Profile test execution
	$(PYTHON) -m pytest --profile --profile-svg

# Python versions
test-py311: ## Run tests on Python 3.11 (if available)
	python3.11 -m pytest -n auto --dist worksteal

test-py312: ## Run tests on Python 3.12 (if available)
	python3.12 -m pytest -n auto --dist worksteal

test-py313: ## Run tests on Python 3.13 (if available)
	python3.13 -m pytest -n auto --dist worksteal

# Memory profiling
test-memory: ## Run memory-related tests
	$(PYTHON) -m pytest -m memory --tb=short

# Stress testing
test-stress: ## Run stress tests (repeats fast tests)
	for i in 1 2 3 4 5; do $(MAKE) test-fast || exit 1; done

# Specific files/patterns
test-file: ## Run a specific test file (FILE=path/to/test_file.py)
	@if [ -z "$(FILE)" ]; then echo "Please specify FILE=path/to/test_file.py"; exit 1; fi
	$(PYTHON) -m pytest $(FILE) -v

test-pattern: ## Run tests matching a pattern (PATTERN=pattern)
	@if [ -z "$(PATTERN)" ]; then echo "Please specify PATTERN=test_name_pattern"; exit 1; fi
	$(PYTHON) -m pytest -k "$(PATTERN)" -v

# Docker-based testing
test-docker: ## Run tests via docker-compose
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Reports and continuous testing
test-report: ## Generate test report to test_report.txt
	$(PYTHON) scripts/run_tests_chunked.py --mode full > test_report.txt 2>&1
	@echo "Test report generated: test_report.txt"

test-continuous: ## Run fast tests on a loop (Ctrl+C to stop)
	@while true; do \
		$(MAKE) test-fast; \
		sleep 30; \
	done

# -------------------------------------------------------------------
# Test groups (independent groups)
# -------------------------------------------------------------------
.PHONY: test-groups test-groups-parallel test-groups-list test-group-unit test-group-ai test-group-api test-group-endpoints test-group-advanced test-group-e2e test-quick-groups test-core-groups

test-groups: ## Run all test groups sequentially
	$(PYTHON) test_groups.py all

test-groups-parallel: ## Run all test groups in parallel
	$(PYTHON) test_groups.py parallel

test-groups-list: ## List all test groups
	$(PYTHON) test_groups.py list

test-group-unit: ## Run Unit group
	$(PYTHON) test_groups.py group1_unit

test-group-ai: ## Run AI Core group
	$(PYTHON) test_groups.py group2_ai_core

test-group-api: ## Run API Basic group
	$(PYTHON) test_groups.py group3_api_basic

test-group-endpoints: ## Run AI Endpoints group
	$(PYTHON) test_groups.py group4_ai_endpoints

test-group-advanced: ## Run Advanced Features group
	$(PYTHON) test_groups.py group5_advanced

test-group-e2e: ## Run End-to-End group
	$(PYTHON) test_groups.py group6_e2e

test-quick-groups: ## Run Unit + AI groups
	$(PYTHON) test_groups.py group1_unit && $(PYTHON) test_groups.py group2_ai_core

test-core-groups: ## Run Unit + AI + API groups
	$(PYTHON) test_groups.py group1_unit && $(PYTHON) test_groups.py group2_ai_core && $(PYTHON) test_groups.py group3_api_basic

# -------------------------------------------------------------------
# Integration testing suites
# -------------------------------------------------------------------
.PHONY: test-integration-comprehensive test-integration-api-workflows test-integration-external-services \
        test-integration-contracts test-integration-database test-integration-security test-integration-performance \
        test-integration-ai-services test-integration-e2e test-integration-quick test-integration-core

test-integration-comprehensive: ## Run all integration test suites
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite all

test-integration-api-workflows: ## Run API workflow integration tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite api-workflows

test-integration-external-services: ## Run external services integration tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite external-services

test-integration-contracts: ## Run contract validation tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite contracts

test-integration-database: ## Run database integration tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite database

test-integration-security: ## Run security integration tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite security

test-integration-performance: ## Run performance integration tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite performance

test-integration-ai-services: ## Run AI service integration tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite ai-services

test-integration-e2e: ## Run end-to-end integration tests
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite e2e

test-integration-quick: ## Quick integration tests (API workflows + contracts)
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite api-workflows
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite contracts

test-integration-core: ## Core integration tests (API workflows + database + contracts)
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite api-workflows
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite database
	@$(ACTIVATE) && $(PYTHON) scripts/run_integration_tests.py --suite contracts

# -------------------------------------------------------------------
# Repository cleanup
# -------------------------------------------------------------------
.PHONY: repo-clean repo-clean-apply

repo-clean: ## Dry-run repository cleanup
	$(PYTHON) scripts/repo_cleanup.py

repo-clean-apply: ## Apply repository cleanup
	$(PYTHON) scripts/repo_cleanup.py --apply --remove-empty-dirs

# -------------------------------------------------------------------
# Database migrations via Doppler
# -------------------------------------------------------------------
.PHONY: migrate-dev migrate-stg migrate-prod migrate-upgrade migrate-downgrade-one migrate-current migrate-history migrate-revision

migrate-dev: ## Run Alembic migrations (dev)
	@$(MAKE) migrate-upgrade DOPPLER_CONFIG=dev TARGET=head

migrate-stg: ## Run Alembic migrations (stg)
	@$(MAKE) migrate-upgrade DOPPLER_CONFIG=stg TARGET=head

migrate-prod: ## Run Alembic migrations (prod)
	@$(MAKE) migrate-upgrade DOPPLER_CONFIG=prod TARGET=head

migrate-upgrade: ## Upgrade Alembic to TARGET (TARGET=head or revision id)
	@if [ -z "$(TARGET)" ]; then echo "Specify TARGET=head or a revision id"; exit 1; fi
	$(DOPPLER_RUN) alembic upgrade $(TARGET)

migrate-downgrade-one: ## Downgrade a single Alembic revision
	$(DOPPLER_RUN) alembic downgrade -1

migrate-current: ## Show current Alembic revision
	$(DOPPLER_RUN) alembic current

migrate-history: ## Show Alembic migration history
	$(DOPPLER_RUN) alembic history

migrate-revision: ## Create a new Alembic revision (MSG="your message")
	@if [ -z "$(MSG)" ]; then echo "Specify MSG='your revision message'"; exit 1; fi
	$(DOPPLER_RUN) alembic revision -m "$(MSG)"

# -------------------------------------------------------------------
# Run app via Doppler
# -------------------------------------------------------------------
.PHONY: run-app run-app-dev run-app-stg run-app-prod run-backend run-backend-dev run-backend-stg run-backend-prod run-frontend-dev

run-app: ## Run backend and frontend (./start) with Doppler
	$(DOPPLER_RUN) ./start

run-app-dev: ## Run backend and frontend (dev)
	@$(MAKE) run-app DOPPLER_CONFIG=dev

run-app-stg: ## Run backend and frontend (stg)
	@$(MAKE) run-app DOPPLER_CONFIG=stg

run-app-prod: ## Run backend and frontend (prod)
	@$(MAKE) run-app DOPPLER_CONFIG=prod

run-backend: ## Run backend with Doppler (uses --reload in dev)
	@if [ "$(DOPPLER_CONFIG)" = "dev" ]; then \
		$(DOPPLER_RUN) $(PYTHON) main.py --reload ; \
	else \
		$(DOPPLER_RUN) $(PYTHON) main.py ; \
	fi

run-backend-dev: ## Run backend (dev)
	@$(MAKE) run-backend DOPPLER_CONFIG=dev

run-backend-stg: ## Run backend (stg)
	@$(MAKE) run-backend DOPPLER_CONFIG=stg

run-backend-prod: ## Run backend (prod)
	@$(MAKE) run-backend DOPPLER_CONFIG=prod

run-frontend-dev: ## Run frontend (Next.js) with Doppler (dev)
	cd frontend && $(DOPPLER_RUN) pnpm dev
