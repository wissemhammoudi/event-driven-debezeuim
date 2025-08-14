# API Reference Documentation

## Overview
This document provides a complete reference for all API endpoints in the Event-Driven Data Integration Service. All endpoints return JSON responses and use standard HTTP status codes.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication. In production, implement JWT tokens or API keys.

## Common Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {}
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "details": {}
}
```

## HTTP Status Codes

- `200` - OK: Request successful
- `201` - Created: Resource created successfully
- `204` - No Content: Request successful, no response body
- `400` - Bad Request: Invalid request data
- `404` - Not Found: Resource not found
- `409` - Conflict: Resource already exists
- `422` - Unprocessable Entity: Validation error
- `500` - Internal Server Error: Server error

## Debezium Endpoints

### Start Connector
```http
POST /debezium/start/
```

**Description**: Creates and starts a new Debezium connector.

**Request Body**:
```json
{
  "name": "string",
  "config": {
    "connector_class": "string",
    "tasks_max": "string",
    "database_hostname": "string",
    "database_port": "string",
    "database_user": "string",
    "database_password": "string",
    "database_dbname": "string",
    "topic_prefix": "string",
    "schema_include_list": "string",
    "publication_autocreate_mode": "string",
    "table_include_list": "string",
    "plugin_name": "string",
    "snapshot_mode": "string"
  }
}
```

**Response**:
- `201`: Connector started successfully
- `400`: Invalid configuration
- `409`: Connector already exists
- `500`: Server error

### List Connectors
```http
GET /debezium/list/
```

**Description**: Retrieves all active Debezium connectors.

**Response**:
- `200`: List of connectors
- `500`: Server error

### Get Connector Info
```http
GET /debezium/connector/{connector_name}/info/
```

**Description**: Fetches details of a specific connector.

**Path Parameters**:
- `connector_name`: Connector identifier

**Response**:
- `200`: Connector information
- `404`: Connector not found
- `500`: Server error

### Delete Connector
```http
DELETE /debezium/connector/{connector_name}/delete/
```

**Description**: Stops and removes a specific connector.

**Path Parameters**:
- `connector_name`: Connector identifier

**Response**:
- `204`: Connector deleted successfully
- `404`: Connector not found
- `500`: Server error

## Kafka Topic Endpoints

### List Topics
```http
GET /topic/list
```

**Description**: Retrieves all Kafka topics from the broker.

**Response**:
- `200`: Topics list retrieved successfully
- `500`: Failed to fetch topics

**Example Response**:
```json
{
  "topics": [
    "db.public.person12",
    "db.public.orders",
    "system-topic"
  ]
}
```

### Get Topic Configuration
```http
GET /topic/config?topic_name={topic_name}
```

**Description**: Fetches configuration details for a specific topic.

**Query Parameters**:
- `topic_name`: The name of the topic

**Response**:
- `200`: Topic configuration retrieved
- `404`: Topic not found
- `500`: Failed to fetch configuration

**Example Response**:
```json
{
  "topic_name": "db.public.person12",
  "num_partitions": 1,
  "replication_factor": 1,
  "retention_ms": 604800000,
  "retention_bytes": 1073741824
}
```

### Create Topic
```http
POST /topic/create
```

**Description**: Creates a new Kafka topic.

**Request Body**:
```json
{
  "topic_name": "my-topic",
  "num_partitions": 3,
  "replication_factor": 1,
  "retention_ms": 604800000,
  "retention_bytes": 1073741824
}
```

**Response**:
- `201`: Topic created successfully
- `400`: Invalid topic configuration
- `500`: Failed to create topic

### Update Topic
```http
PATCH /topic/update
```

**Description**: Updates the retention policies of an existing Kafka topic.

**Request Body**:
```json
{
  "topic_name": "my-topic",
  "retention_ms": 259200000,
  "retention_bytes": 536870912
}
```

**Response**:
- `200`: Topic successfully updated
- `400`: Invalid update request
- `404`: Topic not found
- `422`: Validation Error
- `500`: Failed to update topic

### Delete Topic
```http
DELETE /topic/delete?topic_name={topic_name}
```

**Description**: Removes a Kafka topic.

**Query Parameters**:
- `topic_name`: The name of the topic

**Response**:
- `204`: Topic deleted successfully
- `404`: Topic not found
- `500`: Failed to delete topic

## Consumer Endpoints

### Start Consumer
```http
POST /consumer/start
```

**Description**: Starts a new Kafka consumer with the specified configuration.

**Request Body**:
```json
{
  "consumer_id": "string",
  "kafka_topic": "string",
  "pipeline_name": "string",
  "connection_id": "string",
  "max_event": "integer",
  "max_time": "integer",
  "job_type": "string",
  "auto_offset_reset": "string"
}
```

**Response**:
- `201`: Consumer started successfully
- `400`: Invalid configuration
- `409`: Consumer already exists
- `500`: Server error

### Stop Consumer
```http
POST /consumer/stop?consumer_id={consumer_id}
```

**Description**: Stops a running Kafka consumer by its ID.

**Query Parameters**:
- `consumer_id`: Consumer identifier

**Response**:
- `200`: Consumer stopped successfully
- `404`: Consumer not found
- `422`: Validation error
- `500`: Server error

### List Consumers
```http
GET /consumer/list
```

**Description**: Lists all running Kafka consumers.

**Response**:
- `200`: List of consumers
- `500`: Server error

### Get Consumer Info
```http
GET /consumer/info/{consumer_id}
```

**Description**: Retrieves information about a specific consumer.

**Path Parameters**:
- `consumer_id`: Consumer identifier

**Response**:
- `200`: Consumer information
- `404`: Consumer not found
- `500`: Server error

## Health Check Endpoints

### Service Health
```http
GET /health
```

**Description**: Returns the overall health status of the service.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "debezium": "healthy",
    "kafka": "healthy",
    "redis": "healthy",
    "consumer": "healthy"
  }
}
```

### Service Status
```http
GET /health/{service_name}
```

**Description**: Returns the health status of a specific service.

**Path Parameters**:
- `service_name`: Service identifier (debezium, kafka, redis, consumer)

**Response**:
```json
{
  "service": "debezium",
  "status": "healthy",
  "details": {
    "connectors": 2,
    "uptime": "2h 30m"
  }
}
```

## Error Handling

### Validation Errors
When request validation fails, the API returns a `422` status with detailed error information:

```json
{
  "success": false,
  "error": "Validation failed",
  "details": {
    "field": "topic_name",
    "message": "Topic name is required"
  }
}
```

### Server Errors
Internal server errors return a `500` status with error details:

```json
{
  "success": false,
  "error": "Internal server error",
  "details": {
    "error_id": "uuid",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Rate Limiting
Currently, the API does not implement rate limiting. In production, consider implementing:
- Request rate limiting per IP
- API key-based rate limiting
- Burst protection

## CORS Configuration
The API supports Cross-Origin Resource Sharing (CORS) for web applications:

```json
{
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH",
  "Access-Control-Allow-Headers": "Content-Type, Authorization"
}
```

## API Versioning
The current API version is v1. Future versions will be available at `/api/v2/`, `/api/v3/`, etc.

## SDKs and Libraries

### Python Client
```python
import requests

class EventDrivenClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def start_connector(self, name, config):
        response = requests.post(
            f"{self.base_url}/debezium/start/",
            json={"name": name, "config": config}
        )
        return response.json()
    
    def create_topic(self, topic_config):
        response = requests.post(
            f"{self.base_url}/topic/create",
            json=topic_config
        )
        return response.json()
```

### JavaScript Client
```javascript
class EventDrivenClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async startConnector(name, config) {
        const response = await fetch(`${this.baseUrl}/debezium/start/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, config })
        });
        return response.json();
    }
}
```

## Testing

### Postman Collection
Import the following collection into Postman for testing:

```json
{
  "info": {
    "name": "Event-Driven Data Integration API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Debezium",
      "item": [
        {
          "name": "Start Connector",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/debezium/start/",
            "body": {
              "mode": "raw",
              "raw": "{\"name\":\"test-connector\",\"config\":{}}"
            }
          }
        }
      ]
    }
  ]
}
```

### cURL Examples
```bash
# Start a Debezium connector
curl -X POST http://localhost:8000/debezium/start/ \
  -H "Content-Type: application/json" \
  -d '{"name":"test-connector","config":{}}'

# Create a Kafka topic
curl -X POST http://localhost:8000/topic/create \
  -H "Content-Type: application/json" \
  -d '{"topic_name":"test-topic","num_partitions":1}'

# Start a consumer
curl -X POST http://localhost:8000/consumer/start \
  -H "Content-Type: application/json" \
  -d '{"consumer_id":"test-consumer","kafka_topic":"test-topic"}'
```

## Related Documentation
- [Debezium Service](./debezium.md)
- [Kafka Service](./kafka.md)
- [Consumer Service](./consumer.md)
- [Redis Service](./redis.md)
- [Configuration Guide](./configuration.md)

## Redis Endpoints

### Get Event Count
```http
GET /redis/count/{consumer_id}
```

**Description**: Retrieves the current event count for a specific consumer.

**Path Parameters**:
- `consumer_id`: The ID of the consumer

**Response**:
- `200`: Event count retrieved successfully
- `404`: Consumer not found
- `500`: Server error

**Example Response**:
```json
{
  "consumer_id": "consumer-1",
  "event_count": 45,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Reset Event Count
```http
POST /redis/reset/{consumer_id}
```

**Description**: Resets the event count for a specific consumer.

**Path Parameters**:
- `consumer_id`: The ID of the consumer

**Response**:
- `200`: Event count reset successfully
- `404`: Consumer not found
- `500`: Server error

### Get Consumer Status
```http
GET /redis/status/{consumer_id}
```

**Description**: Retrieves the current status and metadata for a specific consumer.

**Path Parameters**:
- `consumer_id`: The ID of the consumer

**Response**:
- `200`: Consumer status retrieved successfully
- `404`: Consumer not found
- `500`: Server error

**Example Response**:
```json
{
  "consumer_id": "consumer-1",
  "status": "RUNNING",
  "event_count": 45,
  "start_time": "2024-01-15T09:00:00Z",
  "last_event_time": "2024-01-15T10:30:00Z",
  "threshold_met": false
}
```

### List All Consumers
```http
GET /redis/consumers
```

**Description**: Lists all consumers with their current status and event counts.

**Response**:
- `200`: Consumer list retrieved successfully
- `500`: Server error

**Example Response**:
```json
{
  "consumers": [
    {
      "consumer_id": "consumer-1",
      "status": "RUNNING",
      "event_count": 45,
      "threshold_met": false
    },
    {
      "consumer_id": "consumer-2",
      "status": "STOPPED",
      "event_count": 0,
      "threshold_met": false
    }
  ]
}
```
