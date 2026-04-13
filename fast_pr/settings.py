from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# class with server-api configured
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )  # link database

    DATABASE_URL: Annotated[str, Field(init=False)]  # db object format
    ALGORITHM: Annotated[str, Field(init=False)]
    SECRET_KEY: Annotated[str, Field(init=False)]
    ACESSS_TOKEN_EXPIRE_MINUTES: Annotated[int, Field(init=False)]


# preset
settings = Settings()
