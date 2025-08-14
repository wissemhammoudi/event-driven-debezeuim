# Debezium Service Documentation

## Overview
The Debezium service manages PostgreSQL Change Data Capture (CDC) connectors that capture database changes and stream them to Kafka topics.

## Architecture
```
PostgreSQL → Debezium Connector → Kafka Topic
```

## Service Concepts

### Change Data Capture (CDC)
Debezium captures all changes (INSERT, UPDATE, DELETE) from PostgreSQL tables and converts them into events that are streamed to Kafka topics.

### Connector Lifecycle
1. **Initialization**: Connector starts and takes initial snapshot of tables
2. **Streaming**: Continuous monitoring of WAL (Write-Ahead Log) for changes
3. **Recovery**: Automatic recovery from failures with offset management
4. **Cleanup**: Graceful shutdown and resource cleanup

## Configuration Options

### Required Configuration
- `connector_class`: Must be `io.debezium.connector.postgresql.PostgresConnector`
- `database_hostname`: PostgreSQL server hostname
- `database_port`: PostgreSQL server port (default: 5432)
- `database_user`: Database username with replication privileges
- `database_password`: Database password
- `database_dbname`: Database name to monitor

### Optional Configuration
- `topic_prefix`: Prefix for Kafka topics (default: database name)
- `schema_include_list`: Specific schemas to monitor (default: all)
- `table_include_list`: Specific tables to monitor (default: all)
- `plugin_name`: PostgreSQL logical replication plugin (default: pgoutput)
- `snapshot_mode`: Snapshot behavior (initial, never, schema_only)

### Performance Tuning
- `tasks_max`: Maximum number of connector tasks
- `max_queue_size`: Maximum size of the change event queue
- `max_batch_size`: Maximum number of events in a batch
- `poll_interval_ms`: Polling interval for new changes

## PostgreSQL Requirements

### Database Configuration
```sql
-- Enable logical replication
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;

-- Restart PostgreSQL after changes
SELECT pg_reload_conf();
```

### User Permissions
```sql
-- Create dedicated user for Debezium
CREATE USER debezium WITH REPLICATION LOGIN PASSWORD 'password';

-- Grant necessary permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium;
GRANT USAGE ON SCHEMA public TO debezium;
```

### Publication Setup
```sql
-- Create publication for tables
CREATE PUBLICATION dbz_publication FOR TABLE public.users, public.orders;

-- Or auto-create publications
-- Set publication_autocreate_mode to 'filtered' in connector config
```

## Event Schema

### Change Event Structure
```json
{
  "schema": {
    "type": "struct",
    "fields": [
      {"field": "before", "type": "struct", "optional": true},
      {"field": "after", "type": "struct", "optional": true},
      {"field": "source", "type": "struct", "optional": false},
      {"field": "op", "type": "string", "optional": false},
      {"field": "ts_ms", "type": "int64", "optional": true}
    ]
  },
  "payload": {
    "before": null,
    "after": {"id": 1, "name": "John Doe", "email": "john@example.com"},
    "source": {
      "version": "2.4.0.Final",
      "connector": "postgresql",
      "name": "db.public.users",
      "ts_ms": 1640995200000,
      "snapshot": "false",
      "db": "mydatabase",
      "schema": "public",
      "table": "users",
      "txId": 12345,
      "lsn": 12345678
    },
    "op": "c",
    "ts_ms": 1640995200000
  }
}
```

### Operation Types
- `c`: Create (INSERT)
- `u`: Update (UPDATE)
- `d`: Delete (DELETE)
- `r`: Read (SNAPSHOT)

## API Reference
For complete API endpoint documentation, see [API Reference](../docs/api.md#debezium-endpoints).
