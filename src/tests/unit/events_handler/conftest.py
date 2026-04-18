from uuid import uuid4

import pytest
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)
from faker.proxy import Faker

from deps_file_storage.events_handler.events import FileDeleted


@pytest.fixture
def file_id() -> str:
    return uuid4().hex


@pytest.fixture
def file_path(faker: Faker) -> str:
    return faker.file_path()


@pytest.fixture
def file_deleted_dee(mocker, file_id, file_path) -> DomainEventEnvelope[FileDeleted]:
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = FileDeleted(id=file_id, path=file_path)

    return dee
