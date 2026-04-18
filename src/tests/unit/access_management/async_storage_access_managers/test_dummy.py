import pytest

from deps_file_storage.infrastructure.access_management import AsyncDummyAccessManager


@pytest.mark.asyncio
class TestAsyncDummyAccessManager:
    async def test_access_manager__is_dummy(self, async_access_manager):
        assert isinstance(async_access_manager(), AsyncDummyAccessManager)

    async def test_check_is_accessible_file__none(self, async_access_manager, file_factory):
        file = file_factory()
        res = await async_access_manager().check_is_accessible_file(file.filename)

        assert res is None

    async def test_grant_file_access__none(self, async_access_manager, file_factory):
        file = file_factory()
        res = await async_access_manager().grant_file_access(file.filename)

        assert res is None

    async def test_remove_file_access__none(self, async_access_manager, file_factory):
        file = file_factory()
        res = await async_access_manager().remove_file_access(file.filename)

        assert res is None
