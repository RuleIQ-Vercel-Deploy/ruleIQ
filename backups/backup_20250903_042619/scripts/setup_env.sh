#!/bin/bash

# RuleIQ Environment Setup Script
# This script helps set up the environment for development or production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Default values
ENVIRONMENT="development"
SKIP_CONFIRM=false
CREATE_DATABASE=false
SETUP_REDIS=false

# Help function
show_help() {
    echo -e "${BLUE}RuleIQ Environment Setup Script${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment    Set environment (development|staging|production)"
    echo "  -d, --create-db      Create database if it doesn't exist"
    echo "  -r, --setup-redis    Setup Redis configuration"
    echo "  -y, --yes            Skip confirmation prompts"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment production --create-db"
    echo "  $0 -e development -d -r"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -d|--create-db)
            CREATE_DATABASE=true
            shift
            ;;
        -r|--setup-redis)
            SETUP_REDIS=true
            shift
            ;;
        -y|--yes)
            SKIP_CONFIRM=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production|testing)$ ]]; then
    echo -e "${RED}Error: Environment must be one of: development, staging, production, testing${NC}"
    exit 1
fi

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check PostgreSQL client
    if ! command -v psql &> /dev/null; then
        warn "PostgreSQL client (psql) not found. Database operations will be skipped."
    fi
    
    # Check Redis client
    if ! command -v redis-cli &> /dev/null; then
        warn "Redis client (redis-cli) not found. Redis operations will be skipped."
    fi
    
    log "System requirements check completed."
}

# Create .env.local file
create_env_file() {
    log "Setting up environment file for $ENVIRONMENT..."
    
    ENV_FILE="$PROJECT_ROOT/.env.local"
    EXAMPLE_FILE="$PROJECT_ROOT/.env.example"
    
    if [[ ! -f "$EXAMPLE_FILE" ]]; then
        error ".env.example file not found!"
        exit 1
    fi
    
    if [[ -f "$ENV_FILE" ]] && [[ "$SKIP_CONFIRM" == false ]]; then
        read -p ".env.local already exists. Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Skipping environment file creation."
            return
        fi
    fi
    
    # Copy example file
    cp "$EXAMPLE_FILE" "$ENV_FILE"
    
    # Update environment-specific values
    if [[ "$ENVIRONMENT" == "production" ]]; then
        sed -i.bak 's/ENVIRONMENT=development/ENVIRONMENT=production/' "$ENV_FILE"
        sed -i.bak 's/DEBUG=true/DEBUG=false/' "$ENV_FILE"
        sed -i.bak 's/LOG_LEVEL=DEBUG/LOG_LEVEL=INFO/' "$ENV_FILE"
        sed -i.bak 's/SENTRY_ENVIRONMENT=development/SENTRY_ENVIRONMENT=production/' "$ENV_FILE"
    elif [[ "$ENVIRONMENT" == "staging" ]]; then
        sed -i.bak 's/ENVIRONMENT=development/ENVIRONMENT=staging/' "$ENV_FILE"
        sed -i.bak 's/SENTRY_ENVIRONMENT=development/SENTRY_ENVIRONMENT=staging/' "$ENV_FILE"
    fi
    
    # Clean up backup file
    rm -f "$ENV_FILE.bak"
    
    log "Environment file created: $ENV_FILE"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    directories=(
        "uploads"
        "temp"
        "logs"
        "data"
    )
    
    for dir in "${directories[@]}"; do
        dir_path="$PROJECT_ROOT/$dir"
        if [[ ! -d "$dir_path" ]]; then
            mkdir -p "$dir_path"
            log "Created directory: $dir_path"
        fi
    done
}

# Setup Python virtual environment
setup_python_env() {
    log "Setting up Python environment..."
    
    if [[ ! -d "$PROJECT_ROOT/venv" ]]; then
        log "Creating Python virtual environment..."
        python3 -m venv "$PROJECT_ROOT/venv"
    fi
    
    source "$PROJECT_ROOT/venv/bin/activate"
    
    log "Installing/updating Python dependencies..."
    pip install --upgrade pip
    pip install -r "$PROJECT_ROOT/requirements.txt" || true
    
    log "Python environment setup completed."
}

# Create database
create_database() {
    if [[ "$CREATE_DATABASE" != true ]]; then
        return
    fi
    
    log "Checking database setup..."
    
    # Extract database connection details from .env.local
    ENV_FILE="$PROJECT_ROOT/.env.local"
    if [[ -f "$ENV_FILE" ]]; then
        source "$ENV_FILE"
    fi
    
    if [[ -z "$DATABASE_URL" ]]; then
        warn "DATABASE_URL not found in environment. Skipping database creation."
        return
    fi
    
    # Extract database name from URL
    DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\(.*\):.*/\1/p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_USER=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    
    log "Creating database: $DB_NAME"
    
    # Create database (requires superuser access)
    if command -v createdb &> /dev/null; then
        createdb "$DB_NAME" 2>/dev/null || warn "Database $DB_NAME already exists or creation failed"
    else
        warn "createdb command not found. Please create the database manually."
    fi
    
    # Create test database
    TEST_DB_NAME="${DB_NAME}_test"
    if command -v createdb &> /dev/null; then
        createdb "$TEST_DB_NAME" 2>/dev/null || warn "Test database $TEST_DB_NAME already exists or creation failed"
    fi
}

# Setup Redis
setup_redis() {
    if [[ "$SETUP_REDIS" != true ]]; then
        return
    fi
    
    log "Checking Redis configuration..."
    
    # Check if Redis is running
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            log "Redis is running and accessible"
        else
            warn "Redis is not running. Please start Redis server."
        fi
    fi
}

# Generate secrets
generate_secrets() {
    log "Checking for required secrets..."
    
    ENV_FILE="$PROJECT_ROOT/.env.local"
    
    # Check if secrets need to be generated
    if grep -q "your-super-secret-jwt-key-change-this-in-production" "$ENV_FILE"; then
        log "Generating new JWT secret..."
        NEW_JWT_SECRET=$(openssl rand -hex 32)
        sed -i.bak "s/your-super-secret-jwt-key-change-this-in-production/$NEW_JWT_SECRET/" "$ENV_FILE"
    fi
    
    if grep -q "your-super-secret-key-change-this-in-production" "$ENV_FILE"; then
        log "Generating new secret key..."
        NEW_SECRET=$(openssl rand -hex 32)
        sed -i.bak "s/your-super-secret-key-change-this-in-production/$NEW_SECRET/" "$ENV_FILE"
    fi
    
    if grep -q "your-32-character-encryption-key" "$ENV_FILE"; then
        log "Generating new encryption key..."
        NEW_ENCRYPTION_KEY=$(openssl rand -hex 16)
        sed -i.bak "s/your-32-character-encryption-key/$NEW_ENCRYPTION_KEY/" "$ENV_FILE"
    fi
    
    rm -f "$ENV_FILE.bak"
}

# Validate environment
validate_environment() {
    log "Validating environment configuration..."
    
    ENV_FILE="$PROJECT_ROOT/.env.local"
    
    if [[ -f "$ENV_FILE" ]]; then
        source "$ENV_FILE"
        
        # Check required variables
        required_vars=("DATABASE_URL" "SECRET_KEY" "JWT_SECRET" "ENCRYPTION_KEY")
        missing_vars=()
        
        for var in "${required_vars[@]}"; do
            if [[ -z "${!var}" ]] || [[ "${!var}" == *"change-this"* ]]; then
                missing_vars+=("$var")
            fi
        done
        
        if [[ ${#missing_vars[@]} -gt 0 ]]; then
            warn "Missing or invalid required environment variables:"
            for var in "${missing_vars[@]}"; do
                echo "  - $var"
            done
        else
            log "Environment validation completed successfully."
        fi
    fi
}

# Display next steps
show_next_steps() {
    echo ""
    echo -e "${BLUE}=== Setup Complete ===${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review and update .env.local with your actual values"
    echo "2. Start PostgreSQL: sudo systemctl start postgresql"
    echo "3. Start Redis: redis-server"
    echo "4. Run database migrations: alembic upgrade head"
    echo "5. Start the application: uvicorn api.main:app --reload"
    echo ""
    echo "To activate the Python environment:"
    echo "  source venv/bin/activate"
    echo ""
    echo "To run tests:"
    echo "  pytest tests/"
    echo ""
}

# Main execution
main() {
    log "Starting RuleIQ environment setup for $ENVIRONMENT..."
    
    check_requirements
    create_env_file
    create_directories
    setup_python_env
    create_database
    setup_redis
    generate_secrets
    validate_environment
    show_next_steps
    
    log "Environment setup completed successfully!"
}

# Run main function
main "$@"