from pydantic import ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings

__all__ = ["AuthenticationSettings", "Settings", "ServiceInfoSettings"]


class AuthenticationSettings(BaseSettings):
    enabled: bool = Field(False, env="AUTH_ENABLED")
    verify_ssl: bool = Field(True, env="AUTH_VERIFY_SSL")
    certs_endpoint: str | None = Field(None, env="AUTH_CERTS_ENDPOINT")
    encryption_algorithm: str = Field("RS256", env="AUTH_ENCRYPTION_ALGORITHM")
    api_key: str | None = Field(None, env="API_KEY")

    @model_validator(mode="after")
    def validate_certs_endpoint_and_key(self):
        if self.enabled and (self.certs_endpoint is None and self.api_key is None):
            raise ValueError(
                "Please provide OAUTH certificates endpoint via `AUTH_CERTS_ENDPOINT` " "or provide auth key via `API_KEY`",
            )
        return self


class ServiceInfoSettings(BaseSettings):
    tag: str = ""
    date: str = ""
    hash: str = ""

    model_config = ConfigDict(env_prefix="SERVICE_INFO_")


class Settings(BaseSettings):
    info: ServiceInfoSettings = ServiceInfoSettings()
    auth: AuthenticationSettings = AuthenticationSettings()
    ocr_api_url: str | None = Field(None, env="OCR_API_URL")
    file_storage_url: str | None = Field(None, env="FILE_STORAGE_URL")
    tables_api_url: str | None = Field(None, env="TABLES_API_URL")
    omr_service_url: str | None = Field(None, env="OMR_SERVICE_URL")
    debug_mode: bool = Field(False, env="DEBUG_MODE")
