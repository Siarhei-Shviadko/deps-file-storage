import os
from http import HTTPStatus
from io import BytesIO
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from deps_file_storage.api import v1
from deps_file_storage.app import create_app
from deps_file_storage.infrastructure.access_management.constants import (
    StoragePermissionRuleEnum,
)


@pytest.fixture
def async_app():
    old_routes = v1.v1_router.routes[:]
    v1.v1_router.routes.clear()
    v1.v1_router.include_router(v1.async_storage_router)
    app = create_app()

    yield app

    v1.v1_router.routes.clear()
    v1.v1_router.routes.extend(old_routes)


@pytest.fixture
def set_organisation_permission(async_app):
    with async_app.app.containers.async_storage_service_access_manager.selector.override(StoragePermissionRuleEnum.ORGANISATION):
        yield


@pytest_asyncio.fixture
async def client(async_app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=async_app),
        base_url="http://testserver",
    ) as client:
        yield client


@pytest.mark.asyncio
@pytest.mark.usefixtures("set_organisation_permission", "set_test_user")
class TestAsyncFileStorage:
    base_url = "/api/storage/v1/file"
    default_filename = "sample.pdf"

    async def test_upload__valid_data__return_ok(self, client):
        res = await self._upload_file(client, self.default_filename)

        assert res.status_code == HTTPStatus.OK
        assert res.json()["path"] == self.default_filename

    async def test_upload__file_inside_non_existing_directory__return_filename(self, client):
        path = "foo/bar"
        res = await self._upload_file(client, self.default_filename, path=path)

        assert res.json()["path"] == path + "/" + self.default_filename

    async def test_upload__already_existing_file__return_conflict(self, client):
        await self._upload_file(client, self.default_filename)

        res = await self._upload_file(client, self.default_filename)

        assert res.status_code == HTTPStatus.CONFLICT

    async def test_upload__not_allowed_extension__415(self, client):
        filename = "file.nae"
        base_url = f"{self.base_url}/{filename}"
        res = await client.post(base_url, files={"file": (filename, b"file_content")})

        assert res.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    async def test_download__existing_file__return_ok(self, client):
        res = await self._upload_file(client, self.default_filename)
        path = res.json()["path"]

        res = await self._download_file(client, path)

        assert res.status_code == HTTPStatus.OK

    async def test_download__existing_file__return_valid_data(self, client):
        res = await self._upload_file(client, self.default_filename)
        path = res.json()["path"]

        res = await self._download_file(client, path)

        assert res.content == self._get_file(self.default_filename).read()

    async def test_download__not_existing_file__return_not_found(self, client):
        res = await self._download_file(client, "foo")

        assert res.status_code == HTTPStatus.NOT_FOUND

    async def test_delete__existing_doc__return_ok(self, client):
        res = await self._upload_file(client, self.default_filename)
        path = res.json()["path"]

        res = await self._delete_file(client, path)

        assert res.status_code == HTTPStatus.NO_CONTENT

    async def test_delete__not_existing_doc__return_not_found(self, client):
        res = await self._delete_file(client, "foo")

        assert res.status_code == HTTPStatus.NOT_FOUND

    async def test_delete__folder__return_not_found(self, client):
        path = "foo/bar"
        await self._upload_file(client, self.default_filename, path=path)

        res = await self._delete_file(client, "foo")

        assert res.status_code == HTTPStatus.NOT_FOUND

    async def _upload_file(self, client, filename, path=None):
        base_url = self.base_url
        if path is not None:
            base_url = base_url + "/" + path
        return await client.post(base_url, files={"file": (filename, self._get_file(filename))})

    async def _download_file(self, client, path):
        return await client.get(self.base_url + "/" + path)

    async def _delete_file(self, client, path):
        return await client.delete(self.base_url + "/" + path)

    @staticmethod
    def _get_file(filename):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join("../data", filename))
        with open(file_path, "rb") as f:
            data = f.read()

        return BytesIO(data)
