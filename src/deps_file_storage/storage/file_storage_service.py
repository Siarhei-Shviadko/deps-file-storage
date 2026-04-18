import logging
import os
from pathlib import Path
from typing import List, Optional

from cryptography.fernet import Fernet

from deps_file_storage.domain.interfaces import IStorageServiceProvider
from deps_file_storage.dtos import File
from deps_file_storage.exceptions import AlreadyExistException, NotFoundException

__all__ = ["FileStorageService"]

logger = logging.getLogger(__name__)


class FileStorageService(IStorageServiceProvider):
    FILE_UPLOAD_PERMISSIONS = 0o777

    def __init__(self, media_root: Path, acceptable_mimetypes: List[str], cipher_key: bytes = b"") -> None:
        self.media_root = media_root
        self.acceptable_mimetypes = acceptable_mimetypes
        self._cipher: Optional[Fernet] = Fernet(cipher_key) if cipher_key else None

    def upload(self, path: str, content: bytes, replace_if_exists: bool) -> str:
        absolute_path = self._get_absolute_path(path)
        try:
            absolute_path.parent.mkdir(
                self.FILE_UPLOAD_PERMISSIONS,
                parents=True,
                exist_ok=True,
            )
            if absolute_path.exists() and not replace_if_exists:
                raise AlreadyExistException(path)
            data = content if self._cipher is None else self._cipher.encrypt(content)
            absolute_path.write_bytes(data)
        except FileExistsError:
            raise AlreadyExistException(path)
        except IsADirectoryError:
            raise AlreadyExistException(path)

        return path

    def download(self, path: str) -> File:
        absolute_path = self._get_absolute_path(path)
        try:
            raw_content = absolute_path.read_bytes()
        except FileNotFoundError:
            raise NotFoundException(path, "file")
        except IsADirectoryError:
            raise NotFoundException(path, "file is directory")
        filename = absolute_path.name
        content = raw_content if self._cipher is None else self._cipher.decrypt(raw_content)
        return File(filename, content)

    def delete(self, path: str) -> None:
        absolute_path = self._get_absolute_path(path)
        try:
            absolute_path.unlink()
            self._delete_dir_if_empty(absolute_path)
        except FileNotFoundError:
            raise NotFoundException(path, "file")
        except IsADirectoryError:
            raise NotFoundException(path, "file is directory")

    def ping(self) -> None:
        return None

    def _get_absolute_path(self, path: str) -> Path:
        """Generate absolute path using template: 'self.media_root/file_path/'
        :param path: path to the file directory in the destination storage;
        :return: file directory absolute path.
        """
        return Path(self.media_root) / path

    def _delete_dir_if_empty(self, path: Path) -> None:
        """Removes container folder if there are no more files associated with it."""
        dir_name = path.parent
        while not self.media_root.samefile(dir_name) and not os.listdir(dir_name):
            Path(dir_name).rmdir()
            dir_name = dir_name.parent
