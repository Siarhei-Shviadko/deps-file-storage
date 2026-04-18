# PubSub
EXCHANGER = "Documents"
FILE_EXCHANGER = "File"
QUEUE = "file_storage"
BASE_TOPIC = "blob"
DELETE_BLOB_TOPIC = f"{BASE_TOPIC}.delete"

FILE_STORAGE_COMMANDS_CHANNEL = "FileStorageCommands"
COMMANDS_QUEUE = "file-storage-commands"

# File storage
PROJECT_NAME = "file-storage"
V1_PREFIX = "/v1"
BASE_API_PREFIX = "/api/storage"
INTERNAL_API_PREFIX = "/api-internal/storage"
API_PREFIX = BASE_API_PREFIX + V1_PREFIX
SWAGGER_DOC_URL = "/docs"
DESCRIPTION = "Gateway for all storage providers"
ALLOWED_FILE_EXTENSIONS = (
    "jpg",
    "jpeg",
    "png",
    "pdf",
    "msg",
    "eml",
    "las",
    "xls",
    "xlsx",
    "xlsm",
    "xltx",
    "xltm",
    "csv",
    "docx",
    "doc",
    "json",
    "sgy",
    "tif",
    "tiff",
)
