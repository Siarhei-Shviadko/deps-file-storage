from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob.aio import ContainerClient

from deps_file_storage.domain.async_interfaces import IAsyncStorageServiceProvider
from deps_file_storage.dtos import File
from deps_file_storage.exceptions import AlreadyExistException, NotFoundException

__all__ = ["AsyncAzureStorageService"]


class AsyncAzureStorageService(IAsyncStorageServiceProvider):
    def __init__(self, connection_string: str, container_name: str):
        self._container_client = ContainerClient.from_connection_string(
            conn_str=connection_string,
            container_name=container_name,
        )
        self._container_name = container_name

    async def upload(self, path: str, content: bytes, replace_if_exists: bool) -> str:
        blob_client = self._container_client.get_blob_client(path)
        try:
            await blob_client.upload_blob(content, overwrite=replace_if_exists)
        except ResourceExistsError:
            raise AlreadyExistException(path)
        return path

    async def download(self, path: str) -> File:
        blob_client = self._container_client.get_blob_client(path)
        try:
            stream = await blob_client.download_blob()
            content = await stream.readall()
        except ResourceNotFoundError:
            raise NotFoundException(path, "file")
        return File(filename=path, content=content)

    async def delete(self, path: str) -> None:
        blob_client = self._container_client.get_blob_client(path)
        try:
            await blob_client.delete_blob()
        except ResourceNotFoundError:
            raise NotFoundException(path, "file")

    async def ping(self) -> None:
        exists = await self._container_client.exists()
        if not exists:
            raise NotFoundException(self._container_name, "storage")
