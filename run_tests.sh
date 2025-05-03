#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Start PostgreSQL
echo -e "\n${GREEN}Starting PostgreSQL container...${NC}"
docker-compose --env-file .env.test up -d postgres

# Wait for PostgreSQL to be ready
echo -e "\n${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
for i in {1..30}; do
    if docker-compose --env-file .env.test exec postgres pg_isready -U test_user -d test_db > /dev/null 2>&1; then
        echo -e "${GREEN}PostgreSQL is ready!${NC}"
        break
    fi
    sleep 1
done

# Set up trap to ensure cleanup
trap 'docker-compose --env-file .env.test down' EXIT

# Run unit tests locally
echo -e "\n${GREEN}Running unit tests...${NC}"
pipenv run pytest tests/unit/ -v --cov=src --cov-report=term-missing
UNIT_TEST_STATUS=$?

# Run regular integration tests locally
echo -e "\n${GREEN}Running regular integration tests...${NC}"
pipenv run pytest tests/integration/ -v --cov=src --cov-report=term-missing
REGULAR_INTEGRATION_TEST_STATUS=$?

# Run Docker integration tests
echo -e "\n${GREEN}Running Docker integration tests...${NC}"
docker-compose --env-file .env.test up --build test_runner
DOCKER_INTEGRATION_TEST_STATUS=$?

# Generate coverage report
echo -e "\n${GREEN}Generating coverage report...${NC}"
pipenv run coverage html

# Check test results
if [ $UNIT_TEST_STATUS -eq 0 ] && [ $REGULAR_INTEGRATION_TEST_STATUS -eq 0 ] && [ $DOCKER_INTEGRATION_TEST_STATUS -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    if [ $UNIT_TEST_STATUS -ne 0 ]; then
        echo -e "\n${RED}Unit tests failed.${NC}"
    fi
    if [ $REGULAR_INTEGRATION_TEST_STATUS -ne 0 ]; then
        echo -e "\n${RED}Regular integration tests failed.${NC}"
    fi
    if [ $DOCKER_INTEGRATION_TEST_STATUS -ne 0 ]; then
        echo -e "\n${RED}Docker integration tests failed.${NC}"
    fi
    exit 1
fi 