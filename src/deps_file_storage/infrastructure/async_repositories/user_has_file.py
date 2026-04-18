from operator import itemgetter
from typing import List, Optional

from deps_async_datasource import AsyncDatabase

from deps_file_storage.domain.async_interfaces import IAsyncUserHasFileRepository

from .query_factories import UserHasFileQueryFactory

__all__ = ["AsyncUserHasFileRepository"]


class AsyncUserHasFileRepository(IAsyncUserHasFileRepository):
    def __init__(self, database: AsyncDatabase) -> None:
        self.database = database
        self._query_factory = UserHasFileQueryFactory()

    async def add_file_to_user(self, filename: str, user_id: str) -> None:
        async with self.database.connection() as conn:
            await conn.execute(self._query_factory.add_file(), user_id, filename)

    async def get_user_files(self, user_id: str) -> List[str]:
        async with self.database.connection() as conn:
            files = await conn.fetch(self._query_factory.get_user_files_by_user_id(), user_id)

        return list(map(itemgetter(0), files))

    async def get_user_file_by_name(self, user_id: str, filename: str) -> Optional[str]:
        async with self.database.connection() as conn:
            return await conn.fetchval(self._query_factory.get_user_file_by_file_name(), user_id, filename)

    async def remove_file_from_users(self, filename: str) -> bool:
        async with self.database.connection() as conn:
            removal_result = await conn.fetchval(self._query_factory.remove_file(), filename)

        return bool(removal_result)
