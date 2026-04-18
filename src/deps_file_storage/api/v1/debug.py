from fastapi import APIRouter

from deps_file_storage.api.endpoint_marker import MarkerRoute
from deps_file_storage.api.endpoint_visibility import Visibility

router = APIRouter(prefix="/debug", route_class=MarkerRoute)


@router.get(
    "/500",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
def return_internal_server_error():
    raise ValueError
