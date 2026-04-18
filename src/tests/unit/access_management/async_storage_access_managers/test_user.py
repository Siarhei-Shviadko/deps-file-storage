import pytest

from deps_file_storage.exceptions import ForbiddenError
from deps_file_storage.infrastructure.access_management import (
    AsyncUserBasedAccessManager,
)


@pytest.fixture
def async_user_access_manager(async_access_manager):
    return async_access_manager.user()


@pytest.mark.asyncio
@pytest.mark.usefixtures("set_test_user")
class TestAsyncUserBasedAccessManager:
    async def test_access_manager__is_user(self, async_user_access_manager):
        assert isinstance(async_user_access_manager, AsyncUserBasedAccessManager)

    async def test_check_is_accessible_file__accessible__none(
        self,
        async_user_access_manager: AsyncUserBasedAccessManager,
        async_user_has_file_repository_mock,
        test_user,
        file_factory,
    ):
        file = file_factory()
        async_user_has_file_repository_mock.get_user_file_by_name.return_value = file.filename

        res = await async_user_access_manager.check_is_accessible_file(file.filename)

        assert res is None
        async_user_has_file_repository_mock.get_user_file_by_name.assert_awaited_once_with(
            user_id=test_user["subject"],
            filename=file.filename,
        )

    async def test_check_is_accessible_file__not_accessible__forbidden(
        self,
        async_user_access_manager: AsyncUserBasedAccessManager,
        async_user_has_file_repository_mock,
        test_user,
        file_factory,
    ):
        file = file_factory()
        async_user_has_file_repository_mock.get_user_file_by_name.return_value = None

        with pytest.raises(ForbiddenError):
            await async_user_access_manager.check_is_accessible_file(file.filename)

        async_user_has_file_repository_mock.get_user_file_by_name.assert_awaited_once_with(
            user_id=test_user["subject"],
            filename=file.filename,
        )

    async def test_check_is_accessible_file__user_is_admin__none(
        self,
        set_admin_user,
        async_user_access_manager: AsyncUserBasedAccessManager,
        async_user_has_file_repository_mock,
        file_factory,
    ):
        file = file_factory()
        async_user_has_file_repository_mock.get_user_file_by_name.return_value = None

        res = await async_user_access_manager.check_is_accessible_file(file.filename)

        assert res is None
        async_user_has_file_repository_mock.get_user_file_by_name.assert_not_awaited()

    async def test_grant_file_access__successfully(
        self,
        async_user_access_manager: AsyncUserBasedAccessManager,
        async_user_has_file_repository_mock,
        test_user,
        file_factory,
    ):
        file = file_factory()
        async_user_has_file_repository_mock.add_file_to_user.return_value = None

        res = await async_user_access_manager.grant_file_access(file.filename)

        assert res is None
        async_user_has_file_repository_mock.add_file_to_user.assert_awaited_once_with(
            filename=file.filename, user_id=test_user["subject"]
        )

    async def test_remove_file_access__successfully(
        self,
        async_user_access_manager: AsyncUserBasedAccessManager,
        async_user_has_file_repository_mock,
        test_user,
        file_factory,
    ):
        file = file_factory()
        async_user_has_file_repository_mock.remove_file_from_users.return_value = True

        res = await async_user_access_manager.remove_file_access(file.filename)

        assert res is None
        async_user_has_file_repository_mock.remove_file_from_users.assert_awaited_once_with(
            filename=file.filename,
        )
