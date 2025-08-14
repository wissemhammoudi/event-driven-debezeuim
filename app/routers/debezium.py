from fastapi import APIRouter, HTTPException, status
from services.debezium import DebeziumService
from model.debezium import DebeziumConnectorPayload

router = APIRouter(prefix="/debezium", tags=["Debezium"])

debezium_service = DebeziumService()

@router.post(
    "/start/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Debezium connector successfully started"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid connector configuration"},
        status.HTTP_409_CONFLICT: {"description": "Connector with the same name already exists"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to start Debezium connector"}
    }
)
def start_producer(connector_payload: DebeziumConnectorPayload):
    """Starts a new Debezium connector with the provided configuration."""
    try:
        return debezium_service.start_producer_debezium(connector_payload=connector_payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start Debezium connector: {str(e)}"
        )

@router.get(
    "/list/",
    responses={
        status.HTTP_200_OK: {"description": "Successfully retrieved list of Debezium connectors"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to fetch Debezium connectors"}
    }
)
def list_debezium_connectors():
    """Lists all active Debezium connectors."""
    try:
        return debezium_service.list_debezium_connectors()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Debezium connectors: {str(e)}"
        )

@router.get(
    "/connector/{connector_name}/info/",
    responses={
        status.HTTP_200_OK: {"description": "Successfully retrieved Debezium connector info"},
        status.HTTP_404_NOT_FOUND: {"description": "Connector not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to fetch connector info"}
    }
)
def get_connector_info(connector_name: str):
    """Fetches information about a specific Debezium connector."""
    try:
        connector_info = debezium_service.get_debezium_connector_info(connector_name=connector_name)
        if not connector_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connector '{connector_name}' not found"
            )
        return connector_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch connector info: {str(e)}"
        )

@router.delete(
    "/connector/{connector_name}/delete/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Debezium connector successfully deleted"},
        status.HTTP_404_NOT_FOUND: {"description": "Connector not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to delete connector"}
    }
)
def stop_connector(connector_name: str):
    """Stops and deletes a specific Debezium connector."""
    try:
        if not debezium_service.get_debezium_connector_info(connector_name=connector_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connector '{connector_name}' not found"
            )
        debezium_service.delete_debezium_connector(connector_name=connector_name)
        return  # No content for 204 responses
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete connector: {str(e)}"
        )