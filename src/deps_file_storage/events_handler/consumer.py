import logging

from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.events.subscriber import (
    DomainEventDispatcher,
    DomainEventHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_file_storage.constants import (
    COMMANDS_QUEUE,
    EXCHANGER,
    FILE_EXCHANGER,
    FILE_STORAGE_COMMANDS_CHANNEL,
    QUEUE,
)
from deps_file_storage.domain.events.commands import DeleteFiles as DeleteFilesCommand
from deps_file_storage.domain.events.events import DeleteFiles

from .events import FileDeleted

_logger = logging.getLogger(__name__)


def make_consumer(
    subscriber: IMessageConsumer,
    producer: IMessageProducer,
) -> IMessageConsumer:
    from deps_file_storage.events_handler.handlers import (  # noqa: WPS433
        delete_files_command_handler,
        delete_files_handler,
        file_deleted_handler,
    )

    _logger.info("Start consuming...")

    events_handlers = (
        DomainEventHandlersBuilder.for_aggregate_type(EXCHANGER)
        .on_event(DeleteFiles, delete_files_handler)
        .and_for_aggregate_type(FILE_EXCHANGER)
        .on_event(FileDeleted, file_deleted_handler)
        .for_queue(QUEUE)
        .build()
    )

    commands_handlers = (
        CommandHandlersBuilder.from_channel(FILE_STORAGE_COMMANDS_CHANNEL)
        .on_message(DeleteFilesCommand, delete_files_command_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    ded = DomainEventDispatcher(events_handlers, subscriber)
    ded.initialize()

    cd = CommandDispatcher(commands_handlers, subscriber, producer)
    cd.initialize()

    return subscriber
