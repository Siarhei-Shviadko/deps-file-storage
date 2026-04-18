from abc import ABC, abstractmethod
from typing import List, Optional

__all__ = ["IAsyncOrganisationHasFileRepository"]


class IAsyncOrganisationHasFileRepository(ABC):
    @abstractmethod
    async def add_file_to_user_and_organisation(
        self,
        filename: str,
        user_id: str,
        organisation_name: str,
    ) -> None:
        pass

    @abstractmethod
    async def remove_file_from_users_and_organisation(self, filename: str) -> None:
        pass

    @abstractmethod
    async def get_organisation_files(self, organisation_name: str) -> List[str]:
        pass

    @abstractmethod
    async def get_organisation_file_by_name(self, organisation_name: str, filename: str) -> Optional[str]:
        pass
