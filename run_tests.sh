#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Running tests..."

# Run unit tests
echo -e "\n${GREEN}Running unit tests...${NC}"
pipenv run pytest tests/unit/ -v --cov=src --cov-report=term-missing

# Run integration tests
echo -e "\n${GREEN}Running integration tests...${NC}"
pipenv run pytest tests/integration/ -v --cov=src --cov-report=term-missing

# Generate coverage report
echo -e "\n${GREEN}Generating coverage report...${NC}"
pipenv run coverage html

# Check if all tests passed
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
else
    echo -e "\n${RED}Some tests failed.${NC}"
    exit 1
fi 