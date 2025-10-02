# Changelog

All notable changes to the Bitfinex Funding/Lending API Scripts will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.2] - 2025-10-02

### Added
- **Enhanced Order Cancellation**: New bulk cancellation capabilities
  - `cancel_funding_offers()` method for canceling multiple specific offers
  - `cancel-funding-offers` CLI command for bulk cancellation by offer IDs
  - Support for comma-separated offer ID lists
  - Individual error handling for each cancellation attempt

- **Improved Order Strategy Logic**: Fixed remaining amount handling
  - Corrected `generate_order_strategy()` to properly merge remaining amounts
  - Last order now includes leftover funds that don't fill complete minimum orders
  - Ensures full utilization of available lending balance

- **Smart Balance Calculation**: Enhanced lending automation balance checking
  - When `cancel_existing=True`, system now considers pending offers as available funds
  - Calculates "effective balance" = wallet_balance + pending_offers_total
  - Prevents false "insufficient balance" errors when offers will be cancelled first
  - More accurate balance validation for automation workflows

### Fixed
- **Order Amount Distribution**: Resolved issue where remaining amounts were ignored
  - Previously: 5 orders × $150 = $750 (ignoring $108.99 remainder)
  - Now: 4 orders × $150 + 1 order × $258.99 = $858.99 (full utilization)

- **Balance Validation Logic**: Fixed incorrect balance checking in automation
  - Previously: Only checked wallet balance, ignored pending offers that would be cancelled
  - Now: Considers effective balance when cancellation is enabled
  - Eliminates false "insufficient balance" errors

- **CLI Validation Order**: Fixed validation sequence in funding-lend-automation command
  - Previously: Validated total_amount=0 before converting to "use all available balance"
  - Now: Converts total_amount=0 to effective balance before validation
  - Properly handles "use all available balance" feature with pending offer cancellation

### Technical
- **API Enhancement**: Added bulk cancellation method to `AuthenticatedBitfinexAPI`
- **CLI Commands**: New command for canceling multiple offers with detailed results
- **Order Generation**: Improved algorithm for complete fund utilization

## [2.2.1] - 2025-10-02

### Fixed
- **Docker Permission Issues**: Resolved cron daemon permission errors in containers
  - Removed cron dependency that required root privileges
  - Implemented simple sleep-based loop for automated execution
  - Fixed log directory creation in automated scripts
  - Ensured non-root user compatibility

### Changed
- **Container Architecture**: Replaced cron with reliable loop-based automation
  - Maintains same functionality with improved stability
  - Better error handling and logging
  - Simplified container configuration

### Technical
- **Dependency Updates**: Removed unnecessary cron package from Dockerfile
- **Script Improvements**: Enhanced `run_auto_lending.sh` with automatic directory creation

## [2.2.0] - 2025-10-02

### Added
- **Complete Docker Containerization**: Full Docker and Docker Compose support
  - Production-ready Dockerfile with Python 3.9 slim base
  - Automated cron job configuration for scheduled lending
  - Environment variable-driven configuration system
  - Volume mounting for persistent logs and configuration

- **Automated Lending Scripts**: Comprehensive automation framework
  - `run_auto_lending.sh`: Environment-driven execution wrapper
  - `manual_run.sh`: Local manual execution utility
  - Error handling and retry mechanisms
  - Comprehensive logging system

- **Configuration System**: Flexible environment-based settings
  - Extensive `.env` configuration options
  - All automation parameters configurable via environment variables
  - Support for multiple execution modes (parallel/sequential)
  - Currency-specific and amount-specific configurations

- **Documentation Suite**: Complete documentation package
  - `DOCKER_README.md`: Detailed containerization guide
  - Installation, configuration, and troubleshooting guides
  - API usage examples and best practices
  - Security recommendations and monitoring guidance

### Changed
- **Project Structure**: Reorganized documentation into categorized files
  - Main README simplified to project overview
  - Detailed guides moved to `docs/` directory
  - Improved navigation and discoverability

### Technical
- **API Integration**: Enhanced error handling and rate limiting
- **Logging System**: Structured logging with configurable levels
- **Security**: Non-root container execution with proper permissions

## [2.1.0] - 2025-10-02

### Fixed
- **Nonce Collision Issues**: Resolved parallel processing nonce errors
  - Changed default processing to sequential for reliability
  - Individual API instances for parallel workers
  - Enhanced retry logic with exponential backoff
  - Optimized rate limiting (parallel: 20/min, sequential: 30/min)

### Added
- **Reliability Improvements**: Multiple layers of error prevention
  - Automatic nonce error detection and retry
  - Rate limit compliance with built-in delays
  - Comprehensive error messages with suggestions

### Changed
- **Processing Strategy**: Sequential processing as default for stability
- **Error Handling**: Improved error messages and recovery mechanisms

## [2.0.0] - 2025-10-02

### Changed
- **Focus Shift**: Complete removal of borrowing functionality
  - Dedicated exclusively to lending operations
  - Simplified codebase and reduced complexity
  - Enhanced lending-specific features

- **API Corrections**: Proper Bitfinex API endpoint usage
  - `get_funding_credits` for active lending positions (earning interest)
  - `get_funding_loans` for unused funds tracking
  - `get_funding_offers` for pending lending offers

### Added
- **Portfolio Analytics**: Enhanced lending portfolio statistics
  - Accurate income calculations from active positions only
  - Comprehensive risk metrics (concentration, duration, liquidity)
  - Unused funds visibility and tracking

- **Lending Optimization**: Improved lending strategy generation
  - Market-based rate discovery
  - Intelligent order ladder creation
  - Balance validation and adjustment

### Removed
- **Borrowing Features**: Complete removal of borrowing-related code
  - Simplified user interface
  - Reduced API complexity
  - Focused feature set

### Documentation
- **API Documentation**: Updated with correct endpoint explanations
- **Usage Examples**: Lending-focused examples and workflows

## [1.0.0] - 2025-10-02

### Added
- **Initial Release**: Core Bitfinex API integration
  - Public market data access (ticker, order book, trades)
  - Authenticated account operations (wallets, orders, positions)
  - Basic market analysis and strategy recommendations
  - Simple portfolio statistics and reporting

### Features
- **Market Data**: Real-time and historical funding market data
- **Account Management**: Wallet balances and position tracking
- **Order Management**: Submit and cancel funding offers
- **Analysis Tools**: Market statistics and basic recommendations
- **CLI Interface**: Command-line interface for all operations

---

## Version History Summary

- **2.2.2** (2025-10-02): Enhanced order cancellation and fixed order amount distribution
- **2.2.1** (2025-10-02): Docker permission fixes and stability improvements
- **2.2.0** (2025-10-02): Complete Docker containerization and automation framework
- **2.1.0** (2025-10-02): Parallel processing fixes and reliability enhancements
- **2.0.0** (2025-10-02): Lending-only focus with API corrections and portfolio improvements
- **1.0.0** (2025-10-02): Initial release with core Bitfinex API functionality

## Migration Guide

### From 2.1.x to 2.2.x
- Docker users: Update `docker-compose.yml` and rebuild containers
- Configuration: Review new environment variables in `docs/CONFIG.md`
- Scripts: Use new `run_auto_lending.sh` for automation

### From 2.0.x to 2.1.x
- Default processing changed to sequential
- Add `--parallel` flag if parallel processing is needed
- Review rate limiting changes

### From 1.x to 2.0.x
- Borrowing functionality removed
- Update API endpoint understanding
- Review portfolio calculations (now lending-only)

---

For detailed installation and usage instructions, see:
- [INSTALL.md](INSTALL.md) - Installation guide
- [USAGE.md](USAGE.md) - Command usage and examples
- [CONFIG.md](CONFIG.md) - Configuration options
- [DOCKER.md](DOCKER.md) - Docker deployment guide