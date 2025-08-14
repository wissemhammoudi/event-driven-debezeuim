from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class OffsetResetStrategy(str, Enum):
    EARLIEST = "earliest"
    LATEST = "latest"
    
class ConsumerCreationRequest(BaseModel):
    """
    Request model for creating a new Kafka consumer with configurable polling behavior.
    
    Attributes:
        consumer_id: Unique identifier for the consumer group
        kafka_topic: Target topic to consume messages from
        pipeline_name: Associated pipeline name for monitoring
        max_event: Maximum number of events to poll per batch
        max_time: Maximum time in ms to wait for messages
        auto_offset_reset: Offset reset policy when no offset exists
    """
    consumer_id: str = Field(..., min_length=1)
    kafka_topic: str = Field(..., min_length=1)
    pipeline_name: str = Field(..., min_length=1)
    max_event: int = Field(..., gt=0)
    max_time: int = Field(..., gt=0)
    auto_offset_reset: Optional[OffsetResetStrategy] = Field(
        default=OffsetResetStrategy.EARLIEST,
        description="What to do when there is no initial offset in Kafka"
    )