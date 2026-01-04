from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    CLERK_SIGNING_SECRET:str

    class Config:
        env_file = ".env"

settings = Settings()
