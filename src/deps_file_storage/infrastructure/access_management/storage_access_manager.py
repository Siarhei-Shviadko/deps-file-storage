from typing import Optional

from deps_file_storage.domain.interfaces import (
    IOrganisationHasFileRepository,
    IUserHasFileRepository,
)
from deps_file_storage.exceptions import ForbiddenError
from deps_file_storage.extras.value_objects import UserValueObject
from deps_file_storage.infrastructure.access_management.context_vars import user
from deps_file_storage.infrastructure.interfaces import IStorageServiceAccessManager


class DummyAccessManager(IStorageServiceAccessManager):
    def check_is_accessible_file(self, file: str) -> None:
        return None

    def grant_file_access(self, file: str) -> None:
        return None

    def remove_file_access(self, file: str) -> None:
        return None


class CurrentUserMixin:
    @property
    def current_user(self) -> Optional[UserValueObject]:
        user_credentials = user.get(None)
        if user_credentials is not None:
            return UserValueObject(**user_credentials)

        return user_credentials


class UserBasedAccessManager(IStorageServiceAccessManager, CurrentUserMixin):
    def __init__(
        self,
        user_has_file_repository: IUserHasFileRepository,
        admins_group: str,
    ):
        self._user_has_file_repository = user_has_file_repository
        self._admins_group = admins_group

    def check_is_accessible_file(self, file: str) -> None:
        if self._user_is_admin():
            return None

        user_file = self._user_has_file_repository.get_user_file_by_name(
            user_pk=self.current_user.subject,
            filename=file,
        )
        if user_file is None:
            raise ForbiddenError(f"User has no access to file {file}")

    def grant_file_access(self, file: str) -> None:
        self._user_has_file_repository.add_file_to_user(file, self.current_user.subject)

    def remove_file_access(self, file: str) -> None:
        self._user_has_file_repository.remove_file_from_users(file)

    def _user_is_admin(self) -> bool:
        return self._admins_group in self.current_user.groups


class OrganisationBasedAccessManager(IStorageServiceAccessManager, CurrentUserMixin):
    def __init__(
        self,
        organisation_has_file_repository: IOrganisationHasFileRepository,
    ):
        self._organisation_has_file_repository = organisation_has_file_repository

    def check_is_accessible_file(self, file: str) -> None:
        organisation_file = self._organisation_has_file_repository.get_organisation_file_by_name(
            organisation_name=self.current_user.organisation,
            file_name=file,
        )
        if organisation_file is None:
            raise ForbiddenError(f"User has no access to file {file}")

    def grant_file_access(self, file: str) -> None:
        self._organisation_has_file_repository.add_file_to_user_and_organisation(
            file,
            self.current_user.subject,
            self.current_user.organisation,
        )

    def remove_file_access(self, file: str) -> None:
        self._organisation_has_file_repository.remove_file_from_users_and_organisation(
            file,
        )
