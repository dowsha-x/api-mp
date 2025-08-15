from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = 'secret'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACCESS_KEY: str
    SECRET_KEY_S: str
    ENDPOINT_URL: str
    BUCKET_NAME: str

    CELERY_BROKER_URL: str = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "rpc://"

    model_config = ConfigDict(env_file='.env', extra='allow')


settings = Settings()
