#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Start PostgreSQL
echo -e "\n${GREEN}Starting PostgreSQL container...${NC}"
docker-compose -f docker-compose.standalone-test.yml up -d postgres

# Wait for PostgreSQL to be ready
echo -e "\n${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
for i in {1..30}; do
    if docker-compose -f docker-compose.standalone-test.yml exec postgres pg_isready -U test_user -d test_db > /dev/null 2>&1; then
        echo -e "${GREEN}PostgreSQL is ready!${NC}"
        break
    fi
    sleep 1
done

# Set up trap to ensure cleanup
trap 'docker-compose -f docker-compose.standalone-test.yml down' EXIT

# Run all integration tests
echo -e "\n${GREEN}Running integration tests...${NC}"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/integration/ -v --integration
TEST_STATUS=$?

# Generate coverage report (optional - only if pytest-cov installed)
if command -v coverage &> /dev/null; then
    echo -e "\n${GREEN}Generating coverage report...${NC}"
    coverage html
fi

# Check test results
if [ $TEST_STATUS -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Tests failed.${NC}"
    exit 1
fi
