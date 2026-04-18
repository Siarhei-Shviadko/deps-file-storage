import pytest

from deps_file_storage.dtos import File
from deps_file_storage.exceptions import AlreadyExistException, NotFoundException
from deps_file_storage.storage import AsyncAzureStorageService

from .config import CONFIG


@pytest.mark.skip
class TestAsuncAzureStorageService:
    NOT_EXIST_FILE_PATH = "not_exist_file.txt"
    NOT_EXIST_CONTAINER = "not_exist_container"
    CONTENT = b"test async azure"

    def test__storage_not_exist_container__not_found_exception_is_raised(self):
        with pytest.raises(NotFoundException):
            AsyncAzureStorageService(CONFIG.get("CONNECTION_STRING"), self.NOT_EXIST_CONTAINER)

    def test__upload__file_is_uploaded(self, async_azure_storage_test_date):
        blob_client = async_azure_storage_test_date.get("BLOB_CLIENT")
        service = async_azure_storage_test_date.get("SERVICE")
        file_path = async_azure_storage_test_date.get("FILE_PATH")

        service.upload(file_path, self.CONTENT, False)

        assert blob_client.exists()

    def test__upload__content_is_overwritten(self, async_azure_storage_test_date):
        blob_client = async_azure_storage_test_date.get("BLOB_CLIENT")
        blob_client.upload_blob(self.CONTENT)
        service = async_azure_storage_test_date.get("SERVICE")
        file_path = async_azure_storage_test_date.get("FILE_PATH")
        new_content = b"new content"

        service.upload(file_path, new_content, True)

        assert blob_client.download_blob().readall() == new_content

    def test__upload__content_is_not_overwritten__already_exists_exception_is_raised(self, async_azure_storage_test_date):
        blob_client = async_azure_storage_test_date.get("BLOB_CLIENT")
        blob_client.upload_blob(self.CONTENT)
        service = async_azure_storage_test_date.get("SERVICE")
        file_path = async_azure_storage_test_date.get("FILE_PATH")
        new_content = b"new content"

        with pytest.raises(AlreadyExistException):
            service.upload(file_path, new_content, False)

    def test__download__content_is_correct(self, async_azure_storage_test_date):
        blob_client = async_azure_storage_test_date.get("BLOB_CLIENT")
        blob_client.upload_blob(self.CONTENT)
        service = async_azure_storage_test_date.get("SERVICE")
        file_path = async_azure_storage_test_date.get("FILE_PATH")

        assert service.download(file_path) == File(file_path, self.CONTENT)

    def test__download__wrong_path__not_found_exception_is_raised(self, async_azure_storage_test_date):
        service = async_azure_storage_test_date.get("SERVICE")

        with pytest.raises(NotFoundException):
            service.download(self.NOT_EXIST_FILE_PATH)

    def test__delete__file_is_deleted(self, async_azure_storage_test_date):
        blob_client = async_azure_storage_test_date.get("BLOB_CLIENT")
        blob_client.upload_blob(self.CONTENT)
        service = async_azure_storage_test_date.get("SERVICE")
        file_path = async_azure_storage_test_date.get("FILE_PATH")

        service.delete(file_path)

        assert not blob_client.exists()

    def test__delete__wrong_path__not_found_exception_is_raised(self, async_azure_storage_test_date):
        service = async_azure_storage_test_date.get("SERVICE")

        with pytest.raises(NotFoundException):
            service.delete(self.NOT_EXIST_FILE_PATH)

    def test__ping__wrong_container__not_found_exception_is_raised(self, async_azure_storage_test_date):
        service = async_azure_storage_test_date.get("SERVICE")

        with pytest.raises(NotFoundException):
            service.ping()

    def test__ping__container_exists(self, async_azure_storage_test_date):
        service = async_azure_storage_test_date.get("SERVICE")

        ping_result = service.ping()

        assert ping_result is None
