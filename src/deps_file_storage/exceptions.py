from http import HTTPStatus
from typing import Optional


class StorageException(Exception):
    """StorageException - base exception for other class of exceptions"""

    code = "storage_exception"


class LogicalException(StorageException):
    """LogicalError - raises, when user tries to perform an illogical operation"""

    code = "logical_exception"


class ForbiddenError(StorageException):
    code = "document_forbidden_error"


class AuthError(StorageException):
    code = "authentication_error"

    def __init__(self, detail: str, status_code: int = HTTPStatus.UNAUTHORIZED) -> None:
        super().__init__(detail)
        self.status_code = status_code


class NotFoundException(StorageException):
    """NotFoundError - raises, when user trying to get an nonexistent object"""

    code = "not_found_exception"

    def __init__(self, object_name: str, object_type: str):
        """
        Raises, when user trying to get an nonexistent object.
        :param object_name: name of the object, that user trying to found;
        :param object_type: type of the object (file, directory, ...) that
        user user trying to found.
        """
        super().__init__(f"Could not find the {object_type} '{object_name}'")


class AlreadyExistException(StorageException):
    """AlreadyExistException - raises, when user trying to create already existent object"""

    code = "already_exist_exception"

    def __init__(self, object_name: str):
        """
        Raises, when user trying to create already existent object.
        :param object_name: name of the object, that user trying to found;
        user user trying to found.
        """
        super().__init__(f"Resource '{object_name}' already exists")


class UnacceptableMimetypeException(StorageException):
    """UnacceptableMimetypeException - raises, when user trying to load file with unacceptable mimetype"""

    code = "unacceptable_mimetype_exception"

    def __init__(self, object_name: str, mimetype: Optional[str] = None):
        """
        Raises, when user trying to load file with unacceptable mimetype.
        :param object_name: name of the object, that user trying to found;
        user user trying to found.
        """
        super().__init__(
            f"Resource '{object_name}' has unacceptable mimetype ({mimetype})",
        )
