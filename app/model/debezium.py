from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional
from enum import Enum

class DatabaseType(str, Enum):
    POSTGRES = "postgres"
    MYSQL = "mysql"
    SQLSERVER = "sqlserver"

class DebeziumConfig(BaseModel):
    """
    Configuration model for Debezium connector setup with database-specific parameters.
    """
    connector_class: str = Field(
        default="io.debezium.connector.postgresql.PostgresConnector",
        description="Fully qualified class name of the Debezium connector"
    )
    tasks_max: str = Field(
        default="1",
        description="Maximum number of tasks the connector can use"
    )
    database_hostname: str = Field(
        ...,
        example="postgres-host",
        description="Hostname of the database server"
    )
    database_port: str = Field(
        ...,
        example="5432",
        description="Port number of the database server"
    )
    database_user: str = Field(
        ...,
        example="debezium",
        description="Username for database connection"
    )
    database_password: str = Field(
        ...,
        description="Password for database connection",
        sensitive=True
    )
    database_dbname: str = Field(
        ...,
        example="production_db",
        description="Name of the database to monitor"
    )
    topic_prefix: str = Field(
        ...,
        example="inventory",
        description="Prefix for Kafka topics containing changes"
    )
    schema_include_list: Optional[str] = Field(
        default=None,
        example="public,audit",
        description="Comma-separated schemas to include"
    )
    table_include_list: Optional[str] = Field(
        default=None,
        example="public.orders,public.customers",
        description="Comma-separated tables to include"
    )
    plugin_name: Optional[str] = Field(
        default="pgoutput",
        description="Logical decoding plugin name"
    )
    snapshot_mode: Optional[str] = Field(
        default="initial",
        description="Behavior for initial snapshot"
    )

    @validator('connector_class')
    def validate_connector_class(cls, v):
        valid_connectors = {
            "postgres": "io.debezium.connector.postgresql.PostgresConnector",
            "mysql": "io.debezium.connector.mysql.MySqlConnector"
        }
        if v not in valid_connectors.values():
            raise ValueError(f"Invalid connector class. Must be one of: {', '.join(valid_connectors.values())}")
        return v

class DebeziumConnectorPayload(BaseModel):
    """
    Payload model for creating/updating Debezium connectors via REST API
    """
    name: str = Field(
        ...,
        example="inventory-connector",
        description="Unique name for the connector"
    )
    config: DebeziumConfig = Field(
        ...,
        description="Complete configuration for the connector"
    )