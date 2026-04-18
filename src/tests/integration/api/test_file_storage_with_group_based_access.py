import io
import os.path
from http import HTTPStatus

import pytest

from deps_file_storage.infrastructure.access_management.context_vars import user


@pytest.mark.usefixtures("set_user_permission", "set_test_user")
class TestStorageApiWithGroupBasedAuthentication:
    url = "api/storage/v1/file"

    def test_post__file_not_allowed_extension__error_returned(self, client, repositories, file_factory_not_allowed_extension):
        file = file_factory_not_allowed_extension()
        filename = os.path.basename(file.filename)

        resp = client.post(self.url, files={"file": (filename, io.BytesIO(file.content))})

        assert resp.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    def test_post__file_does_not_exist__file_accessible_to_user(self, client, repositories, file_factory):
        file = file_factory()
        filename = os.path.basename(file.filename)

        resp = client.post(self.url, files={"file": (filename, io.BytesIO(file.content))})

        assert resp.status_code == HTTPStatus.OK
        assert filename in repositories.user_has_file_repository().get_user_files(user.get()["subject"])

    def test_get__user_has_access_to_file__file_returned(self, client, file_factory):
        file = file_factory()
        filename = os.path.basename(file.filename)

        client.post(self.url, files={"file": (filename, io.BytesIO(file.content))})

        resp = client.get(f"{self.url}/{filename}")

        assert resp.status_code == HTTPStatus.OK
        assert resp.content == file.content

    def test_get__user_has_no_access_to_file__forbidden_returned(self, client):
        resp = client.get(f"{self.url}/not-allowed")

        assert resp.status_code == HTTPStatus.FORBIDDEN

    def test_get__user_tries_to_get_other_users_files__forbidden_returned(self, client, file_factory):
        file = file_factory()
        filename = os.path.basename(file.filename)

        client.post(self.url, files={"file": (filename, io.BytesIO(file.content))})

        user.set({"subject": "other", "groups": ["other"]})

        resp = client.get(f"{self.url}/{filename}")

        assert resp.status_code == HTTPStatus.FORBIDDEN

    def test_delete__user_has_access_to_file__no_content_returned(self, client, file_factory):
        file = file_factory()
        filename = os.path.basename(file.filename)

        client.post(self.url, files={"file": (filename, io.BytesIO(file.content))})

        resp = client.delete(f"{self.url}/{filename}")

        assert resp.status_code == HTTPStatus.NO_CONTENT

    def test_delete__user_has_no_access_to_file__forbidden_returned(self, client):
        resp = client.delete(f"{self.url}/not-allowed")

        assert resp.status_code == HTTPStatus.FORBIDDEN

    def test_delete__user_tries_to_delete_other_users_files__forbidden_returned(self, client, file_factory):
        file = file_factory()
        filename = os.path.basename(file.filename)

        client.post(self.url, files={"file": (filename, io.BytesIO(file.content))})

        user.set({"subject": "other", "groups": ["other"]})

        resp = client.delete(f"{self.url}/{filename}")

        assert resp.status_code == HTTPStatus.FORBIDDEN

    def test_get__admin_tries_to_get_other_users_files__file_returned(self, client, repositories, file_factory, admin_user):
        file = file_factory()
        filename = os.path.basename(file.filename)

        client.post(self.url, files={"file": (filename, io.BytesIO(file.content))})

        user.set(admin_user)

        resp = client.get(f"{self.url}/{filename}")

        admin_files = repositories.user_has_file_repository().get_user_files(admin_user["subject"])

        assert resp.status_code == HTTPStatus.OK
        assert filename not in admin_files

    def test_delete__admin_tries_to_delete_other_users_files__no_content(self, client, file_factory, admin_user):
        file = file_factory()
        filename = os.path.basename(file.filename)

        client.post(self.url, files={"file": (filename, io.BytesIO(file.content))})

        user.set(admin_user)

        resp = client.delete(f"{self.url}/{filename}")

        assert resp.status_code == HTTPStatus.NO_CONTENT
