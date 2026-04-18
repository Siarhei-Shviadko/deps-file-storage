import os
from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile
from starlette.responses import StreamingResponse

from deps_file_storage.api.endpoint_marker import MarkerRoute
from deps_file_storage.api.endpoint_visibility import Visibility
from deps_file_storage.api.utils.headers import get_download_headers
from deps_file_storage.api.v1.sanitizers import sanitize_filename, sanitize_path
from deps_file_storage.config import get_settings
from deps_file_storage.constants import ALLOWED_FILE_EXTENSIONS
from deps_file_storage.containers import Containers
from deps_file_storage.domain.interfaces import IStorageService

router = APIRouter(prefix="/file", route_class=MarkerRoute)


@router.get(
    "/{path:path}",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
@sanitize_path
def download_file(
    path: str,
    storage: Optional[str] = Query(get_settings().default_storage),
    storage_service: IStorageService = Depends(
        Provide[Containers.storage_service_accessor],
    ),
):
    file_obj = storage_service.download(path=path, storage_name=storage)
    return StreamingResponse(
        content=chunk_data(file_obj.content),
        headers=get_download_headers(file_obj.filename),
    )


@router.post(
    "/{path:path}",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
@sanitize_path
@sanitize_filename
def upload_file_with_path(
    path: str = "",
    file: UploadFile = File(...),
    replace_if_exists: bool = Form(default=False, alias="replaceIfExists"),
    storage: Optional[str] = Form(get_settings().default_storage),
    storage_service: IStorageService = Depends(
        Provide[Containers.storage_service_accessor],
    ),
):
    return upload_file(
        path=path,
        file=file,
        replace_if_exists=replace_if_exists,
        storage=storage,
        storage_service=storage_service,
    )


@router.post(
    "",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
@sanitize_filename
def upload_file_without_path(
    file: UploadFile = File(...),
    replace_if_exists: bool = Form(default=False, alias="replaceIfExists"),
    storage: Optional[str] = Form(get_settings().default_storage),
    storage_service: IStorageService = Depends(
        Provide[Containers.storage_service_accessor],
    ),
):
    return upload_file(
        path="",
        file=file,
        replace_if_exists=replace_if_exists,
        storage=storage,
        storage_service=storage_service,
    )


def _get_extension(filename):
    _, ext = os.path.splitext(filename)
    return ext[1:].lower() if ext else ""


def upload_file(
    path: str = "",
    file: UploadFile = File(...),
    replace_if_exists: bool = Form(default=False, alias="replaceIfExists"),
    storage: Optional[str] = Form(get_settings().default_storage),
    storage_service: IStorageService = Depends(
        Provide[Containers.storage_service_accessor],
    ),
):
    file_extension = _get_extension(file.filename)
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        notes_for_error = "Upload file extension: {0}".format(file_extension)
        return Response(content=notes_for_error, status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    path = os.path.join(path, file.filename).strip("/")
    upload_path = storage_service.upload(
        path=path,
        content=file.file.read(),
        replace_if_exists=replace_if_exists,
        storage_name=storage,
    )

    return {"path": upload_path}


def chunk_data(content: bytes):
    """
    Chunk file content into one pieces so StreamingResponse should not stream per one byte
    """
    chunk_size = 1000000  # 1 MB
    chunk_begin_offset = 0
    chunk = content[chunk_begin_offset : chunk_begin_offset + chunk_size]  # noqa: E203
    while chunk:
        yield chunk
        chunk_begin_offset += chunk_size
        chunk = content[chunk_begin_offset : chunk_begin_offset + chunk_size]  # noqa: E203


@router.delete(
    "/{path:path}",
    status_code=HTTPStatus.NO_CONTENT,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
@sanitize_path
def delete_file(
    path: str,
    storage: Optional[str] = Form(get_settings().default_storage),
    storage_service: IStorageService = Depends(
        Provide[Containers.storage_service_accessor],
    ),
):
    storage_service.delete(path=path, storage_name=storage)
    # None  is not a valid response for NO_CONTENT status code, so we need to
    # explicitly return Response()
    # See: https://github.com/tiangolo/fastapi/issues/2253
    return Response(status_code=HTTPStatus.NO_CONTENT)
