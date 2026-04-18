from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from deps_file_storage.api.endpoint_marker import MarkerRoute
from deps_file_storage.api.endpoint_visibility import Visibility
from deps_file_storage.containers import Containers
from deps_file_storage.domain.interfaces import IStorageService

router = APIRouter(prefix="/healthcheck", route_class=MarkerRoute)


@router.get(
    "",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def healthcheck(
    storage_type: str = Query("FILE_STORAGE"),
    storage_service: IStorageService = Depends(Provide[Containers.storage_service]),
):
    try:
        storage_service.ping(storage_type)
    except Exception as e:
        return JSONResponse(
            content={"detail": f"{storage_type} isn't configured properly: {e}"},
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )
