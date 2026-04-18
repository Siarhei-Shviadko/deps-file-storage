from pathlib import Path
from random import choice

import factory
from faker import Faker

from deps_file_storage.constants import ALLOWED_FILE_EXTENSIONS
from deps_file_storage.storage import AioFile

__all__ = ["AioFileFactory", "MEDIA_ROOT"]

MEDIA_ROOT = Path("/media/files")
faker = Faker()


class AioFileFactory(factory.Factory):
    class Meta:
        model = AioFile

    path = faker.file_name(extension=choice(ALLOWED_FILE_EXTENSIONS))
    content = faker.text().encode()
    media_root = MEDIA_ROOT
