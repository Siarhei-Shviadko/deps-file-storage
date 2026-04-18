from deps_file_storage.domain.async_interfaces import (
    IAsyncStorageService,
    IAsyncStorageServiceAccessManager,
)
from deps_file_storage.dtos import File

__all__ = ["AsyncStorageServiceAccessor"]


class AsyncStorageServiceAccessor(IAsyncStorageService):
    def __init__(
        self,
        storage_service: IAsyncStorageService,
        storage_access_manager: IAsyncStorageServiceAccessManager,
    ) -> None:
        self._storage_service = storage_service
        self._storage_access_manager = storage_access_manager

    async def upload(
        self,
        path: str,
        content: bytes,
        replace_if_exists: bool,
        storage_name: str,
    ) -> str:
        await self._storage_access_manager.grant_file_access(file=path)
        return await self._storage_service.upload(
            path=path,
            content=content,
            replace_if_exists=replace_if_exists,
            storage_name=storage_name,
        )

    async def download(self, path: str, storage_name: str) -> File:
        await self._storage_access_manager.check_is_accessible_file(file=path)
        return await self._storage_service.download(path=path, storage_name=storage_name)

    async def delete(self, path: str, storage_name: str) -> None:
        await self._storage_access_manager.check_is_accessible_file(file=path)
        await self._storage_access_manager.remove_file_access(file=path)
        await self._storage_service.delete(path=path, storage_name=storage_name)

    async def ping(self, storage_name: str) -> None:
        await self._storage_service.ping(storage_name=storage_name)
