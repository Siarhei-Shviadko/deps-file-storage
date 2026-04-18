from deps_file_storage.domain.async_interfaces import (
    IAsyncStorageServiceAccessManager,
    IAsyncUserHasFileRepository,
)
from deps_file_storage.exceptions import ForbiddenError

from ..context_var_mixins import CurrentUserMixin

__all__ = ["AsyncUserBasedAccessManager"]


class AsyncUserBasedAccessManager(IAsyncStorageServiceAccessManager, CurrentUserMixin):
    def __init__(
        self,
        user_has_file_repository: IAsyncUserHasFileRepository,
        admins_group: str,
    ) -> None:
        self._user_has_file_repository = user_has_file_repository
        self._admins_group = admins_group

    async def check_is_accessible_file(self, file: str) -> None:
        if self._user_is_admin():
            return None

        user_file = await self._user_has_file_repository.get_user_file_by_name(
            user_id=self.current_user["subject"],
            filename=file,
        )
        if user_file is None:
            raise ForbiddenError(f"User has no access to file {file}")

    async def grant_file_access(self, file: str) -> None:
        await self._user_has_file_repository.add_file_to_user(filename=file, user_id=self.current_user["subject"])

    async def remove_file_access(self, file: str) -> None:
        await self._user_has_file_repository.remove_file_from_users(filename=file)

    def _user_is_admin(self) -> bool:
        return self.current_user["organisation"] == self._admins_group
