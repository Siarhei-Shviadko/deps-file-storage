import io
from http import HTTPStatus
from typing import Final

from deps_file_storage.exceptions import (
    AlreadyExistException,
    ForbiddenError,
    NotFoundException,
)

URL: Final[str] = "/api-internal/storage/file"


def test_get__file_exists__ok_returned(client, storage_service_mock, file_factory):
    file = file_factory()
    storage_service_mock.download.return_value = file

    resp = client.get(f"{URL}/{file.filename}")

    assert resp.status_code == HTTPStatus.OK
    assert resp.content == file.content


def test_get__file_not_found__not_found_returned(client, storage_service_mock):
    storage_service_mock.download.side_effect = NotFoundException("not-found", "file")

    resp = client.get(f"{URL}/not-found")

    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_post__file_does_not_exist__ok_returned(client, storage_service_mock, file_factory):
    file = file_factory()
    storage_service_mock.upload.return_value = file.filename

    resp = client.post(f"{URL}/{file.filename}", files={"file": (file.filename, io.BytesIO())})

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"path": file.filename}


def test_post__file_does_exist__conflict_returned(client, storage_service_mock, file_factory):
    file = file_factory()
    storage_service_mock.upload.side_effect = AlreadyExistException(file.filename)

    resp = client.post(f"{URL}/{file.filename}", files={"file": (file.filename, io.BytesIO())})

    assert resp.status_code == HTTPStatus.CONFLICT


def test_delete__file_exists__no_content_returned(client, storage_service_mock):
    resp = client.delete(f"{URL}/delete-me")

    assert resp.status_code == HTTPStatus.NO_CONTENT


def test_delete__file_not_found__no_content_returned(client, storage_service_mock):
    storage_service_mock.delete.side_effect = NotFoundException("delete-me", "file")

    resp = client.delete(f"{URL}/delete-me")

    assert resp.status_code == HTTPStatus.NOT_FOUND
