from sqlalchemy import Column, Table

from deps_file_storage.infrastructure.models import (
    organisation_has_file_table,
    user_has_file_table,
)


class UserHasFileQueryFactory:
    def __init__(self) -> None:
        self._user_has_file_schema = user_has_file_table

    def add_file(self) -> str:
        return f"insert into {self._table_schema} values($1, $2)"

    def get_user_files_by_user_id(self) -> str:
        return f"select {self._filename} from {self._table_schema} where {self._user_id} = $1"

    def get_user_file_by_file_name(self) -> str:
        return f"select {self._filename} from {self._table_schema} where {self._user_id} = $1 and {self._filename} = $2"

    def remove_file(self) -> str:
        return f"delete from {self._table_schema} where {self._filename} = $1 returning {self._filename}"

    @property
    def _table_schema(self) -> Table:
        return self._user_has_file_schema

    @property
    def _user_id(self) -> Column:
        return self._user_has_file_schema.c.user_id

    @property
    def _filename(self) -> Column:
        return self._user_has_file_schema.c.filename


class OrganisationHasFileQueryFactory:
    def __init__(self) -> None:
        self._organisation_has_file_schema = organisation_has_file_table

    def add_file(self) -> str:
        return f"insert into {self._table_schema} values($1, $2)"

    def get_files_for_organisation(self) -> str:
        return f"select {self._filename} from {self._table_schema} where {self._organisation} = $1"

    def remove_file(self) -> str:
        return f"delete from {self._table_schema} where {self._filename} = $1"

    def get_organisation_file_by_file_name(self) -> str:
        return (
            f"select {self._filename} "
            f"from {self._table_schema} "
            f"where {self._organisation} = $1 "
            f"and {self._filename} = $2"
        )

    @property
    def _table_schema(self) -> Table:
        return self._organisation_has_file_schema

    @property
    def _filename(self) -> Column:
        return self._organisation_has_file_schema.c.filename

    @property
    def _organisation(self) -> Column:
        return self._organisation_has_file_schema.c.organisation_name
