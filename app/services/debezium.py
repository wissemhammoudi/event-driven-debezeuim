from pydantic import ValidationError
import httpx
from typing import Optional
from time import sleep
from model.debezium import DebeziumConnectorPayload
from functools import wraps
from core.config import Settings

# Load settings
settings = Settings()

# Decorator for error handling
def handle_debezium_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as ve:
            return {"error": f"Validation error: {str(ve)}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    return wrapper

class DebeziumService:
    def __init__(self):
        self.connector_url = settings.DEBEZIUM_CONNECTOR_URL  # Get URL from settings

    @handle_debezium_errors
    def start_producer_debezium(self, connector_payload: Optional[DebeziumConnectorPayload] = None):
        """
        Creates a Debezium connector by POSTing the provided payload, retrieves its configuration to construct the
        Kafka topic name, and starts a producer using that topic.
        
        Parameters:
            connector_payload (DebeziumConnectorPayload): Pydantic model instance for the connector payload.
        
        Returns:
            dict: A message indicating success or error details.
        """
        # Validate the payload using Pydantic
        connector_payload = DebeziumConnectorPayload(**connector_payload.dict())  # Ensures proper validation
        payload_dict = connector_payload.dict()
        json_payload = {
            "name": payload_dict["name"],
            "config": {str(key).replace("_", "."): value for key, value in payload_dict["config"].items()}
        }

        # Create the Debezium connector
        create_response = httpx.post(
            self.connector_url,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            json=json_payload,
            timeout=5.0
        )

        # Extract the response body, if successful
        response_json = create_response.json()
        return {"result": response_json}

    @handle_debezium_errors
    def list_debezium_connectors(self):
        """Get list of Debezium connectors."""
        response = httpx.get(
            self.connector_url,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=5.0
        )
        response.raise_for_status()
        return {"result": response.json()}

    @handle_debezium_errors
    def get_debezium_connector_info(self, connector_name: str):
        """Get details of a specific Debezium connector."""
        connector_info_url = f"{self.connector_url}/{connector_name}"
        response = httpx.get(connector_info_url, timeout=5.0)
        response.raise_for_status()
        return {"result": response.json()}

    @handle_debezium_errors
    def delete_debezium_connector(self, connector_name: str):
        """Delete a Debezium connector."""
        stop_url = f"{self.connector_url}/{connector_name}"
        stop_response = httpx.delete(
            stop_url,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=5.0
        )
        stop_response.raise_for_status()
        return {"result": f"Connector '{connector_name}' deleted successfully."}
