from uuid import uuid4

import pytest

from deps_file_storage.infrastructure.async_repositories import (
    AsyncOrganisationHasFileRepository,
    AsyncUserHasFileRepository,
)


@pytest.mark.usefixtures("session")
class TestAsyncOrganisationHasFileRepository:
    @pytest.mark.asyncio
    async def test_add_file_to_user_and_organisation_and_remove_it(
        self,
        async_organisation_has_file_repository: AsyncOrganisationHasFileRepository,
        faker,
    ):
        user_id, organisation_name, filename = uuid4().hex, uuid4().hex, faker.file_name()
        await async_organisation_has_file_repository.add_file_to_user_and_organisation(
            filename,
            user_id,
            organisation_name,
        )

        filenames = await async_organisation_has_file_repository.get_organisation_files(organisation_name)
        assert filename in filenames

        await async_organisation_has_file_repository.remove_file_from_users_and_organisation(filename)
        filenames = await async_organisation_has_file_repository.get_organisation_files(organisation_name)
        assert filename not in filenames

    @pytest.mark.asyncio
    async def test_add_file_to_user_and_organisation__same_user_different_orgs(
        self,
        async_organisation_has_file_repository: AsyncOrganisationHasFileRepository,
        async_user_has_file_repository: AsyncUserHasFileRepository,
        faker,
    ):
        user_id = uuid4().hex
        organisation1_name, organisation2_name = uuid4().hex, uuid4().hex
        filename1, filename2 = faker.file_name(), faker.file_name()

        await async_organisation_has_file_repository.add_file_to_user_and_organisation(
            filename1,
            user_id,
            organisation1_name,
        )
        await async_organisation_has_file_repository.add_file_to_user_and_organisation(
            filename2,
            user_id,
            organisation2_name,
        )

        filenames = await async_organisation_has_file_repository.get_organisation_files(organisation1_name)
        assert 1 == len(filenames)
        assert filename1 in filenames

        filenames = await async_organisation_has_file_repository.get_organisation_files(organisation2_name)
        assert 1 == len(filenames)
        assert filename2 in filenames

        filenames = await async_user_has_file_repository.get_user_files(user_id)
        assert 2 == len(filenames)
        assert [filename1, filename2] == filenames

    @pytest.mark.asyncio
    async def test_add_file_to_user_and_organisation__different_users_same_org(
        self,
        async_organisation_has_file_repository: AsyncOrganisationHasFileRepository,
        async_user_has_file_repository: AsyncUserHasFileRepository,
        faker,
    ):
        user1_id, user2_id = uuid4().hex, uuid4().hex
        organisation_name = uuid4().hex
        filename1, filename2 = faker.file_name(), faker.file_name()

        await async_organisation_has_file_repository.add_file_to_user_and_organisation(
            filename1,
            user1_id,
            organisation_name,
        )
        await async_organisation_has_file_repository.add_file_to_user_and_organisation(
            filename2,
            user2_id,
            organisation_name,
        )

        filenames = await async_organisation_has_file_repository.get_organisation_files(organisation_name)
        assert 2 == len(filenames)
        assert [filename1, filename2] == filenames

        filenames = await async_user_has_file_repository.get_user_files(user1_id)
        assert filename1 in filenames and filename2 not in filenames
