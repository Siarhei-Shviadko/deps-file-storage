from http import HTTPStatus
from typing import Any, Dict

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request

from deps_file_storage.constants import INTERNAL_API_PREFIX
from deps_file_storage.exceptions import AuthError
from deps_file_storage.extras.auth import DepsAuthService
from deps_file_storage.extras.auth.exceptions import (
    DepsAuthError,
    EmptyAuthorizationHeader,
    InvalidAuthorizationHeaderFormat,
    InvalidJWTError,
)
from deps_file_storage.infrastructure.access_management.context_vars import user

PUBLIC_ENDPOINTS = (
    "/api/storage/v1/docs",
    "/api/storage/v1/debug/500",
    "/api/storage/v1/healthcheck",
    "/favicon.ico",
    "/api/storage/v1/openapi.json",
)


@inject
def set_user_from_jwt(
    request: Request,
    auth_service: DepsAuthService = Depends(Provide["deps_auth_service"]),
) -> None:
    if request.url.path in PUBLIC_ENDPOINTS or request.url.path.startswith(INTERNAL_API_PREFIX):
        return None

    try:
        user_credentials = auth_service.authorize(request.headers)
        _validate_user_organisation(user_credentials)
        user.set(user_credentials)
    except (EmptyAuthorizationHeader, InvalidAuthorizationHeaderFormat) as e:
        raise AuthError(
            detail=str(e),
            status_code=HTTPStatus.UNAUTHORIZED,
        )
    except InvalidJWTError:
        raise AuthError(
            detail="Invalid JWT",
            status_code=HTTPStatus.UNAUTHORIZED,
        )
    except DepsAuthError as e:
        raise AuthError(
            detail=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


def _validate_user_organisation(decoded_token: Dict[str, Any]) -> None:
    if not _is_user_has_one_organisation(decoded_token):
        raise AuthError(
            detail="User without organisation or with more than one organisation.",
            status_code=HTTPStatus.FORBIDDEN,
        )


def _is_user_has_one_organisation(decoded_token: Dict[str, Any]) -> bool:
    return bool(decoded_token["groups"] and len(decoded_token["groups"]) == 1)
