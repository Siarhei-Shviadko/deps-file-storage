from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile
from starlette.responses import StreamingResponse

from deps_file_storage import get_settings
from deps_file_storage.api.utils.headers import get_download_headers
from deps_file_storage.api.v1.async_storage import chunk_data, upload_file
from deps_file_storage.api.v1.sanitizers import (
    async_sanitize_filename,
    async_sanitize_path,
)
from deps_file_storage.containers import Containers
from deps_file_storage.domain.async_interfaces import IAsyncStorageService

router = APIRouter(prefix="/file")


@router.get("/{path:path}")
@inject
@async_sanitize_path
async def download_file(
    path: str,
    storage: str | None = Query(get_settings().default_storage),
    storage_service: IAsyncStorageService = Depends(Provide[Containers.async_storage_service]),
):
    file_obj = await storage_service.download(path=path, storage_name=storage)
    return StreamingResponse(
        content=chunk_data(file_obj.content),
        headers=get_download_headers(file_obj.filename),
    )


@router.post("/{path:path}")
@inject
@async_sanitize_path
@async_sanitize_filename
async def upload_file_with_path(
    path: str = "",
    file: UploadFile = File(...),
    replace_if_exists: bool = Form(default=False, alias="replaceIfExists"),
    storage: str | None = Form(get_settings().default_storage),
    storage_service: IAsyncStorageService = Depends(Provide[Containers.async_storage_service]),
):
    return await upload_file(
        path=path,
        file=file,
        replace_if_exists=replace_if_exists,
        storage=storage,
        storage_service=storage_service,
    )


@router.post("")
@inject
@async_sanitize_filename
async def upload_file_without_path(
    file: UploadFile = File(...),
    replace_if_exists: bool = Form(default=False, alias="replaceIfExists"),
    storage: str | None = Form(get_settings().default_storage),
    storage_service: IAsyncStorageService = Depends(Provide[Containers.async_storage_service]),
):
    return await upload_file(
        path="",
        file=file,
        replace_if_exists=replace_if_exists,
        storage=storage,
        storage_service=storage_service,
    )


@router.delete("/{path:path}", status_code=HTTPStatus.NO_CONTENT)
@inject
@async_sanitize_path
async def delete_file(
    path: str,
    storage: str | None = Form(get_settings().default_storage),
    storage_service: IAsyncStorageService = Depends(Provide[Containers.async_storage_service]),
):
    await storage_service.delete(path=path, storage_name=storage)
    return Response(status_code=HTTPStatus.NO_CONTENT)
