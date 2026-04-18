import json

import asyncer
from google.cloud import storage
from google.oauth2 import service_account

from deps_file_storage.domain.async_interfaces import IAsyncStorageServiceProvider
from deps_file_storage.dtos import File
from deps_file_storage.exceptions import AlreadyExistException, NotFoundException

__all__ = ["AsyncGCPStorageService"]


class AsyncGCPStorageService(IAsyncStorageServiceProvider):
    def __init__(
        self,
        bucket_name: str,
        auth_key: str,
        media_expires: int,
    ) -> None:
        self.bucket_name = bucket_name
        # media_expires is how long secure uri should remain 'alive' in minutes
        self.media_expires = media_expires

        json_auth_key = json.loads(auth_key)

        credentials = service_account.Credentials.from_service_account_info(json_auth_key)
        project_id = json_auth_key.get("project_id")

        # it is expected that bucket already exists
        self.bucket = storage.Client(
            project=project_id,
            credentials=credentials,
        ).bucket(bucket_name)

        if not self.bucket.exists():
            raise NotFoundException(bucket_name, "storage")

    async def upload(self, path: str, content: bytes, replace_if_exists: bool) -> str:
        blob = self.bucket.blob(path)

        if await asyncer.asyncify(blob.exists)() and not replace_if_exists:
            raise AlreadyExistException(path)

        await asyncer.asyncify(blob.upload_from_string)(content)

        return path

    async def download(self, path: str) -> File:
        blob = await self._get_existing_blob(path)
        content = await asyncer.asyncify(blob.download_as_bytes)()

        return File(filename=path, content=content)

    async def delete(self, path: str) -> None:
        blob = await self._get_existing_blob(path)
        await asyncer.asyncify(blob.delete)()

    async def ping(self) -> None:
        await asyncer.asyncify(self.bucket.exists)()

    async def _get_existing_blob(self, path: str) -> storage.Blob:
        blob = await asyncer.asyncify(self.bucket.get_blob)(path)

        if blob is None:
            raise NotFoundException(path, "file")

        return blob
