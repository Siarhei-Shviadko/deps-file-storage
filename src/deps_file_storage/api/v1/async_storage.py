import os
from http import HTTPStatus
from typing import Iterator, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile
from starlette.responses import StreamingResponse

from deps_file_storage.api.endpoint_marker import MarkerRoute
from deps_file_storage.api.endpoint_visibility import Visibility
from deps_file_storage.api.utils.headers import get_download_headers
from deps_file_storage.api.v1.sanitizers import (
    async_sanitize_filename,
    async_sanitize_path,
)
from deps_file_storage.config import get_settings
from deps_file_storage.constants import ALLOWED_FILE_EXTENSIONS
from deps_file_storage.containers import Containers
from deps_file_storage.domain.async_interfaces import IAsyncStorageService

router = APIRouter(prefix="/file", route_class=MarkerRoute)


@router.get("/{path:path}", openapi_extra={"visibility": Visibility.INTERNAL})
@inject
@async_sanitize_path
async def download_file(
    path: str,
    storage: Optional[str] = Query(get_settings().default_storage),
    storage_service: IAsyncStorageService = Depends(Provide[Containers.async_storage_service_accessor]),
):
    file_obj = await storage_service.download(path=path, storage_name=storage)
    return StreamingResponse(
        content=chunk_data(file_obj.content),
        headers=get_download_headers(file_obj.filename),
    )


@router.post("/{path:path}", openapi_extra={"visibility": Visibility.INTERNAL})
@inject
@async_sanitize_path
@async_sanitize_filename
async def upload_file_with_path(
    path: str = "",
    file: UploadFile = File(...),
    replace_if_exists: bool = Form(default=False, alias="replaceIfExists"),
    storage: Optional[str] = Form(get_settings().default_storage),
    storage_service: IAsyncStorageService = Depends(Provide[Containers.async_storage_service_accessor]),
):
    return await upload_file(
        path=path,
        file=file,
        replace_if_exists=replace_if_exists,
        storage=storage,
        storage_service=storage_service,
    )


@router.post("", openapi_extra={"visibility": Visibility.INTERNAL})
@inject
@async_sanitize_filename
async def upload_file_without_path(
    file: UploadFile = File(...),
    replace_if_exists: bool = Form(default=False, alias="replaceIfExists"),
    storage: Optional[str] = Form(get_settings().default_storage),
    storage_service: IAsyncStorageService = Depends(Provide[Containers.async_storage_service_accessor]),
):
    return await upload_file(
        path="",
        file=file,
        replace_if_exists=replace_if_exists,
        storage=storage,
        storage_service=storage_service,
    )


def _get_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext[1:].lower() if ext else ""


async def upload_file(
    path: str = "",
    file: UploadFile = File(...),
    replace_if_exists: bool = Form(default=False, alias="replaceIfExists"),
    storage: Optional[str] = Form(get_settings().default_storage),
    storage_service: IAsyncStorageService = Depends(Provide[Containers.async_storage_service_accessor]),
):
    file_extension = _get_extension(file.filename)
    if file_extension in ALLOWED_FILE_EXTENSIONS:
        path = os.path.join(path, file.filename).strip("/")
        upload_path = await storage_service.upload(
            path=path,
            content=file.file.read(),
            replace_if_exists=replace_if_exists,
            storage_name=storage,
        )

        return {"path": upload_path}

    notes_for_error = "Upload file extension: {0}".format(file_extension)
    return Response(content=notes_for_error, status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)


def chunk_data(content: bytes) -> Iterator[bytes]:
    chunk_size = 1000000  # 1 MB
    chunk_begin_offset = 0
    chunk = content[chunk_begin_offset : chunk_begin_offset + chunk_size]  # noqa: E203
    while chunk:
        yield chunk
        chunk_begin_offset += chunk_size
        chunk = content[chunk_begin_offset : chunk_begin_offset + chunk_size]  # noqa: E203


@router.delete("/{path:path}", status_code=HTTPStatus.NO_CONTENT, openapi_extra={"visibility": Visibility.INTERNAL})
@inject
@async_sanitize_path
async def delete_file(
    path: str,
    storage: Optional[str] = Form(get_settings().default_storage),
    storage_service: IAsyncStorageService = Depends(Provide[Containers.async_storage_service_accessor]),
):
    await storage_service.delete(path=path, storage_name=storage)
    return Response(status_code=HTTPStatus.NO_CONTENT)
