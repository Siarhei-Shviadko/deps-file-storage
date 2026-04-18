import pytest_asyncio
from deps_async_datasource import AsyncDatabase


@pytest_asyncio.fixture
async def session(async_database: AsyncDatabase):
    connection = await async_database.acquire_connection()
    transaction = connection.transaction()

    try:
        await transaction.start()
        yield
    finally:
        await transaction.rollback()
        await async_database.release_connection(connection)


@pytest_asyncio.fixture()
async def async_organisation_has_file_repository(repositories):
    yield await repositories.async_organisation_has_file_repository()


@pytest_asyncio.fixture()
async def async_user_has_file_repository(repositories):
    yield await repositories.async_user_has_file_repository()
