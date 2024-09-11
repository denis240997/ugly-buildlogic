import logging
from functools import lru_cache

# from pydantic import AnyUrl
from pydantic_settings import BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    static_dir: str = "static/"
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
