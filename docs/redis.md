# Redis Service Documentation

## Overview
The Redis service provides in-memory data caching and event aggregation for the event-driven data integration service. It stores event counts, triggers pipeline execution, and provides fast data access for real-time operations.

## Architecture
```
Consumer Service → Redis Cache → Event Aggregation → Pipeline Trigger
```

## Service Concepts

### In-Memory Caching
Redis provides ultra-fast data access by storing frequently used data in memory, significantly reducing latency compared to disk-based storage.

### Event Aggregation
- **Counter Management**: Track event counts per consumer and time window
- **Threshold Monitoring**: Trigger pipelines when thresholds are exceeded
- **Time-based Aggregation**: Aggregate events within configurable time windows


## Data Structures

### Key-Value Storage
- **Event Counters**: Track event counts per consumer
- **Configuration**: Store service configuration
- **Session Data**: Cache user sessions and tokens
- **Cache Data**: Frequently accessed data


## Event Aggregation

### Counter Logic
```python
# Event counter implementation
def increment_event_counter(consumer_id):
    key = f"consumer:{consumer_id}:events"
    count = redis.incr(key)
    
    # Set expiration for automatic cleanup
    redis.expire(key, 86400)  # 24 hours
    
    return count

def get_event_count(consumer_id):
    key = f"consumer:{consumer_id}:events"
    count = redis.get(key)
    return int(count) if count else 0
```

### Threshold Monitoring
```python
# Threshold checking
def check_thresholds(consumer_id, max_events, max_time):
    event_key = f"consumer:{consumer_id}:events"
    time_key = f"consumer:{consumer_id}:start_time"
    
    event_count = int(redis.get(event_key) or 0)
    start_time = float(redis.get(time_key) or time.time())
    current_time = time.time()
    
    # Check event threshold
    if event_count >= max_events:
        return "EVENT_THRESHOLD"
    
    # Check time threshold
    if (current_time - start_time) >= max_time:
        return "TIME_THRESHOLD"
    
    return None
```

### Time Window Management
```python
# Time-based aggregation
def aggregate_events_by_time(consumer_id, time_window):
    current_time = int(time.time())
    window_start = current_time - time_window
    
    # Get events within time window
    events = redis.zrangebyscore(
        f"consumer:{consumer_id}:events_timeline",
        window_start,
        current_time
    )
    
    return len(events)
```

### Debug Commands
```bash
# Check Redis info
redis-cli info

# Monitor commands in real-time
redis-cli monitor

# Check memory usage
redis-cli info memory

# Analyze key patterns
redis-cli --scan --pattern "*"
```

## API Reference
For complete API endpoint documentation, see [API Reference](../docs/api.md#redis-endpoints).
