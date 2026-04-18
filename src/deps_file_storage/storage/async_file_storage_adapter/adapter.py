from pathlib import Path

from ...domain.async_interfaces import IAsyncStorageServiceProvider
from ...dtos import File
from ...exceptions import AlreadyExistException
from .file import AioFile

__all__ = ["AsyncFileStorage"]


class AsyncFileStorage(IAsyncStorageServiceProvider):
    def __init__(self, media_root: Path) -> None:
        self._media_root = media_root

    async def upload(self, path: str, content: bytes, replace_if_exists: bool) -> str:
        file = AioFile(path=path, content=content, media_root=self._media_root)
        if await file.exists() and not replace_if_exists:
            raise AlreadyExistException(path)
        await file.upload()

        return path

    async def download(self, path: str) -> File:
        file = AioFile(path=path, media_root=self._media_root)
        await file.download()

        return File(filename=file.name, content=file.content)

    async def delete(self, path: str) -> None:
        file = AioFile(path=path, media_root=self._media_root)
        await file.delete()

    async def ping(self) -> None:
        return None
