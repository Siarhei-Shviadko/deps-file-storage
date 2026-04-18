import os.path
from unittest import mock

import pytest

from deps_file_storage.exceptions import ForbiddenError


@pytest.mark.usefixtures("set_user_permission", "set_test_user")
class TestStorageServiceAccessor:
    def test_download__user_has_access_to_file__file_returned(self, storage_service_accessor, mock_repositories, file_factory):
        file = file_factory()
        mock_repositories.user_has_file_repository().get_user_file_by_name.return_value = file.filename

        with mock.patch("pathlib.Path.read_bytes", return_value=file.content):
            res = storage_service_accessor.download(file.filename, "FILE_STORAGE")

        file.filename = os.path.basename(file.filename)

        assert res == file

    def test_download__user_has_no_access_to_file__forbidden_error_is_raised(self, storage_service_accessor, mock_repositories):
        mock_repositories.user_has_file_repository().get_user_file_by_name.return_value = None

        with pytest.raises(ForbiddenError):
            storage_service_accessor.download("test-file", "FILE_STORAGE")
