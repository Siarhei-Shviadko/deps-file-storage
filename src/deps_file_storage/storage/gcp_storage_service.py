import json
import os
import uuid
from pathlib import PurePosixPath

from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
from google.oauth2 import service_account

from deps_file_storage.domain.interfaces import IStorageServiceProvider
from deps_file_storage.dtos import File
from deps_file_storage.exceptions import NotFoundException

__all__ = ["GCPStorageService"]


class GCPStorageService(IStorageServiceProvider):
    def __init__(
        self,
        bucket_name: str,
        auth_key: str,
        media_expires: int,
        use_emulator: bool,
    ) -> None:
        self.bucket_name = bucket_name

        if use_emulator:
            credentials = AnonymousCredentials()
            # Project id could be any value
            project_id = "test"
        else:
            json_data = json.loads(auth_key)
            project_id = json_data.get("project_id")
            credentials = service_account.Credentials.from_service_account_info(
                json_data,
            )
        # it is expected that bucket already exists
        self.bucket = storage.Client(
            project=project_id,
            credentials=credentials,
        ).bucket(bucket_name)
        if not self.bucket.exists():
            raise NotFoundException(bucket_name, "storage")

        # media_expires is how long secure uri should remain 'alive' in minutes
        self.media_expires = media_expires

    def upload(
        self,
        file_path: str,
        content: bytes,
        replate_if_exists: bool = False,
    ) -> str:
        blob = self.bucket.blob(file_path)
        blob.upload_from_string(content)
        return file_path

    def download(self, file_path: str) -> File:
        blob = self._get_existing_blob(file_path)
        content = blob.download_as_bytes()
        return File(PurePosixPath(file_path).name, content)

    def delete(self, file_path: str) -> None:
        blob = self._get_existing_blob(file_path)
        blob.delete()

    def ping(self) -> None:
        # TODO: make proper ping logic
        return None

    def _get_existing_blob(self, file_path: str) -> storage.Blob:
        blob = self.bucket.blob(file_path)
        if not blob.exists():
            raise NotFoundException(file_path, "file")
        return blob

    @staticmethod
    def _generate_unique_file_path(file_path: str) -> str:
        root, file_name = os.path.split(file_path)
        _, ext = os.path.splitext(file_name)

        new_file_path = PurePosixPath(root).joinpath(str(uuid.uuid4().hex) + ext)
        if new_file_path.is_absolute():
            return str(new_file_path.relative_to("/"))
        return str(new_file_path)
