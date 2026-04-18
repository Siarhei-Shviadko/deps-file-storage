import logging
from typing import Any, Dict, Iterable

import boto3
import magic
from botocore.exceptions import ClientError

from deps_file_storage.domain.interfaces import IStorageServiceProvider
from deps_file_storage.dtos import File
from deps_file_storage.exceptions import (
    AlreadyExistException,
    NotFoundException,
    UnacceptableMimetypeException,
)

__all__ = ["S3StorageService"]


class S3StorageService(IStorageServiceProvider):
    NOT_FOUND_ERROR_CODES = ["NoSuchBucket", "NoSuchKey"]

    def __init__(
        self,
        settings: Dict[str, Any],
        acceptable_mimetypes: Iterable[str],
    ):
        self._s3_resource = self._get_s3_client(
            settings["aws_access_key_id"],
            settings["aws_secret_access_key"],
            settings["s3_endpoint_url"],
        )
        self._bucket = settings["s3_bucket_name"]
        self.acceptable_mimetypes = acceptable_mimetypes
        self._logger = logging.getLogger(__name__)

    def upload(self, path: str, content: bytes, replace_if_exists: bool) -> str:
        mimetype = magic.from_buffer(content, mime=True)
        if mimetype not in self.acceptable_mimetypes:
            raise UnacceptableMimetypeException(path, mimetype)

        if not replace_if_exists and self.exists(path):
            raise AlreadyExistException(path)
        s3_object = self._s3_resource.Object(self._bucket, path)
        s3_object.put(Body=content)
        return path

    def download(self, path: str):
        try:  # noqa: WPS503
            file_obj = self._s3_resource.Object(self._bucket, path)
            content = file_obj.get()["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] in self.NOT_FOUND_ERROR_CODES:
                self._logger.error(f"Received error: {e.response['Error']}")
                raise NotFoundException(path, "file")
        else:
            return File(path, content)

    def delete(self, path: str) -> None:
        try:
            bucket = self._s3_resource.Bucket(self._bucket)
            bucket.objects.filter(Prefix=path).delete()
        except ClientError as e:
            if e.response["Error"]["Code"] in self.NOT_FOUND_ERROR_CODES:
                self._logger.error(f"Received error: {e.response['Error']}")
                raise NotFoundException(path, "file")

    def ping(self) -> None:
        # TODO: make proper ping logic
        return None

    def exists(self, path: str) -> bool:
        try:
            self._s3_resource.Object(self._bucket, path).load()
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
        return True

    @staticmethod
    def _get_s3_client(
        aws_access_key_id: str,
        aws_secret_access_key: str,
        endpoint_url: str,
    ):
        aws_auth_params = {}
        if aws_access_key_id:
            aws_auth_params["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            aws_auth_params["aws_secret_access_key"] = aws_secret_access_key

        return boto3.resource("s3", endpoint_url=endpoint_url or None, **aws_auth_params)
