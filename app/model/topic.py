from typing import Optional
from pydantic import BaseModel, Field

class TopicManagementBase(BaseModel):
    """Base model for topic-related requests"""
    topic_name: str = Field(
        ...,
        min_length=1,
        strip_whitespace=True,
        description="Name of the Kafka topic"
    )

class CreateTopicRequest(TopicManagementBase):
    """
    Request model for creating new Kafka topics with configurable partitioning
    """
    num_partitions: int = Field(
        default=1,
        ge=1,
        description="Number of partitions for parallelism"
    )
    replication_factor: int = Field(
        default=1,
        ge=1,
        description="Number of replicas for fault tolerance"
    )
    retention_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Retention time in milliseconds (7 days)"
    )
    retention_bytes: Optional[int] = Field(
        default=None,
        ge=0,
        description="Retention size in bytes (1GB)"
    )

class UpdateTopicRequest(TopicManagementBase):
    """
    Request model for updating topic retention policies
    """
    retention_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="New retention time in milliseconds"
    )
    retention_bytes: Optional[int] = Field(
        default=None,
        ge=0,
        description="New retention size in bytes"
    )

class TopicInfoRequest(TopicManagementBase):
    """Request model for retrieving topic information"""
    pass

class DeleteTopicRequest(TopicManagementBase):
    """Request model for deleting topics"""
    pass