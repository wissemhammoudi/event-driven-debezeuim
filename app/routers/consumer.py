from fastapi import APIRouter, Depends, HTTPException, status
from core.config import settings
from services.consumer import KafkaConsumerService
from functools import lru_cache
from model.consumer import ConsumerCreationRequest  

router = APIRouter(prefix="/consumer", tags=["consumer"])


@lru_cache()
def get_kafka_service_singleton() -> KafkaConsumerService:
    return KafkaConsumerService(settings.KAFKA_BROKER)

def get_kafka_service(
    kafka_service: KafkaConsumerService = Depends(get_kafka_service_singleton)
) -> KafkaConsumerService:
    return kafka_service

@router.post(
    "/start",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Consumer successfully started"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid consumer configuration"},
        status.HTTP_409_CONFLICT: {"description": "Consumer with the same ID already exists"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to start consumer"}
    }
)
def start_consumer(
    consumer_request: ConsumerCreationRequest, 
    kafka_service: KafkaConsumerService = Depends(get_kafka_service)
):
    """Starts a Kafka consumer with the provided configuration."""
    try:
        response = kafka_service.start_consumer(
            consumer_request  
        )
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start consumer: {str(e)}"
        )

@router.post(
    "/stop",
    response_model=dict,
    responses={
        status.HTTP_200_OK: {"description": "Consumer successfully stopped"},
        status.HTTP_404_NOT_FOUND: {"description": "Consumer not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to stop consumer"}
    }
)
def stop_consumer(
    consumer_id: str,
    kafka_service: KafkaConsumerService = Depends(get_kafka_service)
):
    """Stops a running Kafka consumer by its ID."""
    try:
        response = kafka_service.stop_consumer(consumer_id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consumer with ID '{consumer_id}' not found"
            )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop consumer: {str(e)}"
        )

@router.get(
    "/list",
    response_model=dict,
    responses={
        status.HTTP_200_OK: {"description": "Successfully retrieved list of consumers"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to fetch consumers"}
    }
)
def list_consumers(
    kafka_service: KafkaConsumerService = Depends(get_kafka_service)
):
    """Lists all running Kafka consumers."""
    try:
        response = kafka_service.list_consumers()
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch consumers: {str(e)}"
        )

@router.get(
    "/info/{consumer_id}",
    response_model=dict,
    responses={
        status.HTTP_200_OK: {"description": "Successfully retrieved consumer info"},
        status.HTTP_404_NOT_FOUND: {"description": "Consumer not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to fetch consumer info"}
    }
)
def get_consumer_info(
    consumer_id: str,
    kafka_service: KafkaConsumerService = Depends(get_kafka_service)
):
    """Retrieves information about a specific Kafka consumer by its ID."""
    try:
        response = kafka_service.get_consumer_info(consumer_id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consumer with ID '{consumer_id}' not found"
            )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch consumer info: {str(e)}"
        )