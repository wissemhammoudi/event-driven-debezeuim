from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional

class DebeziumConfig(BaseModel):
    connector_class: str = Field(..., description="The fully qualified class name of the Debezium connector.")
    tasks_max: str = Field(..., description="The maximum number of tasks the connector can use.")
    database_hostname: str = Field(..., description="The hostname of the database server.")
    database_port: str = Field(..., description="The port on which the database server is listening.")
    database_user: str = Field(..., description="The username to connect to the database.")
    database_password: str = Field(..., description="The password to connect to the database.")
    database_dbname: str = Field(..., description="The name of the database to capture changes from.")
    topic_prefix: str = Field(..., description="Prefix for the Kafka topics where changes will be written.")
    schema_include_list: Optional[str] = Field(None, description="Comma-separated list of schemas to include.")
    publication_autocreate_mode: Optional[str] = Field(None, description="Defines if Debezium should auto-create publications.")
    table_include_list: Optional[str] = Field(None, description="Comma-separated list of tables to include.")
    plugin_name: Optional[str] = Field(None, description="The logical decoding plugin name (e.g., pgoutput for PostgreSQL).")
    snapshot_mode: Optional[str] = Field(None, description="Specifies how the initial snapshot should be taken.")
    


class DebeziumConnectorPayload(BaseModel):
    name: str = Field(..., description="The name of the Debezium connector.")
    config: DebeziumConfig
