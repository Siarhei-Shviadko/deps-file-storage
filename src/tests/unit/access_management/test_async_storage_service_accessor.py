import pytest


@pytest.fixture
def async_storage_service_accessor(services, async_storage_access_manager_mock, async_storage_service_mock):
    return services.async_storage_service_accessor()


@pytest.mark.asyncio
class TestAsyncStorageServiceAccessor:
    _storage_name = "FILE_STORAGE"

    async def test_upload(
        self,
        file_factory,
        async_storage_service_accessor,
        async_storage_service_mock,
        async_storage_access_manager_mock,
    ):
        file = file_factory()
        async_storage_access_manager_mock.grant_file_access.return_value = None
        async_storage_service_mock.upload.return_value = file.filename

        res = await async_storage_service_accessor.upload(
            path=file.filename,
            content=file.content,
            replace_if_exists=True,
            storage_name=self._storage_name,
        )

        assert res == file.filename
        async_storage_access_manager_mock.grant_file_access.assert_awaited_once_with(file=file.filename)
        async_storage_service_mock.upload.assert_awaited_once_with(
            path=file.filename,
            content=file.content,
            replace_if_exists=True,
            storage_name=self._storage_name,
        )

    async def test_download(
        self,
        file_factory,
        async_storage_service_accessor,
        async_storage_service_mock,
        async_storage_access_manager_mock,
    ):
        file = file_factory()
        async_storage_access_manager_mock.check_is_accessible_file.return_value = None
        async_storage_service_mock.download.return_value = file

        res = await async_storage_service_accessor.download(
            path=file.filename,
            storage_name=self._storage_name,
        )

        assert res == file
        async_storage_access_manager_mock.check_is_accessible_file.assert_awaited_once_with(file=file.filename)
        async_storage_service_mock.download.assert_awaited_once_with(
            path=file.filename,
            storage_name=self._storage_name,
        )

    async def test_delete(
        self,
        file_factory,
        async_storage_service_accessor,
        async_storage_service_mock,
        async_storage_access_manager_mock,
    ):
        file = file_factory()
        async_storage_access_manager_mock.check_is_accessible_file.return_value = None
        async_storage_access_manager_mock.remove_file_access.return_value = None
        async_storage_service_mock.delete.return_value = None

        res = await async_storage_service_accessor.delete(
            path=file.filename,
            storage_name=self._storage_name,
        )

        assert res is None
        async_storage_access_manager_mock.check_is_accessible_file.assert_awaited_once_with(file=file.filename)
        async_storage_access_manager_mock.remove_file_access.assert_awaited_once_with(file=file.filename)
        async_storage_service_mock.delete.assert_awaited_once_with(
            path=file.filename,
            storage_name=self._storage_name,
        )

    async def test_ping(
        self,
        async_storage_service_accessor,
        async_storage_service_mock,
    ):
        async_storage_service_mock.ping.return_value = None

        res = await async_storage_service_accessor.ping(
            storage_name=self._storage_name,
        )

        assert res is None
        async_storage_service_mock.ping.assert_awaited_once_with(storage_name=self._storage_name)
