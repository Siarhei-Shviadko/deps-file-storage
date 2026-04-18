from faker.proxy import Faker

from deps_file_storage.events_handler.handlers import file_deleted_handler
from deps_file_storage.exceptions import NotFoundException


def test_file_deleted__no_file__no_errors(file_deleted_dee, storage_service_mock, file_path, faker: Faker):
    storage_service_mock.delete.side_effect = NotFoundException(file_path, faker.text(10))

    file_deleted_handler(file_deleted_dee)


def test_file_deleted__file_exists__no_errors(file_deleted_dee, storage_service_mock):
    storage_service_mock.delete.return_value = None

    file_deleted_handler(file_deleted_dee)
