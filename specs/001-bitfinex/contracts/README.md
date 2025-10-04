# API Contracts for Bitfinex Lending Automation System

This directory contains the API contract definitions for the lending automation system.

## Files

### lending-api.md
Contains the OpenAPI/Swagger specification for the REST API endpoints, including:
- Authentication endpoints
- Lending offer management
- Portfolio operations
- Market data access
- Real-time WebSocket specifications

### websocket-protocol.md
Defines the WebSocket communication protocol for real-time features:
- Market data streaming
- Order status updates
- Portfolio change notifications
- Connection management and error handling

### error-responses.md
Standardized error response formats and error codes used across all APIs:
- HTTP status codes mapping
- Error response schemas
- Client error handling guidelines

## API Design Principles

### RESTful Design
- Resource-based URLs (`/api/v1/lending/offers`)
- HTTP methods for CRUD operations
- Proper status codes and response formats
- HATEOAS links for discoverability

### Authentication
- JWT Bearer token authentication
- Refresh token mechanism
- Role-based access control
- API key fallback for programmatic access

### Real-time Communication
- WebSocket for live data updates
- Event-driven architecture
- Connection health monitoring
- Automatic reconnection handling

### Error Handling
- Consistent error response format
- Appropriate HTTP status codes
- Detailed error messages for debugging
- Client-friendly error categorization

## Versioning Strategy

- URL-based versioning: `/api/v1/`
- Semantic versioning for API changes
- Backward compatibility maintenance
- Deprecation notices for breaking changes

## Rate Limiting

- Per-user rate limits: 100 requests/minute
- Per-endpoint limits: Varies by operation complexity
- Burst handling with token bucket algorithm
- Clear rate limit headers in responses

## Data Formats

### Request/Response Format
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_12345"
  }
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": { ... },
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_12345"
  }
}
```

## Testing

### Contract Testing
- API contract validation using Dredd or similar tools
- Schema validation for all requests/responses
- Integration tests for end-to-end workflows

### Performance Testing
- Load testing for rate limit compliance
- Latency testing for real-time requirements
- Memory usage validation under load

These contracts ensure consistent API design and implementation across all platform interfaces.