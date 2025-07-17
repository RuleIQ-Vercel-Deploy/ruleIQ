#!/bin/bash

# Script to set up the PostgreSQL database for RuleIQ
# This script should be run with appropriate PostgreSQL permissions

echo "Setting up RuleIQ database..."

# Database configuration
DB_NAME="ruleiq_test"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}This script will help set up the PostgreSQL database for RuleIQ.${NC}"
echo -e "${YELLOW}You may need to enter your PostgreSQL admin password.${NC}"
echo ""

# Function to check if database exists
check_database_exists() {
    sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$1"
}

# Function to create database
create_database() {
    echo -e "${GREEN}Creating database '$DB_NAME'...${NC}"
    sudo -u postgres createdb "$DB_NAME"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Database '$DB_NAME' created successfully!${NC}"
    else
        echo -e "${RED}Failed to create database '$DB_NAME'.${NC}"
        return 1
    fi
}

# Check if database exists
if check_database_exists "$DB_NAME"; then
    echo -e "${YELLOW}Database '$DB_NAME' already exists.${NC}"
    read -p "Do you want to drop and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Dropping database '$DB_NAME'...${NC}"
        sudo -u postgres dropdb "$DB_NAME"
        create_database
    fi
else
    create_database
fi

# Set password for postgres user (optional)
echo ""
echo -e "${YELLOW}Do you want to set/update the password for the 'postgres' user?${NC}"
read -p "Enter new password (or press Enter to skip): " -s NEW_PASSWORD
echo

if [ ! -z "$NEW_PASSWORD" ]; then
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD '$NEW_PASSWORD';"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Password updated successfully!${NC}"
        echo -e "${YELLOW}Please update the DATABASE_URL in your .env file with the new password:${NC}"
        echo -e "DATABASE_URL=postgresql://postgres:$NEW_PASSWORD@localhost:5432/ruleiq_test"
    else
        echo -e "${RED}Failed to update password.${NC}"
    fi
fi

# Test connection
echo ""
echo -e "${YELLOW}Testing database connection...${NC}"
if [ ! -z "$NEW_PASSWORD" ]; then
    PGPASSWORD="$NEW_PASSWORD" psql -U postgres -h localhost -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1
else
    # Try with no password first
    psql -U postgres -h localhost -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database connection successful!${NC}"
else
    echo -e "${RED}Database connection failed. Please check your PostgreSQL configuration.${NC}"
    echo -e "${YELLOW}Common issues:${NC}"
    echo "1. PostgreSQL service is not running"
    echo "2. Password authentication is not configured in pg_hba.conf"
    echo "3. The postgres user password is incorrect"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"