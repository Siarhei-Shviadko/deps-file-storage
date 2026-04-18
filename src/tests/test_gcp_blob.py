import tempfile

import pytest

from deps_file_storage.exceptions import NotFoundException
from deps_file_storage.storage import GCPStorageService


@pytest.mark.skip
class TestGCPStorageBlobService:
    INITIAL_FILE_PATH = "test.txt"
    CONTAINER_PATH = "test"
    FILE_CONTENT = b"The quick brown fox jumps over the lazy dog"

    def test__storage_does_not_exist__raises_blob_not_found_exception(self, gcp_storage_test_data):
        auth_key = gcp_storage_test_data.get("AUTH_KEY")
        with pytest.raises(NotFoundException):
            GCPStorageService("some_non_existing_bucket_name", auth_key, 2)

    def test_upload_content__file_uploaded(self, gcp_storage_test_data):
        _, test_file_path = tempfile.mkstemp()
        client = gcp_storage_test_data.get("STORAGE_CLIENT")
        bucket = client.get_bucket(gcp_storage_test_data.get("BUCKET_NAME"))
        file_path = self._get_file_path()
        blob_before_upload = bucket.blob(file_path)
        assert not blob_before_upload.exists()

        blob_service = gcp_storage_test_data.get("SERVICE")
        new_file_name = blob_service.upload(file_path, open(test_file_path, "rb").read())
        blob = bucket.blob(new_file_name)
        assert blob.exists()

    def test_download__file_does_not_exist__raises_blob_not_found_exception(self, gcp_storage_test_data):
        blob_service = gcp_storage_test_data.get("SERVICE")
        with pytest.raises(NotFoundException):
            blob_service.download(self._get_file_path())

    def test_download__file_added__content_is_correct(self, gcp_storage_test_data):
        _, test_file_path = tempfile.mkstemp()
        self._prepare_file_content(test_file_path)

        blob_service = gcp_storage_test_data.get("SERVICE")
        file_path = self._get_file_path()
        new_file_path = blob_service.upload(file_path, open(test_file_path, "rb").read())

        file_content = blob_service.download(new_file_path).content
        assert file_content == self.FILE_CONTENT

    def _get_file_path(self) -> str:
        return "/".join([self.CONTAINER_PATH, self.INITIAL_FILE_PATH])

    def _prepare_file_content(self, file_path) -> None:
        with open(file_path, "wb") as f:
            f.write(self.FILE_CONTENT)
