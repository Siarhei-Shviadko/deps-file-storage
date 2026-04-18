import pytest


@pytest.mark.asyncio
async def test_async_database(async_database):
    await async_database.healthcheck()
