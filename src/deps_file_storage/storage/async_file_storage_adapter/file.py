from pathlib import Path
from typing import Optional

from aiofiles import open as aio_open
from aiofiles import os as aio_os
from aiofiles import ospath as aio_os_path

from ...exceptions import AlreadyExistException, NotFoundException

__all__ = ["AioFile"]


class AioFile:
    def __init__(self, path: str, content: Optional[bytes] = None, media_root: Path = Path()) -> None:
        self._path = path
        self._content = content
        self._media_root = media_root
        self._absolute_path: Path = self._get_absolute_path(self._media_root)

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        return self._absolute_path.name

    @property
    def content(self) -> bytes:
        if self._content is None:
            raise RuntimeError("Content doesn't exist")

        return self._content

    @content.setter
    def content(self, value: bytes) -> None:
        if self._content is not None:
            raise RuntimeError("Content already exists")
        self._content = value

    async def exists(self) -> bool:
        return await aio_os_path.exists(self._absolute_path)

    async def upload(self) -> None:
        try:
            await self._create_directory()
            await self._upload_content()
        except (IsADirectoryError, FileExistsError):
            raise AlreadyExistException(self._path)

    async def download(self) -> None:
        try:
            await self._download_content()
        except FileNotFoundError:
            raise NotFoundException(self._path, "file")
        except IsADirectoryError:
            raise NotFoundException(self._path, "file is directory")

    async def delete(self) -> None:
        try:
            await self._delete_content()
        except FileNotFoundError:
            raise NotFoundException(self._path, "file")
        except IsADirectoryError:
            raise NotFoundException(self._path, "file is directory")

        await self._delete_dir()

    def _get_absolute_path(self, media_root: Path) -> Path:
        return media_root / self._path

    async def _upload_content(self) -> None:
        if self._content is None:
            raise RuntimeError("Content doesn't exist")
        async with aio_open(self._absolute_path, mode="wb") as f:
            await f.write(self._content)

    async def _create_directory(self) -> None:
        await aio_os.makedirs(self._absolute_path.parent, exist_ok=True)

    async def _download_content(self) -> None:
        if self._content is not None:
            raise RuntimeError("Content already exists")
        async with aio_open(self._absolute_path, mode="rb") as f:
            self._content = await f.read()

    async def _delete_content(self) -> None:
        await aio_os.remove(self._absolute_path)

    async def _delete_dir(self) -> None:
        dir_name = self._absolute_path.parent
        while not await self._is_media_root(dir_name) and await self._is_empty_dir(dir_name):
            await aio_os.rmdir(dir_name)
            dir_name = dir_name.parent

    async def _is_media_root(self, dir_name: Path) -> bool:
        return await aio_os_path.samefile(self._media_root, dir_name)

    @staticmethod
    async def _is_empty_dir(dir_name: Path) -> bool:
        return not bool(await aio_os.listdir(dir_name))
