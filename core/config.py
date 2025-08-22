from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    ACCESS_KEY: str
    SECRET_KEY_S: str
    ENDPOINT_URL: str
    BUCKET_NAME: str

    SECRET_KEY: str = 'secret'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = ConfigDict(env_file='.env', extra='allow')


settings = Settings()
