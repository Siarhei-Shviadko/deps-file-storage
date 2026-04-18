from abc import ABC, abstractmethod


class IStorageServiceAccessManager(ABC):
    @abstractmethod
    def check_is_accessible_file(self, file: str) -> None:
        pass

    @abstractmethod
    def grant_file_access(self, file: str) -> None:
        pass

    @abstractmethod
    def remove_file_access(self, file: str) -> None:
        pass
