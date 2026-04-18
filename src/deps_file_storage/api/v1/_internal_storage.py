from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile
from starlette.responses import StreamingResponse

from deps_file_storage.api.utils.headers import get_download_headers
from deps_file_storage.api.v1.sanitizers import sanitize_filename, sanitize_path
from deps_file_storage.api.v1.storage import chunk_data, upload_file
from deps_file_storage.config import get_settings
from deps_file_storage.containers import Containers
from deps_file_storage.domain.interfaces import IStorageService

router = APIRouter(prefix="/file")


@router.get("/{path:path}")
@inject
@sanitize_path
def download_file(
    path: str,
    storage: str | None = Query(get_settings().default_storage),
    storage_service: IStorageService = Depends(
        Provide[Containers.storage_service],
    ),
):
    file_obj = storage_service.download(path=path, storage_name=storage)
    return StreamingResponse(
        content=chunk_data(file_obj.content),
        headers=get_download_headers(file_obj.filename),
    )


@router.post("/{path:path}")
@inject
@sanitize_path
@sanitize_filename
def upload_file_with_path(
    path: str = "",
    file: UploadFile = File(...),
    replace_if_exists: bool = Form(default=False, alias="replaceIfExists"),
    storage: str | None = Form(get_settings().default_storage),
    storage_service: IStorageService = Depends(
        Provide[Containers.storage_service],
    ),
):
    return upload_file(
        path=path,
        file=file,
        replace_if_exists=replace_if_exists,
        storage=storage,
        storage_service=storage_service,
    )


@router.post("")
@inject
@sanitize_filename
def upload_file_without_path(
    file: UploadFile = File(...),
    replace_if_exists: bool = Form(default=False, alias="replaceIfExists"),
    storage: str | None = Form(get_settings().default_storage),
    storage_service: IStorageService = Depends(
        Provide[Containers.storage_service],
    ),
):
    return upload_file(
        path="",
        file=file,
        replace_if_exists=replace_if_exists,
        storage=storage,
        storage_service=storage_service,
    )


@router.delete("/{path:path}", status_code=HTTPStatus.NO_CONTENT)
@inject
@sanitize_path
def delete_file(
    path: str,
    storage: str | None = Form(get_settings().default_storage),
    storage_service: IStorageService = Depends(
        Provide[Containers.storage_service],
    ),
):
    storage_service.delete(path=path, storage_name=storage)
    return Response(status_code=HTTPStatus.NO_CONTENT)
