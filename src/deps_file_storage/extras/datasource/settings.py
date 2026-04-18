from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from .constants import DBDialect, DBDriver

__all__ = ["DatabaseSettings"]


class SSLSettings(BaseSettings):
    key: str = ""
    cert: str = ""
    rootcert: str = ""
    mode: str = "verify-full"

    model_config = ConfigDict(env_prefix="DATABASE_SSL")


class DatabaseSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: str
    db: str
    ssl: SSLSettings = SSLSettings()
    dialect: DBDialect = DBDialect.POSTGRES
    driver: DBDriver = DBDriver.PSYCOPG2
    require_secure_transport: bool = False
    pool_size: int = 10

    model_config = ConfigDict(env_prefix="DATABASE_")
