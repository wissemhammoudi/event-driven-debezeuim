from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BROKER: str
    DEBEZIUM_CONNECTOR_URL: str
    class Config:
        # Specify the path to your .env file
        env_file = "./core/.env"
