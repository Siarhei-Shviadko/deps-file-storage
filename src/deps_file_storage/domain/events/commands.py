from dataclasses import dataclass
from typing import List, Optional

from deps_message_flow.commands.common import Command

from deps_file_storage.config import get_settings


@dataclass
class DeleteFiles(Command):
    file_paths: List[str]
    storage: Optional[str] = get_settings().default_storage


@dataclass
class DeleteFilesReply(Command):
    file_paths: List[str]
