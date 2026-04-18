import io
from http import HTTPStatus

from deps_file_storage.exceptions import (
    AlreadyExistException,
    ForbiddenError,
    NotFoundException,
)


class TestFileStorageApi:
    url = "/api/storage/v1/file"

    def test_get__file_exists__ok_returned(self, client, storage_service_mock, file_factory):
        file = file_factory()
        storage_service_mock.download.return_value = file

        resp = client.get(f"{self.url}/{file.filename}")

        assert resp.status_code == HTTPStatus.OK
        assert resp.content == file.content

    def test_get__file_not_found__not_found_returned(self, client, storage_service_mock):
        storage_service_mock.download.side_effect = NotFoundException("not-found", "file")

        resp = client.get(f"{self.url}/not-found")

        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_post__file_does_not_exist__ok_returned(self, client, storage_service_mock, file_factory):
        file = file_factory()
        storage_service_mock.upload.return_value = file.filename

        resp = client.post(f"{self.url}/{file.filename}", files={"file": (file.filename, io.BytesIO())})

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"path": file.filename}

    def test_post__file_does_exist__conflict_returned(self, client, storage_service_mock, file_factory):
        file = file_factory()
        storage_service_mock.upload.side_effect = AlreadyExistException(file.filename)

        resp = client.post(f"{self.url}/{file.filename}", files={"file": (file.filename, io.BytesIO())})

        assert resp.status_code == HTTPStatus.CONFLICT

    def test_delete__file_exists__no_content_returned(self, client, storage_service_mock):
        resp = client.delete(f"{self.url}/delete-me")

        assert resp.status_code == HTTPStatus.NO_CONTENT

    def test_delete__file_not_found__no_content_returned(self, client, storage_service_mock):
        storage_service_mock.delete.side_effect = NotFoundException("delete-me", "file")

        resp = client.delete(f"{self.url}/delete-me")

        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_get__user_does_not_have_access_to_file__forbidden_returned(self, client, storage_service_accessor_mock):
        storage_service_accessor_mock.download.side_effect = ForbiddenError

        resp = client.get(f"{self.url}/not-allowed")

        assert resp.status_code == HTTPStatus.FORBIDDEN
