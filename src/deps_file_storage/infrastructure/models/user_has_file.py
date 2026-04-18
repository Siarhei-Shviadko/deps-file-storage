from sqlalchemy import Column, String, Table

from deps_file_storage.extras.datasource import metadata

user_has_file_table = Table(
    "user_has_file",
    metadata,
    Column("user_id", String),
    Column("filename", String),
)
