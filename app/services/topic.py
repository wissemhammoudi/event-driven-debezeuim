from fastapi import FastAPI
from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource, ResourceType
from typing import Optional
from functools import wraps
from model.topic import CreateTopicRequest,UpdateTopicRequest,DeleteTopicRequest,TopicInfoRequest
from pydantic import ValidationError
from fastapi import HTTPException
from confluent_kafka import KafkaException, KafkaError

def handle_kafka_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise HTTPException(status_code=400, detail=f"Validation error(s): {', '.join(error_messages)}")
        
        except KafkaException as e:
            error_code = e.args[0].code()
            if error_code == KafkaError.TOPIC_ALREADY_EXISTS:
                raise HTTPException(status_code=409, detail="Topic already exists.")
            raise HTTPException(status_code=500, detail=f"Kafka error: {str(e)}")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    return wrapper




# KafkaTopicService class
class KafkaTopicService:
    def __init__(self, kafka_broker: str):
        self.kafka_broker = kafka_broker  # Store the Kafka broker as an instance variable

    def get_admin_client(self):
        """Create and return an AdminClient instance using the stored Kafka broker."""
        return AdminClient({'bootstrap.servers': self.kafka_broker})

    @handle_kafka_errors
    def create_topic(self, request: CreateTopicRequest):
        """Creates a Kafka topic dynamically with user-defined partitions, replication factor, and retention policies."""
        admin_client = self.get_admin_client() 
        topic_name = request.topic_name.strip()
        if not topic_name:
            raise ValueError("Topic name cannot be empty.")
        
        # Check if topic already exists
        topic_metadata = admin_client.list_topics(timeout=10)
        if topic_name in topic_metadata.topics:
            raise HTTPException(status_code=409, detail=f"Topic '{topic_name}' already exists.")
        topic_name = request.topic_name
        num_partitions = request.num_partitions
        replication_factor = request.replication_factor
        retention_ms = request.retention_ms
        retention_bytes = request.retention_bytes

        config = {}
        if retention_ms is not None:
            config["retention.ms"] = str(retention_ms)
        if retention_bytes is not None:
            config["retention.bytes"] = str(retention_bytes)

        topic_list = [NewTopic(
            topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
            config=config
        )]

        futures = admin_client.create_topics(topic_list)
        for topic, future in futures.items():
            future.result(timeout=30)
        return {
            "message": f"Topic '{topic_name}' created successfully",
            "partitions": num_partitions,
            "replication_factor": replication_factor,
            "retention_policy": config
        }

    @handle_kafka_errors
    def list_topics(self):
        """Fetches all Kafka topics available in the broker."""
        admin_client = self.get_admin_client()  # Use the instance's kafka_broker
        topic_metadata = admin_client.list_topics(timeout=10)
        topics = list(topic_metadata.topics.keys())
        return {"topics": topics}

    @handle_kafka_errors
    def delete_topic(self, topic_name:str):
        """Deletes a Kafka topic."""
        topic_name = topic_name.strip()
        if not topic_name:
            raise ValueError("Topic name cannot be empty.")

        admin_client = self.get_admin_client()
        topic_metadata = admin_client.list_topics(timeout=10)

        if topic_name not in topic_metadata.topics:
            raise HTTPException(status_code=404, detail=f"Topic '{topic_name}' not found.")

        futures = admin_client.delete_topics([topic_name])
        for topic, future in futures.items():
            future.result(timeout=30)  # Ensure deletion completes

        return {"message": f"Topic '{topic_name}' deleted successfully"}

    @handle_kafka_errors
    def update_topic(self, request: UpdateTopicRequest):
        """Updates the retention policies of an existing Kafka topic."""
        topic_name = request.topic_name.strip()
        if not topic_name:
            raise ValueError("Topic name cannot be empty.")

        admin_client = self.get_admin_client()  # Use the instance's kafka_broker

        config = {}
        if request.retention_ms is not None:
            config["retention.ms"] = str(request.retention_ms)
        if request.retention_bytes is not None:
            config["retention.bytes"] = str(request.retention_bytes)

        if not config:
            raise ValueError("At least one retention policy must be specified.")

        resources = [ConfigResource(ResourceType.TOPIC, topic_name, config)]
        futures = admin_client.alter_configs(resources)
        for resource, future in futures.items():
            future.result(timeout=30)

        return {"message": f"Topic '{topic_name}' updated successfully with new retention policies"}

    @handle_kafka_errors
    def get_topic_config(self, topic_name:str):
        """Fetches the configuration of a specific Kafka topic."""
        topic_name = topic_name.strip()
        if not topic_name:
            raise ValueError("Topic name cannot be empty.")

        admin_client = self.get_admin_client()
        topic_metadata = admin_client.list_topics(timeout=10)
        if topic_name not in topic_metadata.topics:
            raise HTTPException(status_code=404, detail=f"Topic '{topic_name}' not found.")

        config_resource = ConfigResource(ResourceType.TOPIC, topic_name)
        futures = admin_client.describe_configs([config_resource])
        result = futures[config_resource].result()

        configs = {
            key: {
                "value": entry.value,
                "source": str(entry.source),
                "is_default": entry.is_default,
                "is_read_only": entry.is_read_only,
                "is_sensitive": entry.is_sensitive
            }
            for key, entry in result.items() if not entry.is_default
        }

        return {"topic_name": topic_name, "config": configs}
