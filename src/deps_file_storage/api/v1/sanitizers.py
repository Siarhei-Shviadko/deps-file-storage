import os
from functools import wraps

from werkzeug.utils import secure_filename


def sanitize_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        path = kwargs["path"]
        if path:
            kwargs["path"] = os.path.realpath(f"/{path}").strip(
                "/",
            )  # Add '/' to make path absolute and normalize it

        return func(*args, **kwargs)

    return wrapper


def sanitize_filename(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        filename = kwargs["file"].filename
        kwargs["file"].filename = secure_filename(filename)

        return func(*args, **kwargs)

    return wrapper


def async_sanitize_path(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        path = kwargs["path"]
        if path:
            kwargs["path"] = os.path.realpath(f"/{path}").strip("/")

        return await func(*args, **kwargs)

    return wrapper


def async_sanitize_filename(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        filename = kwargs["file"].filename
        kwargs["file"].filename = secure_filename(filename)

        return await func(*args, **kwargs)

    return wrapper
