import pytest

from deps_file_storage.exceptions import NotFoundException
from deps_file_storage.infrastructure.access_management import (
    AsyncOrganisationBasedAccessManager,
)


@pytest.fixture
def async_organisation_access_manager(async_access_manager):
    return async_access_manager.organisation()


@pytest.mark.asyncio
@pytest.mark.usefixtures("set_test_user")
class TestAsyncOrganisationBasedAccessManager:
    async def test_access_manager__is_organisation(self, async_organisation_access_manager):
        assert isinstance(async_organisation_access_manager, AsyncOrganisationBasedAccessManager)

    async def test_check_is_accessible_file__accessible__none(
        self,
        async_organisation_access_manager: AsyncOrganisationBasedAccessManager,
        async_organisation_has_file_repository_mock,
        test_user,
        file_factory,
    ):
        file = file_factory()
        async_organisation_has_file_repository_mock.get_organisation_file_by_name.return_value = file.filename

        res = await async_organisation_access_manager.check_is_accessible_file(file.filename)

        assert res is None
        async_organisation_has_file_repository_mock.get_organisation_file_by_name.assert_awaited_once_with(
            organisation_name=test_user["organisation"],
            filename=file.filename,
        )

    async def test_check_is_accessible_file__not_accessible__not_found(
        self,
        async_organisation_access_manager: AsyncOrganisationBasedAccessManager,
        async_organisation_has_file_repository_mock,
        test_user,
        file_factory,
    ):
        file = file_factory()
        async_organisation_has_file_repository_mock.get_organisation_file_by_name.return_value = None

        with pytest.raises(NotFoundException):
            await async_organisation_access_manager.check_is_accessible_file(file.filename)

        async_organisation_has_file_repository_mock.get_organisation_file_by_name.assert_awaited_once_with(
            organisation_name=test_user["organisation"],
            filename=file.filename,
        )

    async def test_grant_file_access__successfully(
        self,
        async_organisation_access_manager: AsyncOrganisationBasedAccessManager,
        async_organisation_has_file_repository_mock,
        test_user,
        file_factory,
    ):
        file = file_factory()
        async_organisation_has_file_repository_mock.add_file_to_user_and_organisation.return_value = None

        res = await async_organisation_access_manager.grant_file_access(file.filename)

        assert res is None
        async_organisation_has_file_repository_mock.add_file_to_user_and_organisation.assert_awaited_once_with(
            filename=file.filename,
            user_id=test_user["subject"],
            organisation_name=test_user["organisation"],
        )

    async def test_remove_file_access__successfully(
        self,
        async_organisation_access_manager: AsyncOrganisationBasedAccessManager,
        async_organisation_has_file_repository_mock,
        test_user,
        file_factory,
    ):
        file = file_factory()
        async_organisation_has_file_repository_mock.remove_file_from_users_and_organisation.return_value = None

        res = await async_organisation_access_manager.remove_file_access(file.filename)

        assert res is None
        async_organisation_has_file_repository_mock.remove_file_from_users_and_organisation.assert_awaited_once_with(
            filename=file.filename,
        )
