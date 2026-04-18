import pytest

from deps_file_storage.exceptions import ForbiddenError


@pytest.fixture
def user_based_access_manager(storage_service_access_manager):
    return storage_service_access_manager.user()


@pytest.mark.usefixtures("set_test_user")
class TestGroupBaseAccessManager:
    def test_access_manager__user_has_file__error_is_not_raised(self, user_based_access_manager, mock_repositories):
        filepath = "/home/user/image.png"

        mock_repositories.user_has_file_repository().get_user_file_by_name.return_value = filepath

        user_based_access_manager.check_is_accessible_file(filepath)

    def test_access_manager__user_does_not_has_file__error_is_raised(self, user_based_access_manager, mock_repositories):
        mock_repositories.user_has_file_repository().get_user_file_by_name.return_value = None

        with pytest.raises(ForbiddenError):
            user_based_access_manager.check_is_accessible_file("/some/file/that/does/not/exist")
