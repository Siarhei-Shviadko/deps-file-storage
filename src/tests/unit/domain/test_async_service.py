import pytest

from deps_file_storage.exceptions import NotFoundException

STORAGE_NAME = "FILE_STORAGE"


@pytest.fixture
def async_file_storage_mock(services, mocker):
    mock = mocker.Mock(services.async_storage_service.kwargs["registered_storages"].kwargs["FILE_STORAGE"].cls)
    with services.async_storage_service.kwargs["registered_storages"].kwargs["FILE_STORAGE"].override(mock):
        yield mock


@pytest.fixture
def async_storage_service(async_file_storage_mock, services):
    yield services.async_storage_service()


@pytest.mark.asyncio
class TestAsyncStorageService:
    async def test_get_storage__non_existent_name__error(self, async_storage_service, file_factory):
        file = file_factory()

        with pytest.raises(NotFoundException):
            await async_storage_service.upload(
                path=file.filename,
                content=file.content,
                replace_if_exists=True,
                storage_name="NON_EXISTENT_STORAGE",
            )

    async def test_upload(self, async_storage_service, async_file_storage_mock, file_factory):
        file = file_factory()
        async_file_storage_mock.upload.return_value = file.filename

        res = await async_storage_service.upload(
            path=file.filename,
            content=file.content,
            replace_if_exists=True,
            storage_name=STORAGE_NAME,
        )

        assert res == file.filename
        async_file_storage_mock.upload.assert_awaited_once_with(file.filename, file.content, True)

    async def test_download(self, async_storage_service, async_file_storage_mock, file_factory):
        file = file_factory()
        async_file_storage_mock.download.return_value = file

        res = await async_storage_service.download(path=file.filename, storage_name=STORAGE_NAME)

        assert res == file
        async_file_storage_mock.download.assert_awaited_once_with(file.filename)

    async def test_delete(self, async_storage_service, async_file_storage_mock, file_factory):
        file = file_factory()
        async_file_storage_mock.delete.return_value = None

        res = await async_storage_service.delete(path=file.filename, storage_name=STORAGE_NAME)

        assert res is None
        async_file_storage_mock.delete.assert_awaited_once_with(file.filename)

    async def test_ping(self, async_storage_service, async_file_storage_mock):
        async_file_storage_mock.ping.return_value = None

        res = await async_storage_service.ping(storage_name=STORAGE_NAME)

        assert res is None
        async_file_storage_mock.ping.assert_awaited_once_with()
