from abc import ABC, abstractmethod

from deps_file_storage.dtos import File

__all__ = ["IAsyncStorageServiceProvider"]


class IAsyncStorageServiceProvider(ABC):
    @abstractmethod
    async def upload(self, path: str, content: bytes, replace_if_exists: bool) -> str:
        pass

    @abstractmethod
    async def download(self, path: str) -> File:
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        pass

    @abstractmethod
    async def ping(self) -> None:
        pass
