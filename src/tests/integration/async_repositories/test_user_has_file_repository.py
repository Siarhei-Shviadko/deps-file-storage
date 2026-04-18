from uuid import uuid4

import pytest

from deps_file_storage.infrastructure.async_repositories import (
    AsyncUserHasFileRepository,
)


@pytest.mark.usefixtures("session")
class TestAsyncUserHasFileRepository:
    @pytest.mark.asyncio
    async def test_add_file_to_user__file_added__user_can_get_filename(
        self,
        async_user_has_file_repository: AsyncUserHasFileRepository,
        faker,
    ):
        user_id, filename = uuid4().hex, faker.file_name()
        await async_user_has_file_repository.add_file_to_user(filename, user_id)

        user_files = await async_user_has_file_repository.get_user_files(user_id)

        assert filename in user_files

    @pytest.mark.asyncio
    async def test_get_user_files__multiple_files__all_files_returned(
        self,
        async_user_has_file_repository: AsyncUserHasFileRepository,
        faker,
    ):
        user_id = uuid4().hex
        files = [faker.file_name() for _ in range(3)]
        for file in files:
            await async_user_has_file_repository.add_file_to_user(file, user_id)

        user_files = await async_user_has_file_repository.get_user_files(user_id)

        assert all(file in user_files for file in files)

    @pytest.mark.asyncio
    async def test_add_file_for_users__2_users_add_files__both_users_get_their_files(
        self,
        async_user_has_file_repository: AsyncUserHasFileRepository,
        faker,
    ):
        user_id_1, user_id_2 = uuid4().hex, uuid4().hex
        user_1_files = [faker.file_name() for _ in range(3)]
        user_2_files = [faker.file_name() for _ in range(3)]

        for file in user_1_files:
            await async_user_has_file_repository.add_file_to_user(file, user_id_1)

        for file in user_2_files:
            await async_user_has_file_repository.add_file_to_user(file, user_id_2)

        files_for_user_1 = await async_user_has_file_repository.get_user_files(user_id_1)
        files_for_user_2 = await async_user_has_file_repository.get_user_files(user_id_2)

        assert all(f in user_1_files for f in files_for_user_1)
        assert all(f in user_2_files for f in files_for_user_2)

    @pytest.mark.asyncio
    async def test_remove_file_from_user__file_exists__record_removed_from_database(
        self,
        async_user_has_file_repository: AsyncUserHasFileRepository,
        faker,
    ):
        user_id, filename = uuid4().hex, uuid4().hex
        await async_user_has_file_repository.add_file_to_user(filename, user_id)

        removed = await async_user_has_file_repository.remove_file_from_users(filename)
        files = await async_user_has_file_repository.get_user_files(user_id)

        assert removed is True
        assert filename not in files

    @pytest.mark.asyncio
    async def test_remove_file_from_user__file_does_not_exist__false_returned(
        self,
        async_user_has_file_repository: AsyncUserHasFileRepository,
        faker,
    ):
        removed = await async_user_has_file_repository.remove_file_from_users("this_file_does_not_exist")

        assert removed is False
