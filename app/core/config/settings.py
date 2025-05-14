from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = "Token"
    OPENAI_API_URL: str = "https://models.github.ai/inference"
    MODEL_NAME: str = "openai/gpt-4o"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_FORMATS: list = ["jpg", "jpeg", "png"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()