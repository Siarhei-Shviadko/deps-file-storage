from sqlalchemy import Column, String, Table

from deps_file_storage.extras.datasource import metadata

organisation_has_file_table = Table(
    "organisation_has_file",
    metadata,
    Column("organisation_name", String),
    Column("filename", String),
)
