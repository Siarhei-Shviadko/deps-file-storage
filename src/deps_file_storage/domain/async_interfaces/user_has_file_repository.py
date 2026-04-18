from abc import ABC, abstractmethod
from typing import List, Optional

__all__ = ["IAsyncUserHasFileRepository"]


class IAsyncUserHasFileRepository(ABC):
    @abstractmethod
    async def add_file_to_user(self, filename: str, user_id: str) -> None:
        pass

    @abstractmethod
    async def get_user_files(self, user_id: str) -> List[str]:
        pass

    @abstractmethod
    async def get_user_file_by_name(self, user_id: str, filename: str) -> Optional[str]:
        pass

    @abstractmethod
    async def remove_file_from_users(self, filename: str) -> bool:
        pass
