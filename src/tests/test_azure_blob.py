import pytest

from deps_file_storage.dtos import File
from deps_file_storage.exceptions import AlreadyExistException, NotFoundException
from deps_file_storage.storage import AzureStorageService

from .config import CONFIG


@pytest.mark.skip
class TestAzureStorageService:
    INVALID_FILE_PATH = "invalid.txt"
    INVALID_CONTAINER = "invalid"
    CONTENT = b"spoilt pug test"

    def test__storage_not_exist__not_found_exception_is_raised(self):
        with pytest.raises(NotFoundException):
            AzureStorageService(CONFIG.get("CONNECTION_STRING"), self.INVALID_CONTAINER)

    def test_upload__file_is_uploaded(self, azure_storage_test_date):
        blob_client = azure_storage_test_date.get("BLOB_CLIENT")
        service = azure_storage_test_date.get("SERVICE")
        file_path = azure_storage_test_date.get("FILE_PATH")

        service.upload(file_path, self.CONTENT, False)

        assert blob_client.exists()

    def test_upload__content_is_overwritten(self, azure_storage_test_date):
        blob_client = azure_storage_test_date.get("BLOB_CLIENT")
        blob_client.upload_blob(self.CONTENT)
        service = azure_storage_test_date.get("SERVICE")
        file_path = azure_storage_test_date.get("FILE_PATH")
        new_content = b"new content"

        service.upload(file_path, new_content, True)

        assert blob_client.download_blob().readall() == new_content

    def test_upload__content_is_not_overwritten__already_exists_exception_is_raised(self, azure_storage_test_date):
        blob_client = azure_storage_test_date.get("BLOB_CLIENT")
        blob_client.upload_blob(self.CONTENT)
        service = azure_storage_test_date.get("SERVICE")
        file_path = azure_storage_test_date.get("FILE_PATH")
        new_content = b"new content"

        with pytest.raises(AlreadyExistException):
            service.upload(file_path, new_content, False)

    def test_download__content_is_correct(self, azure_storage_test_date):
        blob_client = azure_storage_test_date.get("BLOB_CLIENT")
        blob_client.upload_blob(self.CONTENT)
        service = azure_storage_test_date.get("SERVICE")
        file_path = azure_storage_test_date.get("FILE_PATH")

        assert service.download(file_path) == File(file_path, self.CONTENT)

    def test_download__wrong_path__not_found_exception_is_raised(self, azure_storage_test_date):
        service = azure_storage_test_date.get("SERVICE")

        with pytest.raises(NotFoundException):
            service.download(self.INVALID_FILE_PATH)

    def test_delete__file_is_deleted(self, azure_storage_test_date):
        blob_client = azure_storage_test_date.get("BLOB_CLIENT")
        blob_client.upload_blob(self.CONTENT)
        service = azure_storage_test_date.get("SERVICE")
        file_path = azure_storage_test_date.get("FILE_PATH")

        service.delete(file_path)

        assert not blob_client.exists()

    def test_delete__wrong_path__not_found_exception_is_raised(self, azure_storage_test_date):
        service = azure_storage_test_date.get("SERVICE")

        with pytest.raises(NotFoundException):
            service.delete(self.INVALID_FILE_PATH)
