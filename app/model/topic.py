# Pydantic model for topic creation
from pydantic import BaseModel, Field
from typing import Optional


class CreateTopicRequest(BaseModel):
    topic_name: str = Field(..., min_length=1, strip_whitespace=True, description="Name of the Kafka topic")
    num_partitions: int = Field(default=1, ge=1, description="Number of partitions for the topic")
    replication_factor: int = Field(default=1, ge=1, description="Replication factor for the topic")
    retention_ms: Optional[int] = Field(default=None, ge=0, description="Retention time in milliseconds")
    retention_bytes: Optional[int] = Field(default=None, ge=0, description="Retention size in bytes")



class UpdateTopicRequest(BaseModel):
    topic_name: str = Field(..., min_length=1, strip_whitespace=True, description="Name of the Kafka topic")  
    retention_ms: Optional[int] = Field(default=None, ge=0, description="Retention time in milliseconds")
    retention_bytes: Optional[int] = Field(default=None, ge=0, description="Retention size in bytes")

class TopicInfoRequest(BaseModel):
    topic_name: str

class DeleteTopicRequest(BaseModel):
    topic_name: str