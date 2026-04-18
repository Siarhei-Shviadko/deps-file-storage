import pytest

from deps_file_storage.dtos import File
from deps_file_storage.exceptions import AlreadyExistException, NotFoundException


class TestAsyncFileStorage:
    @pytest.mark.asyncio
    async def test_upload__file_not_exists__successful(self, async_file_storage, file_factory):
        file_in: File = file_factory()
        path = await async_file_storage.upload(file_in.filename, file_in.content, False)
        file_out = await async_file_storage.download(path)

        assert isinstance(file_out, File)
        assert file_in.filename == file_out.filename
        assert file_in.content == file_out.content

    @pytest.mark.asyncio
    async def test_upload__file_exists__rewrite_true__rewritten(self, async_file_storage, file_factory):
        file_in1 = file_factory()
        file_in2 = file_factory()
        await async_file_storage.upload(file_in1.filename, file_in1.content, False)
        path = await async_file_storage.upload(file_in1.filename, file_in2.content, True)
        file_out = await async_file_storage.download(path)

        assert file_in2.content == file_out.content

    @pytest.mark.asyncio
    async def test_upload__file_exists__rewrite_false__already_exist_exception(self, async_file_storage, file_factory):
        file_in1 = file_factory()
        file_in2 = file_factory()
        path = await async_file_storage.upload(file_in1.filename, file_in1.content, False)

        with pytest.raises(AlreadyExistException):
            await async_file_storage.upload(file_in1.filename, file_in2.content, False)

        file_out = await async_file_storage.download(path)

        assert file_in1.content == file_out.content

    @pytest.mark.asyncio
    async def test_delete__file_exists__deleted(self, async_file_storage, file_factory):
        file_in = file_factory()
        path = await async_file_storage.upload(file_in.filename, file_in.content, False)
        await async_file_storage.delete(path)

        with pytest.raises(NotFoundException):
            await async_file_storage.download(path)

    @pytest.mark.asyncio
    async def test_ping__none(self, async_file_storage):
        assert await async_file_storage.ping() is None
