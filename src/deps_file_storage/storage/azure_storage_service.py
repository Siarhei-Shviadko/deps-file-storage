from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import ContainerClient

from deps_file_storage.domain.interfaces import IStorageServiceProvider
from deps_file_storage.dtos import File
from deps_file_storage.exceptions import AlreadyExistException, NotFoundException

__all__ = ["AzureStorageService"]


class AzureStorageService(IStorageServiceProvider):
    def __init__(self, connection_string: str, container_name: str):
        self._container_client = ContainerClient.from_connection_string(
            conn_str=connection_string,
            container_name=container_name,
        )
        if not self._container_client.exists():
            raise NotFoundException(container_name, "storage")

        self._container_name = container_name

    def upload(self, path: str, content: bytes, replace_if_exists: bool) -> str:
        blob_client = self._container_client.get_blob_client(path)
        try:
            blob_client.upload_blob(content, overwrite=replace_if_exists)
        except ResourceExistsError:
            raise AlreadyExistException(path)
        return path

    def download(self, path: str) -> File:
        blob_client = self._container_client.get_blob_client(path)
        try:
            content = blob_client.download_blob().readall()
        except ResourceNotFoundError:
            raise NotFoundException(path, "file")
        return File(path, content)

    def delete(self, path: str) -> None:
        blob_client = self._container_client.get_blob_client(path)
        try:
            blob_client.delete_blob()
        except ResourceNotFoundError:
            raise NotFoundException(path, "file")

    def ping(self) -> None:
        exists = self._container_client.exists()
        if not exists:
            raise NotFoundException(self._container_name, "storage")
