#!/bin/bash
# AI Suite Local Test Runner
# Runs Phase 1 (Functional) + Phase 3 (Regression) tests locally
# Usage: ./scripts/run_tests.sh [phase1|phase3|all]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$ROOT_DIR/test_reports"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

mkdir -p "$REPORTS_DIR"

PHASE="${1:-all}"

run_phase() {
    local phase_num="$1"
    local test_file="$2"
    local phase_name="$3"
    
    echo -e "\n${CYAN}============================================${NC}"
    echo -e "${CYAN}  Phase $phase_num: $phase_name${NC}"
    echo -e "${CYAN}============================================${NC}\n"
    
    if [ ! -f "$ROOT_DIR/backend/tests/$test_file" ]; then
        echo -e "${RED}Test file not found: backend/tests/$test_file${NC}"
        return 1
    fi
    
    cd "$ROOT_DIR/backend"
    
    if python -m pytest "tests/$test_file" \
        -v --tb=short \
        --junitxml="$REPORTS_DIR/local_phase${phase_num}_results.xml" \
        2>&1; then
        echo -e "\n${GREEN}Phase $phase_num: PASSED${NC}"
        return 0
    else
        echo -e "\n${RED}Phase $phase_num: FAILED${NC}"
        return 1
    fi
}

PHASE1_RESULT=0
PHASE3_RESULT=0

if [ "$PHASE" = "phase1" ] || [ "$PHASE" = "all" ]; then
    run_phase 1 "test_phase1_functional.py" "Functional Testing (Gate G1)" || PHASE1_RESULT=1
fi

if [ "$PHASE" = "phase3" ] || [ "$PHASE" = "all" ]; then
    run_phase 3 "test_phase3_regression.py" "Post-Reliability Regression (Gate G3)" || PHASE3_RESULT=1
fi

echo -e "\n${CYAN}============================================${NC}"
echo -e "${CYAN}  Test Pipeline Summary${NC}"
echo -e "${CYAN}============================================${NC}"

if [ "$PHASE" = "phase1" ] || [ "$PHASE" = "all" ]; then
    if [ $PHASE1_RESULT -eq 0 ]; then
        echo -e "  Phase 1 (Functional):  ${GREEN}PASSED${NC}"
    else
        echo -e "  Phase 1 (Functional):  ${RED}FAILED${NC}"
    fi
fi

if [ "$PHASE" = "phase3" ] || [ "$PHASE" = "all" ]; then
    if [ $PHASE3_RESULT -eq 0 ]; then
        echo -e "  Phase 3 (Regression):  ${GREEN}PASSED${NC}"
    else
        echo -e "  Phase 3 (Regression):  ${RED}FAILED${NC}"
    fi
fi

echo -e "${CYAN}============================================${NC}"
echo -e "Reports saved to: $REPORTS_DIR/"

TOTAL=$((PHASE1_RESULT + PHASE3_RESULT))
if [ $TOTAL -eq 0 ]; then
    echo -e "\n${GREEN}ALL GATES PASSED${NC}"
    exit 0
else
    echo -e "\n${RED}GATE FAILURE - Fix issues before deploying${NC}"
    exit 1
fi
