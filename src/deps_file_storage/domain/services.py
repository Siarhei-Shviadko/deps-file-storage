from typing import Callable, Dict

from deps_file_storage.domain.interfaces import IStorageService, IStorageServiceProvider
from deps_file_storage.dtos import File
from deps_file_storage.exceptions import NotFoundException


class StorageService(IStorageService):
    def __init__(
        self,
        registered_storages: Dict[str, Callable[[], IStorageServiceProvider]],
    ):
        self._registered_storages = registered_storages

    def upload(
        self,
        path: str,
        content: bytes,
        replace_if_exists: bool,
        storage_name: str,
    ) -> str:
        return self._get_storage(storage_name).upload(path, content, replace_if_exists)

    def download(self, path: str, storage_name: str) -> File:
        return self._get_storage(storage_name).download(path)

    def delete(self, path: str, storage_name: str) -> None:
        self._get_storage(storage_name).delete(path)

    def ping(self, storage_name: str) -> None:
        return self._get_storage(storage_name).ping()

    def _get_storage(self, storage_name: str) -> IStorageServiceProvider:
        storage = self._registered_storages.get(storage_name, None)
        if storage is None:
            raise NotFoundException(storage_name, "storage")

        return storage()
