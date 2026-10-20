from typing import List, Optional

from sqlalchemy import and_, delete, insert, select

from deps_file_storage.domain.interfaces import IOrganisationHasFileRepository
from deps_file_storage.extras.datasource import Database
from deps_file_storage.infrastructure.models import organisation_has_file_table
from deps_file_storage.infrastructure.repositories.user_has_file import (
    UserHasFileRepository,
)


class OrganisationHasFileRepository(
    IOrganisationHasFileRepository,
    UserHasFileRepository,
):
    def __init__(self, database: Database) -> None:
        super().__init__(database=database)

    def add_file_to_user_and_organisation(
        self,
        filename: str,
        user_pk: str,
        organisation_name: str,
    ) -> None:
        query = insert(organisation_has_file_table).values(
            filename=filename,
            organisation_name=organisation_name,
        )

        with self.database.connection() as conn:
            self.add_file_to_user(filename, user_pk)
            conn.execute(query)

    def remove_file_from_users_and_organisation(self, filename: str) -> None:
        query = delete(organisation_has_file_table).where(
            organisation_has_file_table.c.filename == filename,
        )

        with self.database.connection() as conn:
            self.remove_file_from_users(filename)
            conn.execute(query)

    def get_organisation_files(self, organisation_name: str) -> List[str]:
        query = select(organisation_has_file_table.c.filename).where(
            organisation_has_file_table.c.organisation_name == organisation_name,
        )

        with self.database.connection() as conn:
            filename_rows = conn.execute(query).fetchall()

        return [filename_row[0] for filename_row in filename_rows]

    def get_organisation_file_by_name(self, organisation_name: str, file_name: str) -> Optional[str]:
        query = select(organisation_has_file_table.c.filename).where(
            and_(
                organisation_has_file_table.c.filename == file_name,
                organisation_has_file_table.c.organisation_name == organisation_name,
            ),
        )

        with self.database.connection() as conn:
            return conn.execute(query).fetchone()
