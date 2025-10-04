# Quick Start Guide for Bitfinex Lending Automation System

## Development Environment Setup

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git
- Node.js 18+ (for frontend development)

### Clone and Setup
```bash
# Clone repository
git clone <repository-url>
cd bitfinex-lending

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

### Database Setup
```bash
# Start PostgreSQL with Docker
docker run -d \
  --name postgres-lending \
  -e POSTGRES_DB=lending \
  -e POSTGRES_USER=lending \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:14

# Run migrations (future implementation)
alembic upgrade head
```

### Redis Setup
```bash
# Start Redis with Docker
docker run -d \
  --name redis-lending \
  -p 6379:6379 \
  redis:7-alpine
```

## Running the Application

### Development Mode
```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Or run individually
# Backend API
uvicorn presentation.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (if implemented)
cd frontend && npm run dev
```

### Production Mode
```bash
# Build and deploy
docker-compose up -d

# Check health
curl http://localhost:8000/health
curl http://localhost:3000  # Frontend
```

## API Usage Examples

### Authentication
```bash
# Login to get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```

### Lending Operations
```bash
# Get market data
curl http://localhost:8000/api/v1/market/fUSD

# Submit lending offer
curl -X POST http://localhost:8000/api/v1/lending/offers \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "fUSD",
    "amount": "1000.00",
    "rate": "0.00015",
    "period": 30
  }'

# Get portfolio
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/v1/portfolio
```

### WebSocket Real-time Data
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/market/fUSD');

// Handle market data updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Market update:', data);
};

// Handle connection events
ws.onopen = () => console.log('Connected to market data');
ws.onclose = () => console.log('Disconnected from market data');
```

## CLI Usage (Existing System)

### Basic Commands
```bash
# Activate virtual environment
source venv/bin/activate

# Get help
python cli.py --help

# Check market data
python cli.py funding-ticker --symbol USD

# View wallet balance
python cli.py wallets

# Submit lending offer
python cli.py funding-offer \
  --symbol fUSD \
  --amount 1000 \
  --rate 0.00015 \
  --period 30
```

### Automated Lending
```bash
# Run automated lending strategy
python cli.py funding-lend-automation \
  --symbol USD \
  --total-amount 5000 \
  --min-order 150 \
  --max-orders 20 \
  --no-confirm
```

## Development Workflow

### Code Quality Checks
```bash
# Run all quality checks
make quality

# Individual checks
black .                    # Code formatting
flake8 .                   # Linting
mypy .                     # Type checking
pytest                    # Unit tests
pytest --cov=.            # Coverage report
```

### API Documentation
```bash
# View interactive API docs
open http://localhost:8000/docs

# View alternative docs
open http://localhost:8000/redoc
```

### Database Operations
```bash
# Create migration
alembic revision --autogenerate -m "Add user preferences"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Configuration

### Environment Variables
```bash
# API Configuration
BITFINEX_API_KEY=your_api_key
BITFINEX_API_SECRET=your_api_secret

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/lending

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
SECRET_KEY=your-secret-key
DEBUG=True
LOG_LEVEL=INFO
```

### Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BITFINEX_API_KEY=${BITFINEX_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: lending
      POSTGRES_USER: lending
      POSTGRES_PASSWORD: password

  redis:
    image: redis:7-alpine
```

## Testing

### Unit Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_domain/

# Run with coverage
pytest --cov=domain --cov-report=html
```

### Integration Tests
```bash
# Run API integration tests
pytest tests/integration/

# Run end-to-end tests
pytest tests/e2e/
```

### Manual Testing
```bash
# Test API endpoints
curl -X GET http://localhost:8000/api/v1/health

# Test WebSocket connection
# Use browser developer tools or WebSocket client
```

## Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection string
python -c "import os; print(os.getenv('DATABASE_URL'))"
```

**API Authentication Failed**
```bash
# Verify environment variables
echo $BITFINEX_API_KEY
echo $BITFINEX_API_SECRET

# Test API credentials
python cli.py wallets
```

**WebSocket Connection Failed**
```bash
# Check if API server is running on port 8000
netstat -tlnp | grep 8000

# Verify CORS settings in logs
docker-compose logs api
```

**Memory Usage High**
```bash
# Monitor memory usage
docker stats

# Check for memory leaks in application
# Use memory profiling tools
```

### Logs and Debugging
```bash
# View API logs
docker-compose logs -f api

# View database logs
docker-compose logs -f postgres

# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose restart api
```

## Next Steps

1. **Complete Phase 1**: Finish architecture refactoring
2. **Phase 2**: Implement all API endpoints
3. **Phase 3**: Build React frontend
4. **Phase 4**: Deploy and test in production

## Resources

- [API Documentation](http://localhost:8000/docs)
- [Project Constitution](../constitution.md)
- [Architecture Overview](../spec.md)
- [Development Guide](../development.md)