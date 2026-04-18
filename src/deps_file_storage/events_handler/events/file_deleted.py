from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

__all__ = ["FileDeleted"]


@dataclass
class FileDeleted(DomainEvent):
    id: str
    path: str
