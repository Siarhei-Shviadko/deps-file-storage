from typing import List, Optional

from deps_async_datasource import AsyncDatabase

from deps_file_storage.domain.async_interfaces import (
    IAsyncOrganisationHasFileRepository,
)

from .query_factories import OrganisationHasFileQueryFactory, UserHasFileQueryFactory

__all__ = ["AsyncOrganisationHasFileRepository"]


class AsyncOrganisationHasFileRepository(IAsyncOrganisationHasFileRepository):
    def __init__(self, database: AsyncDatabase) -> None:
        self._database = database
        self._user_query_factory = UserHasFileQueryFactory()
        self._organisation_query_factory = OrganisationHasFileQueryFactory()

    async def add_file_to_user_and_organisation(
        self,
        filename: str,
        user_id: str,
        organisation_name: str,
    ) -> None:
        async with self._database.connection() as conn:
            await conn.execute(self._user_query_factory.add_file(), user_id, filename)
            await conn.execute(self._organisation_query_factory.add_file(), organisation_name, filename)

    async def remove_file_from_users_and_organisation(self, filename: str) -> None:
        async with self._database.connection() as conn:
            await conn.fetchrow(self._user_query_factory.remove_file(), filename)
            await conn.fetchrow(self._organisation_query_factory.remove_file(), filename)

    async def get_organisation_files(self, organisation_name: str) -> List[str]:
        async with self._database.connection() as conn:
            filename_rows = await conn.fetch(
                self._organisation_query_factory.get_files_for_organisation(),
                organisation_name,
            )

        return [filename_row[0] for filename_row in filename_rows]

    async def get_organisation_file_by_name(self, organisation_name: str, filename: str) -> Optional[str]:
        async with self._database.connection() as conn:
            return await conn.fetchval(
                self._organisation_query_factory.get_organisation_file_by_file_name(),
                organisation_name,
                filename,
            )
