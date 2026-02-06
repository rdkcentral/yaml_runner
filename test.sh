#!/bin/bash
# yaml_runner test runner
# Usage: ./test.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Running yaml_runner tests...${NC}\n"

# Ensure package is available for tests by adding src to PYTHONPATH
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"

# Run all unit tests
echo -e "${YELLOW}Running unit tests...${NC}"
python3 -m unittest discover -s unittests -p "*tests.py" -v

echo -e "\n${GREEN}✓ All tests completed${NC}"
