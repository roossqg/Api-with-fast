from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from typing import Annotated


# class with server-api configured
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )  # link database

    DATABASE_URL: Annotated[str,'db_url'] = os.getenv('DATABASE_URL')
    # db object format
    ALGORITHM: Annotated[str,'alg'] = os.getenv('ALGORITHM')
    SECRET_KEY: Annotated[str,'key'] = os.getenv('SECRET_KEY')
    ACESSS_TOKEN_EXPIRE_MINUTES: Annotated[str,'token'] = os.getenv(
        'ACESSS_TOKEN_EXPIRE_MINUTES')


# preset
settings = Settings()
