from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    UPLOAD_FOLDER: str = 'uploads'

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()