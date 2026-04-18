import pytest
from aiofiles import os, ospath

from deps_file_storage.exceptions import AlreadyExistException, NotFoundException
from tests.factories import MEDIA_ROOT


class TestFile:
    @pytest.mark.asyncio
    async def test_upload__file_not_exists__successful(self, aio_file, aio_file_factory):
        await aio_file.upload()

        file = aio_file_factory(path=aio_file.path, content=None)
        await file.download()

        assert aio_file.content == file.content

    @pytest.mark.asyncio
    async def test_exists__file_not_exists__false(self, aio_file):
        assert await aio_file.exists() == False

    @pytest.mark.asyncio
    async def test_exists__file_exists__true(self, aio_file):
        await aio_file.upload()

        assert await aio_file.exists() == True

    @pytest.mark.asyncio
    async def test_upload__file_exists__rewritten_without_errors(self, aio_file_factory):
        file1 = aio_file_factory()
        await file1.upload()
        file2 = aio_file_factory(path=file1.path)
        await file2.upload()

        file = aio_file_factory(path=file1.path, content=None)
        await file.download()

        assert file.content == file2.content

    @pytest.mark.asyncio
    async def test_upload__file_without_content__run_time_error(self, aio_file_factory):
        file = aio_file_factory(content=None)

        with pytest.raises(RuntimeError):
            await file.upload()

    @pytest.mark.asyncio
    async def test_upload__path_exists_as_directory__already_exists_exception(self, aio_file):
        await os.makedirs(aio_file._absolute_path, exist_ok=True)

        with pytest.raises(AlreadyExistException):
            await aio_file.upload()

    @pytest.mark.asyncio
    async def test_upload__parent_path_exists_as_file__already_exists_exception(self, aio_file, aio_file_factory):
        await aio_file.upload()
        new_file = aio_file_factory(path=f"{aio_file.path}/file.pdf")

        with pytest.raises(AlreadyExistException):
            await new_file.upload()

    @pytest.mark.asyncio
    async def test_download__content_exists__run_time_error(self, aio_file):
        with pytest.raises(RuntimeError):
            await aio_file.download()

    @pytest.mark.asyncio
    async def test_download__file_not_exists__not_found_exception(self, aio_file):
        aio_file._content = None

        with pytest.raises(NotFoundException):
            await aio_file.download()

    @pytest.mark.asyncio
    async def test_download__path_exists_as_directory__not_found_exception(self, aio_file_factory):
        file = aio_file_factory(content=None)
        await os.makedirs(file._absolute_path, exist_ok=True)

        with pytest.raises(NotFoundException) as err:
            await file.download()

        assert "Could not find the file is directory" in str(err)

    @pytest.mark.asyncio
    async def test_delete__file_exists__deleted_with_all_dirs_except_media_root(self, aio_file_factory):
        file = aio_file_factory(path="aaa/bbb/ccc/file.pdf")
        await file.upload()

        await file.delete()

        assert not await file.exists()
        assert not await ospath.exists(f"{MEDIA_ROOT}/aaa")
        assert await ospath.exists(MEDIA_ROOT)

    @pytest.mark.asyncio
    async def test_delete__file_exists__deleted_with_all_dirs_except_not_empty(self, aio_file_factory):
        file1 = aio_file_factory(path="aaa/bbb/ccc/file.pdf")
        file2 = aio_file_factory(path="aaa/file.pdf")
        await file1.upload()
        await file2.upload()

        await file1.delete()

        assert not await file1.exists()
        assert not await ospath.exists(f"{MEDIA_ROOT}/aaa/bbb")
        assert await ospath.exists(f"{MEDIA_ROOT}/aaa")
        assert await file2.exists()

    @pytest.mark.asyncio
    async def test_delete__file_not_exists__not_found_exception(self, aio_file):
        with pytest.raises(NotFoundException):
            await aio_file.delete()

    @pytest.mark.asyncio
    async def test_delete__path_exists_as_directory__not_found_exception(self, aio_file):
        await os.makedirs(aio_file._absolute_path, exist_ok=True)

        with pytest.raises(NotFoundException) as err:
            await aio_file.delete()

        assert "Could not find the file is directory" in str(err)

    @pytest.mark.asyncio
    async def test_set_content__content_exists__run_time_error(self, aio_file):
        with pytest.raises(RuntimeError):
            aio_file.content = b"content"

    @pytest.mark.asyncio
    async def test_get_content__content_doesnt_exist__run_time_error(self, aio_file_factory):
        file = aio_file_factory(content=None)
        with pytest.raises(RuntimeError):
            file.content
