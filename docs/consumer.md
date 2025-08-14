# Consumer Service Documentation

## Overview
The Consumer service manages Kafka consumers that process events from topics and trigger data pipelines when thresholds are met. It handles event aggregation, monitoring, and automated pipeline execution.

## Architecture
```
Kafka Topic → Consumer Service → Redis Aggregation → Pipeline Trigger
```

## Service Concepts

### Event Consumption
The consumer service continuously polls Kafka topics for new events, processes them according to business logic, and aggregates them for pipeline triggering.

### Threshold Management
- **Event Count Thresholds**: Trigger pipelines after processing a specified number of events
- **Time-based Thresholds**: Trigger pipelines after a specified time period
- **Combined Thresholds**: Trigger when either count or time threshold is met

### Pipeline Integration
- **Automatic Triggering**: Seamlessly trigger data pipelines when thresholds are exceeded
- **Pipeline Selection**: Route events to appropriate pipelines based on configuration
- **Status Tracking**: Monitor pipeline execution and consumer health

## Consumer Lifecycle

### Initialization
1. **Configuration Loading**: Load consumer settings and pipeline mappings
2. **Kafka Connection**: Establish connection to Kafka broker
3. **Offset Management**: Set initial offset position
4. **Redis Setup**: Initialize event counters and thresholds

### Runtime Operation
1. **Event Polling**: Continuously poll Kafka topics for new events
2. **Event Processing**: Process events according to business logic
3. **Counter Increment**: Update Redis counters for threshold monitoring
4. **Pipeline Triggering**: Automatically trigger pipelines when thresholds met

### Shutdown
1. **Graceful Stop**: Complete current event processing
2. **Offset Commit**: Save current processing position
3. **Resource Cleanup**: Release connections and resources
4. **Status Update**: Update consumer status in monitoring systems

## Configuration Options

### Required Parameters
- `consumer_id`: Unique identifier for the consumer
- `kafka_topic`: Kafka topic to consume from
- `pipeline_name`: Name of the pipeline to trigger
- `connection_id`: Database connection identifier
- `max_event`: Maximum number of events before triggering pipeline
- `max_time`: Maximum time (seconds) before triggering pipeline

### Optional Parameters
- `job_type`: Type of job (sync, async, batch)
- `auto_offset_reset`: Offset reset strategy (earliest, latest)
- `batch_size`: Number of events to process in each batch
- `poll_timeout`: Timeout for Kafka polling operations

### Advanced Configuration
- `retry_policy`: Retry strategy for failed events
- `error_handling`: Error handling and dead letter queue configuration
- `monitoring`: Metrics collection and alerting settings
- `security`: Authentication and authorization settings

## Event Processing

### Event Flow
```python
# Event processing pipeline
def process_event(event):
    # Parse event data
    event_data = parse_event(event)
    
    # Apply business logic
    processed_data = apply_business_logic(event_data)
    
    # Update counters
    increment_event_counter(consumer_id)
    
    # Check thresholds
    if check_thresholds(consumer_id, max_events, max_time):
        trigger_pipeline(pipeline_name, processed_data)
    
    return processed_data
```


### Debug Commands
```bash
# Check consumer status
curl http://localhost:8000/consumer/info/consumer-1

# Monitor consumer logs
docker logs consumer-service

# Check Redis counters
redis-cli get "consumer:consumer-1:events"

# Verify Kafka connectivity
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic my-topic
```

## API Reference
For complete API endpoint documentation, see [API Reference](../docs/api.md#consumer-endpoints).
