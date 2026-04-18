from dataclasses import dataclass
from typing import List, Optional

from deps_message_flow.events.common import DomainEvent

from deps_file_storage.config import get_settings


@dataclass
class DeleteFiles(DomainEvent):
    file_paths: List[str]
    storage: Optional[str] = get_settings().default_storage
