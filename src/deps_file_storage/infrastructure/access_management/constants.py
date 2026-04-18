from enum import Enum


class StoragePermissionRuleEnum(str, Enum):
    NONE = "none"
    USER = "user"
    ORGANISATION = "organisation"
