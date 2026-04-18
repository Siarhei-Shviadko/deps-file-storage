import pytest_asyncio
from pytest_factoryboy import register

from deps_file_storage.storage import AsyncFileStorage
from tests.factories import MEDIA_ROOT, AioFileFactory


@pytest_asyncio.fixture
def async_file_storage():
    return AsyncFileStorage(media_root=MEDIA_ROOT)


register(AioFileFactory)
