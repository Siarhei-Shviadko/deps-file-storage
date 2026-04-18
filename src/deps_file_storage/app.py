import logging
import os
from typing import Awaitable, Callable

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import Response

from deps_file_storage import auth, constants, events_handler
from deps_file_storage.api import service_info, service_info_router, v1
from deps_file_storage.config import BlobStorageSettings
from deps_file_storage.containers import Application
from deps_file_storage.error_handlers import json_error_handler, register_error_handlers
from deps_file_storage.exceptions import AuthError
from deps_file_storage.extras.fastapi_utils import add_auth_to_openapi
from deps_file_storage.infrastructure.access_management.context_vars import user

logger = logging.getLogger(__name__)


def init_application(settings: BlobStorageSettings) -> Application:
    app = Application(messaging_driver_settings=settings.messaging_driver_settings)
    app.config.from_pydantic(settings)
    app.init_resources()
    if app.config.authentication.enabled():
        app.message_brokers.broker_client().user_context = user

    app.containers.wire(packages=(v1, events_handler), modules=[auth])
    app.core.wire((service_info,))
    return app


def register_auth(app: FastAPI):
    add_auth_to_openapi(app)

    @app.middleware("http")
    async def handle_authorization(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            auth.set_user_from_jwt(request)
        except AuthError as err:
            return json_error_handler(err, err.status_code)
        return await call_next(request)


def create_app() -> FastAPI:
    settings = BlobStorageSettings()

    app = init_application(settings)
    _base_service_init(app)

    fastapi_app = FastAPI(
        title=constants.PROJECT_NAME,
        version="1.0.0",
        docs_url=f"{constants.API_PREFIX}{constants.SWAGGER_DOC_URL}" if settings.documentation_enabled else None,
        description=constants.DESCRIPTION,
        openapi_url=f"{constants.API_PREFIX}/openapi.json" if settings.documentation_enabled else None,
    )

    fastapi_app.app = app
    fastapi_app.include_router(prefix=constants.API_PREFIX, router=v1.v1_router)
    fastapi_app.include_router(prefix=constants.BASE_API_PREFIX, router=service_info_router)
    fastapi_app.include_router(prefix=constants.INTERNAL_API_PREFIX, router=v1.internal_router, include_in_schema=False)
    register_error_handlers(fastapi_app)

    if app.config.authentication.enabled():
        register_auth(fastapi_app)

    # TODO: add auth middleware

    if app.config.instrumentation_enabled():
        from deps_observability_instrumentation import (  # noqa: WPS433
            instrument_fast_api,
        )

        instrument_fast_api(fastapi_app)

    return fastapi_app


def run_api():
    env = os.getenv("ENV", "prod")
    options = {
        "host": "0.0.0.0",
        "port": 8004,
        "log_level": os.getenv("LOG_LEVEL", "debug").lower(),
        "reload": env == "development",
        "debug": env == "development",
    }

    uvicorn.run("deps_file_storage.app:create_app", **options)


def run_consumer() -> None:
    settings = BlobStorageSettings()
    app: Application = init_application(settings)
    _base_service_init(app)

    consumer = app.containers.consumer()
    consumer.start_consuming()


def _base_service_init(app: Application) -> None:
    if app.config.instrumentation_enabled():
        logger.info("Instrumentation enabled.")
        from deps_observability_instrumentation import (  # noqa: WPS433
            instrument_messaging,
            setup_instrumentation,
        )

        setup_instrumentation()
        instrument_messaging(app.messaging.producer(), app.messaging.consumer())
