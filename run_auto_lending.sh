#!/bin/bash

# Auto Lending Script for Bitfinex Funding
# This script runs the automated lending strategy using environment variables

set -e  # Exit on any error

# Log function
log() {
    # Ensure log directory exists
    mkdir -p "$(dirname "${LOG_FILE:-/app/logs/auto_lending.log}")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE:-/app/logs/auto_lending.log}"
}

# Error handler
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Check if automated lending is enabled
if [ "${AUTO_LENDING_ENABLED:-true}" != "true" ]; then
    log "Automated lending is disabled (AUTO_LENDING_ENABLED=false)"
    exit 0
fi

# Validate required environment variables
if [ -z "${BITFINEX_API_KEY}" ] || [ -z "${BITFINEX_API_SECRET}" ]; then
    error_exit "BITFINEX_API_KEY and BITFINEX_API_SECRET must be set"
fi

log "Starting automated lending process..."
log "Symbol: ${AUTO_LENDING_SYMBOL:-UST}"
log "Total Amount: ${AUTO_LENDING_TOTAL_AMOUNT:-3000}"
log "Min Order: ${AUTO_LENDING_MIN_ORDER:-150}"

# Build command arguments
CMD_ARGS=(
    "funding-lend-automation"
    "--symbol" "${AUTO_LENDING_SYMBOL:-UST}"
    "--total-amount" "${AUTO_LENDING_TOTAL_AMOUNT:-3000}"
    "--min-order" "${AUTO_LENDING_MIN_ORDER:-150}"
)

# Optional arguments
[ -n "${AUTO_LENDING_MAX_ORDERS}" ] && CMD_ARGS+=("--max-orders" "${AUTO_LENDING_MAX_ORDERS}")
[ -n "${AUTO_LENDING_RATE_INTERVAL}" ] && CMD_ARGS+=("--rate-interval" "${AUTO_LENDING_RATE_INTERVAL}")
[ -n "${AUTO_LENDING_TARGET_PERIOD}" ] && CMD_ARGS+=("--target-period" "${AUTO_LENDING_TARGET_PERIOD}")

# Boolean flags
[ "${AUTO_LENDING_CANCEL_EXISTING:-true}" = "true" ] && CMD_ARGS+=("--cancel-existing")
[ "${AUTO_LENDING_PARALLEL:-false}" = "true" ] && CMD_ARGS+=("--parallel")
[ -n "${AUTO_LENDING_MAX_WORKERS}" ] && CMD_ARGS+=("--max-workers" "${AUTO_LENDING_MAX_WORKERS}")
[ "${AUTO_LENDING_ALLOW_SMALL_ORDERS:-false}" = "true" ] && CMD_ARGS+=("--allow-small-orders")
[ "${AUTO_LENDING_NO_CONFIRM:-true}" = "true" ] && CMD_ARGS+=("--no-confirm")

# Log the command being executed (without sensitive info)
log "Executing: python cli.py ${CMD_ARGS[*]}"

# Execute the command
if python cli.py "${CMD_ARGS[@]}"; then
    log "Automated lending completed successfully"
else
    error_exit "Automated lending failed with exit code $?"
fi