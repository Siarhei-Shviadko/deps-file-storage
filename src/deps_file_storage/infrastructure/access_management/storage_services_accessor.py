from deps_file_storage.domain.interfaces import IStorageService
from deps_file_storage.dtos import File
from deps_file_storage.infrastructure.access_management.storage_access_manager import (
    IStorageServiceAccessManager,
)


class StorageServiceAccessor(IStorageService):
    def __init__(
        self,
        storage_service: IStorageService,
        storage_access_manager: IStorageServiceAccessManager,
    ):
        self._storage_service = storage_service
        self._storage_access_manager = storage_access_manager

    def upload(
        self,
        path: str,
        content: bytes,
        replace_if_exists: bool,
        storage_name: str,
    ) -> str:
        self._storage_access_manager.grant_file_access(path)
        return self._storage_service.upload(
            path=path,
            content=content,
            replace_if_exists=replace_if_exists,
            storage_name=storage_name,
        )

    def download(self, path: str, storage_name: str) -> File:
        self._storage_access_manager.check_is_accessible_file(path)
        return self._storage_service.download(path=path, storage_name=storage_name)

    def delete(self, path: str, storage_name: str) -> None:
        self._storage_access_manager.check_is_accessible_file(path)
        self._storage_access_manager.remove_file_access(path)
        self._storage_service.delete(path=path, storage_name=storage_name)

    def ping(self, storage_name: str) -> None:
        self._storage_service.ping(storage_name)
