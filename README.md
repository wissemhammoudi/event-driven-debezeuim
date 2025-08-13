
# Event-Driven Data Integration Service

## Overview
The **Event-Driven Data Integration Service** enables real-time data streaming and synchronization using **PostgreSQL, Debezium, Kafka, and Redis**. It captures changes from PostgreSQL through Debezium, streams them into Kafka topics, where events are aggregated in Redis. Once they exceed a specified threshold within a given timeframe, an automated data pipeline is triggered to load the processed data into the target system.

## Architecture
1. **PostgreSQL**: The primary database supporting Change Data Capture (CDC).
2. **Debezium**: Captures change events from PostgreSQL and streams them to Kafka.
3. **Kafka**: Serves as the central event broker, storing and distributing change events.
4. **Redis**: Caches events and aggregates counts. When the count exceeds a predefined threshold, it triggers the synchronization pipeline.
5. **FastAPI**: Provides API endpoints to manage Debezium connectors, Kafka topics, and consumers.
6. **Data Pipeline**: Loads processed data into the target system once the event threshold is surpassed.
### **Setup & Configuration (postgresql)**

**1. Enable Logical Replication:**

Logical replication allows streaming of data changes from a PostgreSQL database to external systems like Debezium. To enable it:

- **Modify `postgresql.conf`:** Set the `wal_level` parameter to `logical`. This setting determines the amount of information written to the Write-Ahead Log (WAL), and `logical` is required for logical replication.

```sql
  wal_level = logical

```

**2. Configure Replication Settings:**

Adjust the following parameters in `postgresql.conf` to support replication:

- **`max_replication_slots`:** Specifies the maximum number of replication slots that the server can support. A replication slot is a named, persistent reservation for a replication connection to send WAL data to a replica. Set this to at least the number of subscriptions expected to connect, plus some reserve for table synchronization.
- **`max_wal_senders`:** Sets the maximum number of simultaneously connected WAL sender processes. WAL sender processes are used to stream the WAL from the primary server to the replica. This should be set to at least the same as `max_replication_slots`, plus the number of physical replicas that are connected at the same time.
    
    Example settings:
    

```sql
  max_replication_slots = 10
  max_wal_senders = 10
```

**3. Create a Replication Role:**

A dedicated role with replication privileges is necessary for Debezium to connect and stream changes. In PostgreSQL, roles are entities that can own database objects and have database privileges; they can be considered as "users" or "groups" depending on how they are used. 

- **Create the Role:** Use the `CREATE ROLE` statement to define a new role with replication and login privileges. The `REPLICATION` attribute allows the role to initiate streaming replication, and the `LOGIN` attribute permits the role to log in to the database.

```sql
CREATE ROLE debezium WITH REPLICATION LOGIN PASSWORD 'password';
GRANT USAGE ON SCHEMA public TO debezium;
GRANT SELECT ON public.person12 TO debezium;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium;
ALTER ROLE debezium WITH REPLICATION;
GRANT CREATE ON DATABASE mydatabase TO debezium;
ALTER TABLE public.person12 OWNER TO debezium;

```
## Environment Configuration

Create a `.env` file in `./app/core/.env` with the following settings:

```env
KAFKA_BROKER="kafka:9092"
DEBEZIUM_CONNECTOR_URL="http://host.docker.internal:8083/connectors"
```

## Running the Service

### Prerequisites
- **Docker & Docker Compose** (for Kafka, Redis, and Debezium)
- **Python 3.9+** (for the FastAPI service)

### Setup & Execution
1. **Start Kafka, Zookeeper, FastAPI Service, and Debezium**  
   ```sh
   docker-compose up -d
   ```

## API Documentation

### Debezium Endpoints

#### Connector Management

##### Start Connector
```http
POST /debezium/start/
```
Creates and starts a new Debezium connector.

- **Request Body**: `DebeziumConnectorPayload`
  ```
    {
  "name": "my-postgres-connector",
  "config": {  
    "connector_class": "io.debezium.connector.postgresql.PostgresConnector",
    "tasks_max": "1",  
    "database_hostname": "host.docker.internal",  
    "database_port": "5432",  
    "database_user": "debezium",  
    "database_password": "password",  
    "database_dbname": "mydatabase",  
    "topic_prefix": "db",
    "schema_include_list": "public",
    "publication_autocreate_mode": "filtered",
    "table_include_list": "public.person12",
    "plugin_name": "pgoutput",
    "snapshot_mode": "initial"
  }
    }
  ```
- **Responses**:
  - `201`: Connector successfully started.
  - `400`: Invalid connector configuration.
  - `409`: Connector with the same name exists.
  - `500`: Internal server error.

##### List Connectors
```http
GET /debezium/list/
```
Retrieves all active Debezium connectors.

- **Responses**:
  - `200`: List of connectors retrieved successfully.
  - `500`: Failed to fetch connectors.

##### Get Connector Info
```http
GET /debezium/connector/{connector_name}/info/
```
Fetches details of a specific connector.

- **Path Parameter**:
  - `connector_name`: The name of the connector.
- **Responses**:
  - `200`: Connector information retrieved.
  - `404`: Connector not found.
  - `500`: Failed to fetch connector info.

##### Delete Connector
```http
DELETE /debezium/connector/{connector_name}/delete/
```
Stops and removes a specific connector.

- **Path Parameter**:
  - `connector_name`: The name of the connector.
- **Responses**:
  - `204`: Connector successfully deleted.
  - `404`: Connector not found.
  - `500`: Failed to delete connector.


### Kafka Topic Endpoints

#### Topic Management

##### List Topics
```http
GET /topic/list
```
Retrieves all Kafka topics from the broker.

- **Responses**:
  - `200`: Topics list retrieved successfully.
  - `500`: Failed to fetch topics.

##### Get Topic Configuration
```http
GET /topic/config?topic_name={topic_name}
```
Fetches configuration details for a specific topic.

- **Query Parameter**:
  - `topic_name`: The name of the topic.
- **Responses**:
  - `200`: Topic configuration retrieved.
  - `404`: Topic not found.
  - `500`: Failed to fetch configuration.

##### Create Topic
```http
POST /topic/create
```
Creates a new Kafka topic.

- **Request Body**: `CreateTopicRequest`
  ```json
  {
    "topic_name": "string",
    "num_partitions": 1,
    "replication_factor": 1,
    "retention_ms": 0,
    "retention_bytes": 0
  }
  ```
- **Responses**:
  - `201`: Topic created successfully.
  - `400`: Invalid topic configuration.
  - `500`: Failed to create topic.

##### Update Topic
```http
PATCH /topic/update
```
Updates the retention policies of an existing Kafka topic.

- **Request Body**: `UpdateTopicRequest`
  ```json
  {
    "topic_name": "string",
    "retention_ms": 0,
    "retention_bytes": 0
  }
  ```
- **Responses**:
  - `200`: Topic successfully updated.
  - `400`: Invalid update request.
  - `404`: Topic not found.
  - `422`: Validation Error.
  - `500`: Failed to update topic.

##### Delete Topic
```http
DELETE /topic/delete?topic_name={topic_name}
```
Removes a Kafka topic.

- **Query Parameter**:
  - `topic_name`: The name of the topic.
- **Responses**:
  - `204`: Topic deleted successfully.
  - `404`: Topic not found.
  - `500`: Failed to delete topic.


### Consumer Endpoints

#### Consumer Management

##### Start Consumer
```http
POST /consumer/start
```
Starts a new Kafka consumer with the specified configuration.

- **Request Body**: `ConsumerCreationRequest`
  ```json
{
  "consumer_id": "1",
  "kafka_topic": "db.person12",
  "pipeline_name": "firstPipeline",
  "connection_id": "string",
  "max_event": 10,
  "max_time": 3600,
  "job_type": "string",
  "auto_offset_reset": "earliest"
}
  ```
- **Responses**:
  - `201`: Consumer successfully started.
  - `400`: Invalid consumer configuration.
  - `409`: Consumer with the same ID exists.
  - `500`: Failed to start consumer.

##### Stop Consumer
```http
POST /consumer/stop?consumer_id={consumer_id}
```
Stops a running Kafka consumer by its ID.

- **Query Parameter**:
  - `consumer_id`: The ID of the consumer.
- **Responses**:
  - `200`: Consumer successfully stopped.
  - `404`: Consumer not found.
  - `422`: Validation Error.
  - `500`: Failed to stop consumer.

##### List Consumers
```http
GET /consumer/list
```
Lists all running Kafka consumers.

- **Responses**:
  - `200`: List of consumers retrieved successfully.
  - `500`: Failed to fetch consumers.

##### Get Consumer Info
```http
GET /consumer/info/{consumer_id}
```
Retrieves information about a specific consumer.

- **Path Parameter**:
  - `consumer_id`: The ID of the consumer.
- **Responses**:
  - `200`: Consumer information retrieved.
  - `404`: Consumer not found.
  - `500`: Failed to fetch consumer info.


## Usage Examples

### Debezium Operations

#### Create Connector
```bash
curl -X POST http://localhost:8000/debezium/start/ \
  -H "Content-Type: application/json" \
  -d '{
  "name": "my-postgres-connector",
  "config": {  
    "connector_class": "io.debezium.connector.postgresql.PostgresConnector",
    "tasks_max": "1",  
    "database_hostname": "host.docker.internal",  
    "database_port": "5432",  
    "database_user": "debezium",  
    "database_password": "password",  
    "database_dbname": "mydatabase",  
    "topic_prefix": "db",
    "schema_include_list": "public",
    "publication_autocreate_mode": "filtered",
    "table_include_list": "public.person12",
    "plugin_name": "pgoutput",
    "snapshot_mode": "initial"
  }
}
'
```

### Topic Operations

#### Create Topic
```bash
curl -X POST http://localhost:8000/topic/create \
  -H "Content-Type: application/json" \
  -d '{
    "topic_name": "my-topic",
    "num_partitions": 3,
    "replication_factor": 1,
    "retention_ms": 604800000,
    "retention_bytes": 1073741824
  }'
```

#### Update Topic
```bash
curl -X PATCH http://localhost:8000/topic/update \
  -H "Content-Type: application/json" \
  -d '{
    "topic_name": "my-topic",
    "retention_ms": 259200000,
    "retention_bytes": 536870912
  }'
```

### Consumer Operations

#### Start Consumer
```bash
curl -X POST http://localhost:8000/consumer/start \
  -H "Content-Type: application/json" \
  -d '{
  "consumer_id": "1",
  "kafka_topic": "db.public.person12",
  "pipeline_name": "first pipeline",
  "connection_id": "string",
  "max_event": 10,
  "max_time": 3600,
  "job_type": "sync",
  "auto_offset_reset": "earliest"
}'
```

#### Stop Consumer
```bash
curl -X POST "http://localhost:8000/consumer/stop?consumer_id=consumer-1" \
  -H "Content-Type: application/json"
```


 To check if the logic is working, you could retrieve all the data from Redis and verify whether it has been updated. This will confirm that our sync job has successfully processed the data.

You can use the following command to fetch all keys from Redis and display their values:

```sh
redis-cli --scan | while read key; do 
    type=$(redis-cli type "$key") 
    echo "Key: $key (Type: $type)"  
    case $type in
        string) redis-cli get "$key" ;;
        list) redis-cli lrange "$key" 0 5 ;;  # Limit to 5 items for readability
        set) redis-cli smembers "$key" ;;
        hash) redis-cli hgetall "$key" ;;
        zset) redis-cli zrange "$key" 0 5 withscores ;;
        *) echo "Unsupported type or empty key" ;;
    esac
    echo "----------------------"
done
```

This will list all keys stored in Redis along with their associated values, helping you confirm whether the data sync job has worked as expected.