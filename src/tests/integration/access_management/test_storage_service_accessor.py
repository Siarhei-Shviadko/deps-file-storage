import os.path

import pytest

from deps_file_storage.exceptions import ForbiddenError
from deps_file_storage.infrastructure.access_management.context_vars import user


@pytest.mark.usefixtures("set_user_permission", "set_test_user")
class TestStorageServiceAccessor:
    def test_upload__file_does_not_exist__user_gets_access_to_file(self, storage_service_accessor, repositories, file_factory):
        file = file_factory()

        res = storage_service_accessor.upload(
            file.filename,
            file.content,
            replace_if_exists=False,
            storage_name="FILE_STORAGE",
        )

        repo = repositories.user_has_file_repository()

        assert res == file.filename
        assert file.filename in repo.get_user_files(user.get()["subject"])

    def test_download__user_has_access_to_file__file_returned(self, storage_service_accessor, file_factory):
        file = file_factory()

        storage_service_accessor.upload(
            file.filename,
            file.content,
            replace_if_exists=True,
            storage_name="FILE_STORAGE",
        )

        res = storage_service_accessor.download(file.filename, "FILE_STORAGE")

        file.filename = os.path.basename(file.filename)

        assert res == file

    def test_download__user_tries_to_get_other_users_files__forbidden_error_is_raised(
        self, storage_service_accessor, file_factory
    ):
        file = file_factory()

        storage_service_accessor.upload(
            file.filename,
            file.content,
            replace_if_exists=True,
            storage_name="FILE_STORAGE",
        )

        user.set({"subject": "other", "groups": ["other"]})

        with pytest.raises(ForbiddenError):
            storage_service_accessor.download(file.filename, "FILE_STORAGE")

    def test_delete__user_has_access_to_file__file_deleted(self, storage_service_accessor, repositories, file_factory):
        file = file_factory()

        storage_service_accessor.upload(
            file.filename,
            file.content,
            replace_if_exists=True,
            storage_name="FILE_STORAGE",
        )

        repo = repositories.user_has_file_repository()

        storage_service_accessor.delete(file.filename, "FILE_STORAGE")

        assert file.filename not in repo.get_user_files(user.get()["subject"])

    def test_delete__user_tries_to_delete_other_users_files__forbidden_error_is_raised(
        self, storage_service_accessor, file_factory
    ):
        file = file_factory()

        storage_service_accessor.upload(
            file.filename,
            file.content,
            replace_if_exists=True,
            storage_name="FILE_STORAGE",
        )

        user.set({"subject": "other", "groups": ["other"]})

        with pytest.raises(ForbiddenError):
            storage_service_accessor.delete(file.filename, "FILE_STORAGE")

    def test_download__admin_tries_to_get_other_users_files__file_returned(
        self, storage_service_accessor, file_factory, admin_user
    ):
        file = file_factory()

        storage_service_accessor.upload(
            file.filename,
            file.content,
            replace_if_exists=True,
            storage_name="FILE_STORAGE",
        )

        user.set(admin_user)

        res = storage_service_accessor.download(file.filename, "FILE_STORAGE")

        file.filename = os.path.basename(file.filename)

        assert res == file

    def test_delete__admin_tries_to_delete_other_users_files__file_deleted(
        self, storage_service_accessor, repositories, file_factory, admin_user
    ):
        file = file_factory()

        initial_user_id = user.get()["subject"]

        storage_service_accessor.upload(
            file.filename,
            file.content,
            replace_if_exists=True,
            storage_name="FILE_STORAGE",
        )

        user.set(admin_user)
        repo = repositories.user_has_file_repository()

        storage_service_accessor.delete(file.filename, "FILE_STORAGE")

        assert file.filename not in repo.get_user_files(initial_user_id)
