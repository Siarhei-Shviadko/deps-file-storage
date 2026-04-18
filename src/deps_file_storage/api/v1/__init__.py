import logging

from fastapi import APIRouter

from deps_file_storage.config import get_settings

from ._internal_async_storage import (  # noqa: WPS436
    router as internal_async_storage_router,
)
from ._internal_storage import router as internal_storage_router  # noqa: WPS436
from .async_storage import router as async_storage_router
from .debug import router as debug_router
from .healthcheck import router as healthcheck_router
from .storage import router as storage_router

logger = logging.getLogger(__name__)
v1_router = APIRouter()
internal_router = APIRouter()

v1_router.include_router(debug_router)
v1_router.include_router(healthcheck_router)

_settings = get_settings()

if _settings.feature_async_file_storage:
    v1_router.include_router(async_storage_router, tags=["Files"])
    internal_router.include_router(internal_async_storage_router, tags=["Files"])
    logger.info("Async_mode_enabled...")
else:
    logger.info("Sync_mode_enabled...")
    v1_router.include_router(storage_router, tags=["Files"])
    internal_router.include_router(internal_storage_router, tags=["Files"])
