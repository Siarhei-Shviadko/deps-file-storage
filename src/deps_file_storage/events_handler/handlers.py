import logging
import os
from contextlib import suppress
from typing import List

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.consumer.command_message import CommandMessage
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)
from deps_message_flow.messaging.common import IMessage

from deps_file_storage.config import get_settings
from deps_file_storage.containers import Containers
from deps_file_storage.domain.events.commands import DeleteFilesReply
from deps_file_storage.domain.interfaces import IStorageService
from deps_file_storage.events_handler import ReplyBuilder
from deps_file_storage.exceptions import ForbiddenError, NotFoundException

logger = logging.getLogger(__name__)


def delete_files_handler(dee: DomainEventEnvelope) -> None:
    for file_path in dee.event.file_paths:
        _delete_file(file_path, dee.event.storage)


def delete_files_command_handler(command_message: CommandMessage) -> List[IMessage]:
    try:
        for file_path in command_message.command.file_paths:
            _delete_file(file_path, command_message.command.storage)

        return [ReplyBuilder.with_success(DeleteFilesReply(file_paths=command_message.command.file_paths))]

    except Exception as err:
        logger.error("Failed to delete files! \n Reason: %s" % err)

        return [ReplyBuilder.with_failure(DeleteFilesReply(file_paths=command_message.command.file_paths))]


def file_deleted_handler(dee: DomainEventEnvelope) -> None:
    _delete_file(dee.event.path, get_settings().default_storage)


@inject
def _delete_file(
    file_path: str,
    storage_name: str,
    storage_service: IStorageService = Provide[Containers.storage_service],
    files_deletion_enabled: bool = Provide[Containers.config.files_deletion_enabled],
) -> None:
    if files_deletion_enabled:
        normalized_file_path = _normalize_file_path(file_path)
        with suppress(NotFoundException, ForbiddenError):
            storage_service.delete(path=normalized_file_path, storage_name=storage_name)

    else:
        logger.info(f"File {file_path} deletion skipped.")


def _normalize_file_path(file_path):
    return os.path.realpath(f"/{file_path}").strip("/")
