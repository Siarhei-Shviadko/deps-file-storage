import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, ClassVar, List

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import (
    ConfigDict,
    DirectoryPath,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings

from deps_file_storage.extras.datasource import DatabaseSettings
from deps_file_storage.extras.settings import (
    AuthenticationSettings as BaseAuthenticationSettings,
)
from deps_file_storage.extras.settings import ServiceInfoSettings
from deps_file_storage.infrastructure.access_management.constants import (
    StoragePermissionRuleEnum,
)


class GCPStorageSettings(BaseSettings):
    bucket_name: str | None = Field(None, env="GCP_BLOB_STORAGE_BUCKET_NAME")
    auth_key: str | None = Field(None, env="GCP_BLOB_STORAGE_AUTH_KEY")
    media_expires: str | None = Field(None, env="MEDIA_EXPIRES")
    use_emulator: bool = Field(default=False, env="GCP_BLOB_USE_EMULATOR")
    storage_emulator_host: str | None = Field(None, env="STORAGE_EMULATOR_HOST")

    @field_validator("storage_emulator_host")
    @classmethod
    def validate_host_env(cls, v, info):
        if info.data.get("use_emulator") and not v:
            raise ValidationError("STORAGE_EMULATOR_HOST should be set to use emulator")
        return v


class S3StorageSettings(BaseSettings):
    aws_access_key_id: str = Field("", env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field("", env="AWS_SECRET_ACCESS_KEY")
    s3_endpoint_url: str | None = Field(None, env="S3_ENDPOINT_URL")
    s3_bucket_name: str = Field("", env="S3_BUCKET_NAME")


class AzureStorageSettings(BaseSettings):
    connection_string: str = Field("", env="AZURE_CONNECTION_STRING")
    container_name: str = Field("", env="AZURE_CONTAINER_NAME")


class AuthenticationSettings(BaseAuthenticationSettings):
    admins_group: str
    storage_permission_rule: StoragePermissionRuleEnum = Field(
        StoragePermissionRuleEnum.NONE,
        env="ACCESS_MODE",
    )

    @field_validator("storage_permission_rule")
    @classmethod
    def validate_document_permission_rule(cls, v, info):
        if v != StoragePermissionRuleEnum.NONE and not info.data.get("enabled"):
            raise ValueError("Please enable auth to limit access to documents")
        return v


class BlobStorageSettings(BaseSettings):
    default_storage: str = "FILE_STORAGE"

    root_dir: DirectoryPath = Path(__file__).resolve().parent

    max_content_length: int = 20 * 1024 * 1024  # noqa: WPS43

    # File Storage
    media_root: Path = Field("media/files")

    logger_level: int = Field("INFO", env="FILE_STORAGE_LOGGER_LEVEL")

    acceptable_mimetypes: List[str] = Field(
        default=[
            "image/jpeg",
            "image/png",
            "application/csv",
            "application/pdf",
            "application/json",
            "application/octet-stream",
            "application/vnd.ms-outlook",
            "message/rfc822",
            "text/plain",
            "text/html",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
            "application/vnd.ms-excel",  # .xls
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
            "application/msword",
        ],
        env="ACCEPTABLE_MIMETYPES",
    )

    GUNICORN_WORKERS: ClassVar[int] = 1
    GUNICORN_THREADS: ClassVar[int] = 2
    GUNICORN_BIND: ClassVar[str] = "0.0.0.0:8004"
    GUNICORN_RELOAD: ClassVar[bool] = True

    gcp_storage: GCPStorageSettings = GCPStorageSettings()
    s3_storage: S3StorageSettings = S3StorageSettings()
    azure_storage: AzureStorageSettings = AzureStorageSettings()

    authentication: AuthenticationSettings = AuthenticationSettings()

    database: DatabaseSettings = DatabaseSettings()

    service_info: ServiceInfoSettings = ServiceInfoSettings()

    env: str

    messaging_driver: MessagingDriverEnum = Field(MessagingDriverEnum.RABBITMQ, env="MESSAGING_DRIVER")
    messaging_driver_settings: Any = Field(None, env="MESSAGING_DRIVER_SETTINGS")
    message_broker_connection_string: str
    rabbitmq_dlx_per_queue: bool = Field(False, env="RABBITMQ_DLX_PER_QUEUE")  # noqa: WPS425

    cipher_key: bytes = Field(b"", env="CIPHER_KEY")
    documentation_enabled: bool = True
    files_deletion_enabled: bool = True

    instrumentation_enabled: bool = False

    # Feature flags
    feature_async_file_storage: bool = Field(False, env="FEATURE_ASYNC_FILE_STORAGE")  # noqa: WPS425

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("logger_level", mode="before")
    @classmethod
    def convert_logging_level_str_to_int(cls, value):
        if isinstance(value, int) and value in logging._levelToName:  # noqa: WPS437
            return value

        if value not in logging._nameToLevel:  # noqa: WPS437
            raise ValueError(f"Invalid logger_level '{value}'")

        return logging._nameToLevel[value]  # noqa: WPS437

    @field_validator("messaging_driver_settings")
    @classmethod
    def validate_messaging_driver_settings(cls, v, info):  # noqa: N805
        messaging_driver = info.data.get("messaging_driver")
        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().model_dump()  # TODO: use BaseSettings

        raise ValueError(f"Driver {driver} is not implemented")

    @model_validator(mode="before")
    @classmethod
    def convert_acceptable_mimetypes(cls, values: dict[str, Any]) -> dict[str, Any]:  # noqa: N805
        acceptable_mimetypes = values.pop("acceptable_mimetypes", None)
        if acceptable_mimetypes is not None and isinstance(acceptable_mimetypes, str):
            values["acceptable_mimetypes"] = acceptable_mimetypes.splitlines()

        return values


@lru_cache()
def get_settings() -> BlobStorageSettings:
    return BlobStorageSettings()
