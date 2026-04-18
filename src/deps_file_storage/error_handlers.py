import logging
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request

from deps_file_storage.api.models.error import ErrorModel
from deps_file_storage.exceptions import (
    AlreadyExistException,
    ForbiddenError,
    LogicalException,
    NotFoundException,
    StorageException,
    UnacceptableMimetypeException,
)

logger = logging.getLogger(__name__)


def json_error_handler(error: StorageException, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content=ErrorModel(code=error.code, message=str(error)).model_dump(),
    )  # noqa: WPS221


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StorageException)
    def handle_storage_exception(req: Request, error: StorageException):
        mapper = [
            (LogicalException, HTTPStatus.BAD_REQUEST),
            (AlreadyExistException, HTTPStatus.CONFLICT),
            (ForbiddenError, HTTPStatus.FORBIDDEN),
            (NotFoundException, HTTPStatus.NOT_FOUND),
            (UnacceptableMimetypeException, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
        ]

        for error_type, status_code in mapper:
            if issubclass(type(error), error_type):
                return json_error_handler(error, status_code)

    @app.exception_handler(ValidationError)
    def bad_request(req: Request, exc: ValidationError):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=ErrorModel(code="bad_request", message=str(exc)).model_dump(),
        )

    @app.exception_handler(Exception)
    def handle_all_errors(req: Request, error: Exception):
        logger.error(f"Unhandled error {error}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorModel(code="unhandled_error", message=str(error)).model_dump(),
        )
