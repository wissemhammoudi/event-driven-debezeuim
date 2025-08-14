from pydantic_settings import BaseSettings, Field

class Settings(BaseSettings):
    """
    Central application configuration for Kafka and Debezium connectivity.
    """
    
    KAFKA_BROKER: str = Field(
        default="localhost:9092",
        env="KAFKA_BROKER",
    )
    
    DEBEZIUM_CONNECTOR_URL: str = Field(
        default="http://localhost:8083",
        env="DEBEZIUM_CONNECTOR_URL",  
    )

    class Config:
        env_file = "./core/.env"

settings = Settings()