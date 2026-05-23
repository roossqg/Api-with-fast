from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


# class with server-api configured
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )  # link database

    DATABASE_URL = os.getenv('DATABASE_URL')
    # db object format
    ALGORITHM = os.getenv('ALGORITHM')
    SECRET_KEY = os.getenv('SECRET_KEY')
    ACESSS_TOKEN_EXPIRE_MINUTES = os.getenv('ACESSS_TOKEN_EXPIRE_MINUTES')


# preset
settings = Settings()
