from abc import ABC, abstractmethod

from deps_file_storage.dtos import File

__all__ = ["IAsyncStorageService"]


class IAsyncStorageService(ABC):
    @abstractmethod
    async def upload(
        self,
        path: str,
        content: bytes,
        replace_if_exists: bool,
        storage_name: str,
    ) -> str:
        pass

    @abstractmethod
    async def download(self, path: str, storage_name: str) -> File:
        pass

    @abstractmethod
    async def delete(self, path: str, storage_name: str) -> None:
        pass

    @abstractmethod
    async def ping(self, storage_name: str) -> None:
        pass
