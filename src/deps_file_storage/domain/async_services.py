from typing import Callable, Dict

from deps_file_storage.domain.async_interfaces import (
    IAsyncStorageService,
    IAsyncStorageServiceProvider,
)
from deps_file_storage.dtos import File
from deps_file_storage.exceptions import NotFoundException

__all__ = ["AsyncStorageService"]


class AsyncStorageService(IAsyncStorageService):
    def __init__(
        self,
        registered_storages: Dict[str, Callable[[], IAsyncStorageServiceProvider]],
    ):
        self._registered_storages = registered_storages

    async def upload(
        self,
        path: str,
        content: bytes,
        replace_if_exists: bool,
        storage_name: str,
    ) -> str:
        return await self._get_storage(storage_name).upload(path, content, replace_if_exists)

    async def download(self, path: str, storage_name: str) -> File:
        return await self._get_storage(storage_name).download(path)

    async def delete(self, path: str, storage_name: str) -> None:
        await self._get_storage(storage_name).delete(path)

    async def ping(self, storage_name: str) -> None:
        return await self._get_storage(storage_name).ping()

    def _get_storage(self, storage_name: str) -> IAsyncStorageServiceProvider:
        storage = self._registered_storages.get(storage_name, None)
        if storage is None:
            raise NotFoundException(storage_name, "storage")

        return storage()
