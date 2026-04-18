import pytest

from deps_file_storage.exceptions import ForbiddenError
from deps_file_storage.infrastructure.access_management.context_vars import user


@pytest.fixture
def user_based_access_manager(storage_service_access_manager):
    return storage_service_access_manager.user()


@pytest.mark.usefixtures("set_test_user")
class TestGroupBaseAccessManager:
    def test_access_manager__regular_user_has_file__error_is_not_raised(self, user_based_access_manager, repositories):
        filepath = "/home/user/image.png"

        repositories.user_has_file_repository().add_file_to_user(filepath, user.get()["subject"])

        user_based_access_manager.check_is_accessible_file(filepath)

    def test_access_manager__regular_user_does_not_has_file__error_is_raised(self, user_based_access_manager, repositories):
        with pytest.raises(ForbiddenError):
            user_based_access_manager.check_is_accessible_file("/some/file/that/does/not/exist")

    def test_access_manager__user_tries_to_access_other_users_files__error_is_raised(
        self, user_based_access_manager, repositories
    ):
        filepath = "/someone's/file/do/not/touch"

        repositories.user_has_file_repository().add_file_to_user(filepath, "someone")

        with pytest.raises(ForbiddenError):
            user_based_access_manager.check_is_accessible_file(filepath)

    def test_access_manager__grant_user_access_to_file__user_can_access_that_file(self, user_based_access_manager, repositories):
        filepath = "/access/granted"

        user_based_access_manager.grant_file_access(filepath)
        user_based_access_manager.check_is_accessible_file(filepath)

    def test_access_manager__admin_tries_to_access_his_files__error_is_not_raised(
        self, user_based_access_manager, repositories, admin_user
    ):
        user.set(admin_user)
        filepath = "/cool/file/for/admin"

        repositories.user_has_file_repository().add_file_to_user(filepath, admin_user["subject"])

        user_based_access_manager.check_is_accessible_file(filepath)

    def test_access_manager__admin_tries_to_access_other_users_files__error_is_not_raised(
        self, user_based_access_manager, repositories, admin_user
    ):
        user.set(admin_user)
        filepath = "/admins/allowed"

        repositories.user_has_file_repository().add_file_to_user(filepath, "some guy")

        user_based_access_manager.check_is_accessible_file(filepath)

    def test_remove_file_access__user_has_access_to_file__access__user_has_no_access(
        self, user_based_access_manager, repositories
    ):
        filepath = "/test/file"

        repositories.user_has_file_repository().add_file_to_user(filepath, user.get()["subject"])

        user_based_access_manager.remove_file_access(filepath)

        with pytest.raises(ForbiddenError):
            user_based_access_manager.check_is_accessible_file(filepath)
