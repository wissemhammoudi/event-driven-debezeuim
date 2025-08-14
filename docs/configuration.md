# Configuration Guide

## Overview
This guide covers all configuration aspects of the Event-Driven Data Integration Service, including environment variables, service configurations, and deployment settings.

## Environment Variables

### Core Service Configuration
```env
# Service Configuration
SERVICE_NAME=event-driven-service
SERVICE_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### Kafka Configuration
```env
# Kafka Broker Settings
KAFKA_BROKER=kafka:9092
KAFKA_ZOOKEEPER=zookeeper:2181
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# Kafka Admin Settings
KAFKA_ADMIN_TIMEOUT_MS=30000
KAFKA_ADMIN_REQUEST_TIMEOUT_MS=5000
KAFKA_ADMIN_RETRIES=3

# Kafka Consumer Settings
KAFKA_CONSUMER_GROUP_ID=event-driven-consumer
KAFKA_CONSUMER_AUTO_OFFSET_RESET=earliest
KAFKA_CONSUMER_ENABLE_AUTO_COMMIT=true
KAFKA_CONSUMER_AUTO_COMMIT_INTERVAL_MS=1000
```

### Debezium Configuration
```env
# Debezium Connector Settings
DEBEZIUM_CONNECTOR_URL=http://host.docker.internal:8083/connectors
DEBEZIUM_CONNECTOR_TIMEOUT=30000
DEBEZIUM_CONNECTOR_RETRIES=3

# PostgreSQL Connection Defaults
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
POSTGRES_USER=debezium
POSTGRES_PASSWORD=password
POSTGRES_DB=mydatabase
```

### Redis Configuration
```env
# Redis Connection Settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_SSL=false

# Redis Performance Settings
REDIS_MAX_CONNECTIONS=10
REDIS_CONNECTION_TIMEOUT=5
REDIS_SOCKET_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true
```

### PostgreSQL Configuration
```env
# PostgreSQL Connection Settings
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
POSTGRES_USER=debezium
POSTGRES_PASSWORD=password
POSTGRES_DB=mydatabase
POSTGRES_SSL_MODE=prefer
```

## Service Configuration Files

### Docker Compose Configuration
```yaml
version: '3.8'

services:
  kafka:
    image: confluentinc/cp-kafka:latest
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    container_name: zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  redis:
    image: redis:alpine
    container_name: redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes

  app:
    build: .
    container_name: event-driven-app
    ports:
      - "8000:8000"
    environment:
      - KAFKA_BROKER=kafka:9092
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - kafka
      - redis
```

### FastAPI Configuration
```python
# config/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "event-driven-service"
    service_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Kafka Configuration
    kafka_broker: str = "kafka:9092"
    kafka_zookeeper: str = "zookeeper:2181"
    kafka_security_protocol: str = "PLAINTEXT"
    
    # Debezium Configuration
    debezium_connector_url: str = "http://host.docker.internal:8083/connectors"
    debezium_connector_timeout: int = 30000
    debezium_connector_retries: int = 3
    
    # Redis Configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    
    # PostgreSQL Configuration
    postgres_host: str = "host.docker.internal"
    postgres_port: int = 5432
    postgres_user: str = "debezium"
    postgres_password: str = "password"
    postgres_db: str = "mydatabase"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## PostgreSQL Setup

### 1. Enable Logical Replication
Edit `postgresql.conf`:
```sql
# Replication Settings
wal_level = logical
max_replication_slots = 10
max_wal_senders = 10
max_logical_replication_workers = 4
max_worker_processes = 10

# Connection Settings
listen_addresses = '*'
port = 5432

# Memory Settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### 2. Create Replication Role
```sql
-- Create replication role
CREATE ROLE debezium WITH REPLICATION LOGIN PASSWORD 'password';

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO debezium;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO debezium;

-- Grant permissions for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO debezium;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO debezium;
```

### 3. Create Publication
```sql
-- Create publication for all tables
CREATE PUBLICATION dbz_publication FOR ALL TABLES;

-- Or create publication for specific tables
CREATE PUBLICATION dbz_publication FOR TABLE users, orders, products;
```

### 4. Test Table Setup
```sql
-- Create test table
CREATE TABLE person12 (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert test data
INSERT INTO person12 (name, email) VALUES 
    ('John Doe', 'john@example.com'),
    ('Jane Smith', 'jane@example.com');
```

## Kafka Configuration

### 1. Topic Configuration
```bash
# Create topics with specific configurations
docker exec -it kafka kafka-topics \
  --bootstrap-server kafka:9092 \
  --create \
  --topic db.public.person12 \
  --partitions 1 \
  --replication-factor 1 \
  --config retention.ms=604800000 \
  --config retention.bytes=1073741824
```

### 2. Consumer Group Configuration
```bash
# List consumer groups
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server kafka:9092 \
  --list

# Describe consumer group
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server kafka:9092 \
  --describe \
  --group event-driven-consumer
```

### 3. Broker Configuration
```properties
# server.properties
broker.id=1
listeners=PLAINTEXT://:9092
log.dirs=/var/lib/kafka/data
zookeeper.connect=zookeeper:2181
auto.create.topics.enable=true
delete.topic.enable=true
log.retention.hours=168
log.retention.bytes=1073741824
log.segment.bytes=1073741824
log.retention.check.interval.ms=300000
```

## Redis Configuration

### 1. Redis Configuration File
```conf
# redis.conf
bind 0.0.0.0
port 6379
timeout 0
tcp-keepalive 300
daemonize no
supervised no
pidfile /var/run/redis_6379.pid
loglevel notice
logfile ""
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
maxmemory 256mb
maxmemory-policy allkeys-lru
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

### 2. Redis Performance Tuning
```bash
# Monitor Redis performance
docker exec -it redis redis-cli info memory
docker exec -it redis redis-cli info stats
docker exec -it redis redis-cli info replication

# Check Redis configuration
docker exec -it redis redis-cli config get maxmemory
docker exec -it redis redis-cli config get maxmemory-policy
```

## Security Configuration

### 1. Network Security
```bash
# Firewall rules for production
sudo ufw allow 22/tcp          # SSH
sudo ufw allow 5432/tcp        # PostgreSQL
sudo ufw allow 9092/tcp        # Kafka
sudo ufw allow 6379/tcp        # Redis
sudo ufw allow 8000/tcp        # FastAPI
sudo ufw enable
```

### 2. SSL/TLS Configuration
```env
# Enable SSL for production
KAFKA_SECURITY_PROTOCOL=SSL
KAFKA_SSL_KEYSTORE_LOCATION=/path/to/keystore.jks
KAFKA_SSL_KEYSTORE_PASSWORD=keystore_password
KAFKA_SSL_KEY_PASSWORD=key_password

REDIS_SSL=true
REDIS_SSL_CERT_REQS=none
```

### 3. Authentication
```env
# Redis authentication
REDIS_PASSWORD=strong_password_here

# PostgreSQL authentication
POSTGRES_PASSWORD=strong_password_here

# Kafka authentication (if using SASL)
KAFKA_SECURITY_PROTOCOL=SASL_PLAINTEXT
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_JAAS_CONFIG=org.apache.kafka.common.security.plain.PlainLoginModule
```

## Monitoring Configuration

### 1. Health Check Endpoints
```python
# health_check.py
from fastapi import APIRouter, HTTPException
import redis
from kafka import KafkaAdminClient
import requests

router = APIRouter()

@router.get("/health")
async def health_check():
    services = {}
    
    # Check Redis
    try:
        redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port)
        redis_client.ping()
        services["redis"] = "healthy"
    except:
        services["redis"] = "unhealthy"
    
    # Check Kafka
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=settings.kafka_broker)
        admin_client.list_topics()
        services["kafka"] = "healthy"
    except:
        services["kafka"] = "unhealthy"
    
    # Check Debezium
    try:
        response = requests.get(settings.debezium_connector_url)
        if response.status_code == 200:
            services["debezium"] = "healthy"
        else:
            services["debezium"] = "unhealthy"
    except:
        services["debezium"] = "unhealthy"
    
    overall_status = "healthy" if all(v == "healthy" for v in services.values()) else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "services": services
    }
```

### 2. Logging Configuration
```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/app.log',
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Set specific log levels
    logging.getLogger('kafka').setLevel(logging.WARNING)
    logging.getLogger('redis').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
```

## Deployment Configuration

### 1. Production Environment
```env
# Production settings
DEBUG=false
LOG_LEVEL=WARNING
WORKERS=8

# Production Kafka
KAFKA_BROKER=prod-kafka:9092
KAFKA_SECURITY_PROTOCOL=SASL_SSL

# Production Redis
REDIS_HOST=prod-redis
REDIS_PASSWORD=prod_redis_password
REDIS_SSL=true

# Production PostgreSQL
POSTGRES_HOST=prod-postgres
POSTGRES_PASSWORD=prod_postgres_password
POSTGRES_SSL_MODE=require
```

### 2. Docker Production
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build: .
    container_name: event-driven-app-prod
    restart: unless-stopped
    environment:
      - DEBUG=false
      - LOG_LEVEL=WARNING
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    networks:
      - prod-network

networks:
  prod-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## Configuration Validation

### 1. Configuration Check Script
```python
# validate_config.py
import os
import sys
from config import settings

def validate_config():
    errors = []
    
    # Check required environment variables
    required_vars = [
        'KAFKA_BROKER',
        'REDIS_HOST',
        'POSTGRES_HOST'
    ]
    
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            errors.append(f"Missing required environment variable: {var}")
    
    # Check service connectivity
    try:
        import redis
        redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port)
        redis_client.ping()
    except Exception as e:
        errors.append(f"Redis connection failed: {e}")
    
    if errors:
        print("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("Configuration validation passed!")

if __name__ == "__main__":
    validate_config()
```

## Related Documentation
- [Debezium Service](./debezium.md)
- [Kafka Service](./kafka.md)
- [Consumer Service](./consumer.md)
- [Redis Service](./redis.md)
- [API Reference](./api.md)
