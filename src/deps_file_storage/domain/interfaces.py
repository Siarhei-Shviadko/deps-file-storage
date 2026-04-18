from abc import ABC, abstractmethod
from typing import List, Optional

from deps_file_storage.dtos import File


class IStorageService(ABC):
    @abstractmethod
    def upload(
        self,
        path: str,
        content: bytes,
        replace_if_exists: bool,
        storage_name: str,
    ) -> str:
        pass

    @abstractmethod
    def download(self, path: str, storage_name: str) -> File:
        pass

    @abstractmethod
    def delete(self, path: str, storage_name: str) -> None:
        pass

    @abstractmethod
    def ping(self, storage_name: str) -> None:
        pass


class IStorageServiceProvider(ABC):
    @abstractmethod
    def upload(self, path: str, content: bytes, replace_if_exists: bool) -> str:
        pass

    @abstractmethod
    def download(self, path: str) -> File:
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        pass

    @abstractmethod
    def ping(self) -> None:
        pass


class IUserHasFileRepository(ABC):
    @abstractmethod
    def add_file_to_user(self, filename: str, user_pk: str) -> None:
        pass

    @abstractmethod
    def get_user_files(self, user_pk: str) -> List[str]:
        pass

    @abstractmethod
    def get_user_file_by_name(self, user_pk: str, filename: str) -> Optional[str]:
        pass

    @abstractmethod
    def remove_file_from_users(self, filename: str) -> bool:
        pass


class IOrganisationHasFileRepository(ABC):
    @abstractmethod
    def add_file_to_user_and_organisation(
        self,
        filename: str,
        user_pk: str,
        organisation_name: str,
    ) -> None:
        pass

    @abstractmethod
    def remove_file_from_users_and_organisation(self, filename: str) -> None:
        pass

    @abstractmethod
    def get_organisation_files(self, organisation_name: str) -> List[str]:
        pass

    @abstractmethod
    def get_organisation_file_by_name(self, organisation_name: str, file_name: str) -> Optional[str]:
        pass
