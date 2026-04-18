from operator import itemgetter
from typing import List, Optional

from sqlalchemy import and_, delete, insert, select

from deps_file_storage.domain.interfaces import IUserHasFileRepository
from deps_file_storage.extras.datasource import Database
from deps_file_storage.infrastructure.models.user_has_file import user_has_file_table


class UserHasFileRepository(IUserHasFileRepository):
    def __init__(self, database: Database) -> None:
        self.database = database

    def add_file_to_user(self, filename: str, user_pk: str) -> None:
        stmt = insert(user_has_file_table).values(filename=filename, user_id=user_pk)

        with self.database.connection() as conn:
            conn.execute(stmt)

    def get_user_files(self, user_pk: str) -> List[str]:
        stmt = select([user_has_file_table.c.filename]).where(
            user_has_file_table.c.user_id == user_pk,
        )

        with self.database.connection() as conn:
            files = conn.execute(stmt).fetchall()

        return list(map(itemgetter(0), files))

    def get_user_file_by_name(self, user_pk: str, filename: str) -> Optional[str]:
        query = select([user_has_file_table.c.filename]).where(
            and_(
                user_has_file_table.c.filename == filename,
                user_has_file_table.c.user_id == user_pk,
            ),
        )

        with self.database.connection() as conn:
            return conn.execute(query).fetchone()

    def remove_file_from_users(self, filename: str) -> bool:
        stmt = (
            delete(user_has_file_table)
            .where(user_has_file_table.c.filename == filename)
            .returning(user_has_file_table.c.filename)
        )

        with self.database.connection() as conn:
            removal_result = conn.execute(stmt).fetchone()

        return bool(removal_result)
