import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://faouz:faouz2020@localhost:5436/clients_db")
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    api_key: str = os.getenv("API_KEY", "dev-key-change-in-prod")

    class Config:
        env_file = ".env"


settings = Settings()
