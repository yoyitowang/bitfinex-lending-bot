#!/bin/bash

# Manual Auto Lending Runner
# This script allows you to run the automated lending manually
# Useful for testing or one-off executions

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if .env file exists
if [ ! -f "${SCRIPT_DIR}/.env" ]; then
    echo "Error: .env file not found. Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Load environment variables
set -a
source "${SCRIPT_DIR}/.env"
set +a

# Create logs directory if it doesn't exist
mkdir -p "${SCRIPT_DIR}/logs"

# Export log file path for the script
export LOG_FILE="${SCRIPT_DIR}/logs/auto_lending.log"

echo "Starting manual auto lending execution..."
echo "Log file: ${LOG_FILE}"
echo "Press Ctrl+C to cancel..."
echo ""

# Run the auto lending script
exec "${SCRIPT_DIR}/run_auto_lending.sh" "$@"