import json
import os
import random
import shutil
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from azure.storage.blob import BlobServiceClient
from google.cloud import storage
from google.oauth2 import service_account
from starlette.testclient import TestClient

from deps_file_storage.app import create_app
from deps_file_storage.constants import ALLOWED_FILE_EXTENSIONS
from deps_file_storage.dtos import File
from deps_file_storage.infrastructure.access_management.context_vars import user
from deps_file_storage.storage import (
    AsyncAzureStorageService,
    AzureStorageService,
    GCPStorageService,
)

from .config import CONFIG


@pytest.fixture(scope="module")
def app():
    app = create_app()

    yield app


@pytest.fixture(scope="function")
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def services(app):
    app.app.reset_singletons()
    yield app.app.containers


@pytest.fixture
def repositories(app):
    yield app.app.repositories


@pytest.fixture
def config(app):
    yield app.app.config


@pytest_asyncio.fixture
async def async_database(app):
    database = await app.app.datasources.async_database()

    yield database

    await database.close()


@pytest.fixture
def storage_service_access_manager(services):
    yield services.storage_service_access_manager


def recursive_delete_file_or_folders(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path)


@pytest.fixture(scope="module", autouse=True)
def clear_files_before_start(app):
    p = Path(app.app.config.media_root())
    p.mkdir(parents=True, exist_ok=True)

    dirs_and_files = map(lambda x: os.path.join(p, x), os.listdir(p))
    for i in dirs_and_files:
        recursive_delete_file_or_folders(i)

    yield


@pytest.fixture(scope="function", autouse=True)
def file_storage(app):
    yield

    p = Path(app.app.config.media_root())
    dirs_and_files = map(lambda x: os.path.join(p, x), os.listdir(p))
    for i in dirs_and_files:
        recursive_delete_file_or_folders(i)


@pytest.fixture(scope="function", autouse=False)
def gcp_storage_test_data():
    """Provides GCP storage blob service for tests. Cleans up bucket after tests are done"""
    service = GCPStorageService(CONFIG.get("BUCKET_NAME"), CONFIG.get("AUTH_KEY"), CONFIG.get("MEDIA_EXPIRES"))

    json_data = json.loads(CONFIG.get("AUTH_KEY"))
    project_id = json_data.get("project_id")
    credentials = service_account.Credentials.from_service_account_info(json_data)
    client = storage.Client(project_id, credentials)

    yield {
        "SERVICE": service,
        "BUCKET_NAME": CONFIG.get("BUCKET_NAME"),
        "AUTH_KEY": CONFIG.get("AUTH_KEY"),
        "STORAGE_CLIENT": client,
    }

    bucket = client.get_bucket(CONFIG.get("BUCKET_NAME"))
    bucket.delete_blobs(list(client.list_blobs(bucket)))


@pytest.fixture
def azure_storage_test_date(faker):
    """Provides Azure Storage Service for testing"""
    container_name = str(uuid4())
    blob_service = BlobServiceClient.from_connection_string(CONFIG.get("CONNECTION_STRING"))
    blob_service.create_container(container_name)

    file_path = faker.file_path()
    blob_client = blob_service.get_blob_client(container_name, blob=file_path)

    service = AzureStorageService(CONFIG.get("CONNECTION_STRING"), container_name)

    yield {
        "SERVICE": service,
        "BLOB_CLIENT": blob_client,
        "FILE_PATH": file_path,
    }

    blob_service.delete_container(container_name)


@pytest.fixture
def async_azure_storage_test_date(faker):
    """Provides Async Azure Storage Service for testing"""
    container_name = str(uuid4())
    blob_service = BlobServiceClient.from_connection_string(CONFIG.get("CONNECTION_STRING"))
    blob_service.create_container(container_name)

    file_path = faker.file_path()
    blob_client = blob_service.get_blob_client(container_name, blob=file_path)

    service = AsyncAzureStorageService(CONFIG.get("CONNECTION_STRING"), container_name)

    yield {
        "SERVICE": service,
        "BLOB_CLIENT": blob_client,
        "FILE_PATH": file_path,
    }

    blob_service.delete_container(container_name)


@pytest.fixture
def file_factory(faker):
    return lambda: File(
        filename=faker.file_name(extension=random.choice(ALLOWED_FILE_EXTENSIONS)),
        content=faker.text().encode(),
    )


@pytest.fixture
def file_factory_not_allowed_extension(faker):
    return lambda: File(
        filename=faker.file_name(category="audio"),
        content=faker.text().encode(),
    )


@pytest.fixture
def set_user_permission(config):
    config.authentication.storage_permission_rule.override("user")
    yield
    config.authentication.storage_permission_rule.override("none")


@pytest.fixture
def test_user():
    return {"subject": "test", "groups": ["test"], "organisation": "test"}


@pytest.fixture
def set_test_user(test_user):
    token = user.set(test_user)
    yield
    user.reset(token)


@pytest.fixture
def admin_user(config):
    admins_group = config.authentication.admins_group()
    return {"subject": "admin", "groups": [admins_group], "organisation": admins_group}


@pytest.fixture
def set_admin_user(admin_user):
    token = user.set(admin_user)
    yield
    user.reset(token)


@pytest.fixture
def storage_service_accessor(services):
    return services.storage_service_accessor()


@pytest.fixture
def async_access_manager(services):
    return services.async_storage_service_access_manager
