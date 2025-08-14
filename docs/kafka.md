# Kafka Service Documentation

## Overview
The Kafka service manages Apache Kafka topics, providing a distributed streaming platform for handling real-time data feeds. It serves as the central event broker in the event-driven data integration service.

## Architecture
```
Debezium Connector → Kafka Topic → Consumer Service
```

## Service Concepts

### Event Streaming
Kafka provides a distributed, fault-tolerant streaming platform that handles high-throughput, real-time data feeds with low latency.

### Topic Management
- **Partitioning**: Distributes data across multiple partitions for parallel processing
- **Replication**: Ensures data durability through multiple broker copies
- **Retention**: Configurable data retention policies for storage management

### Consumer Groups
- **Load Balancing**: Multiple consumers in a group share topic partitions
- **Fault Tolerance**: Automatic failover when consumers fail
- **Offset Management**: Tracks processing progress for each partition

## Topic Configuration

### Partition Strategy
- **Single Partition**: Sequential processing, guaranteed order
- **Multiple Partitions**: Parallel processing, improved throughput
- **Partition Key**: Ensures related events go to same partition

### Replication Factor
- **Replication Factor 1**: No redundancy (development only)
- **Replication Factor 3**: Recommended for production
- **Higher Factors**: Increased durability, reduced performance

### Retention Policies
- **Time-based**: Delete messages older than specified time
- **Size-based**: Delete messages when topic exceeds size limit
- **Compaction**: Keep only latest value for each key

### Debug Commands
```bash
# Check topic details
kafka-topics.sh --describe --topic my-topic --bootstrap-server localhost:9092

# Monitor consumer groups
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Check consumer lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group my-group --describe
```

## API Reference
For complete API endpoint documentation, see [API Reference](../docs/api.md#kafka-endpoints).
