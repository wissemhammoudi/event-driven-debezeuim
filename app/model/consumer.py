from typing import Optional
from pydantic import BaseModel

class ConsumerCreationRequest(BaseModel):
    consumer_id: str
    kafka_topic: str
    pipeline_name: str
    max_event: int
    max_time:int
    auto_offset_reset: Optional[str] = "earliest"  # Defaulting to "earliest"
