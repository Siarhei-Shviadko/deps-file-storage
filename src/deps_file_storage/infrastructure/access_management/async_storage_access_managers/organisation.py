from deps_file_storage.domain.async_interfaces import (
    IAsyncOrganisationHasFileRepository,
    IAsyncStorageServiceAccessManager,
)
from deps_file_storage.exceptions import NotFoundException

from ..context_var_mixins import CurrentUserMixin

__all__ = ["AsyncOrganisationBasedAccessManager"]


class AsyncOrganisationBasedAccessManager(IAsyncStorageServiceAccessManager, CurrentUserMixin):
    def __init__(
        self,
        organisation_has_file_repository: IAsyncOrganisationHasFileRepository,
    ) -> None:
        self._organisation_has_file_repository = organisation_has_file_repository

    async def check_is_accessible_file(self, file: str) -> None:
        organisation_file = await self._organisation_has_file_repository.get_organisation_file_by_name(
            organisation_name=self.current_user["organisation"],
            filename=file,
        )
        if organisation_file is None:
            raise NotFoundException(object_name=file, object_type="file")

    async def grant_file_access(self, file: str) -> None:
        await self._organisation_has_file_repository.add_file_to_user_and_organisation(
            filename=file,
            user_id=self.current_user["subject"],
            organisation_name=self.current_user["organisation"],
        )

    async def remove_file_access(self, file: str) -> None:
        await self._organisation_has_file_repository.remove_file_from_users_and_organisation(filename=file)
