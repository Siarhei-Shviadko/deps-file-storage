from abc import ABC, abstractmethod

__all__ = ["IAsyncStorageServiceAccessManager"]


class IAsyncStorageServiceAccessManager(ABC):
    @abstractmethod
    async def check_is_accessible_file(self, file: str) -> None:
        pass

    @abstractmethod
    async def grant_file_access(self, file: str) -> None:
        pass

    @abstractmethod
    async def remove_file_access(self, file: str) -> None:
        pass
