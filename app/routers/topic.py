from fastapi import APIRouter, Depends, HTTPException, status
from services.topic import KafkaTopicService
from core.config import settings
from model.topic import CreateTopicRequest, UpdateTopicRequest, TopicInfoRequest, DeleteTopicRequest
from functools import lru_cache

router = APIRouter(prefix="/topic", tags=["topics"])



@lru_cache()
def get_kafka_service_singleton() -> KafkaTopicService:
    return KafkaTopicService(settings.KAFKA_BROKER)

def get_kafka_service(
    kafka_service: KafkaTopicService = Depends(get_kafka_service_singleton)
) -> KafkaTopicService:
    return kafka_service

@router.get(
    "/list",
    responses={
        status.HTTP_200_OK: {"description": "Successfully retrieved list of Kafka topics"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to fetch topics from Kafka broker"}
    }
)
def list_topics(topic_service: KafkaTopicService = Depends(get_kafka_service)):
    """Fetches all Kafka topics available in the broker."""
    try:
        return topic_service.list_topics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch topics: {str(e)}"
        )

@router.post(
    "/config",
    responses={
        status.HTTP_200_OK: {"description": "Successfully retrieved topic configuration"},
        status.HTTP_404_NOT_FOUND: {"description": "Topic not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to fetch topic configuration"}
    }
)
def get_topic_config(request: TopicInfoRequest, topic_service: KafkaTopicService = Depends(get_kafka_service)):
    """Fetches the configuration of a specific Kafka topic."""
    try:
        config = topic_service.get_topic_config(request.topic_name)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic '{request.topic_name}' not found"
            )
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch topic configuration: {str(e)}"
        )

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Topic successfully created"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid topic configuration"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to create topic"}
    }
)
def create_topic(request: CreateTopicRequest, topic_service: KafkaTopicService = Depends(get_kafka_service)):
    """Creates a Kafka topic dynamically with user-defined partitions, replication factor, and retention policies."""
    try:
        return topic_service.create_topic(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create topic: {str(e)}"
        )

@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Topic successfully deleted"},
        status.HTTP_404_NOT_FOUND: {"description": "Topic not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to delete topic"}
    }
)
def delete_topic(request: DeleteTopicRequest, topic_service: KafkaTopicService = Depends(get_kafka_service)):
    """Deletes a Kafka topic."""
    try:
        if not topic_service.get_topic_config(request.topic_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic '{request.topic_name}' not found"
            )
        topic_service.delete_topic(request.topic_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete topic: {str(e)}"
        )

@router.patch(
    "/update",
    responses={
        status.HTTP_200_OK: {"description": "Topic successfully updated"},
        status.HTTP_404_NOT_FOUND: {"description": "Topic not found"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid update request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to update topic"}
    }
)
def update_topic(request: UpdateTopicRequest, topic_service: KafkaTopicService = Depends(get_kafka_service)):
    """Updates the retention policies of an existing Kafka topic."""
    try:
        if not topic_service.get_topic_config(request.topic_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic '{request.topic_name}' not found"
            )
        return topic_service.update_topic(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update topic: {str(e)}"
        )
