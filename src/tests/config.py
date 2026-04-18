import os

CONFIG = {
    "BUCKET_NAME": os.environ.get("GCP_BLOB_STORAGE_BUCKET_NAME"),
    "MEDIA_EXPIRES": 2,
    "AUTH_KEY": os.environ.get("GCP_BLOB_STORAGE_AUTH_KEY"),
    "CONNECTION_STRING": os.environ.get("AZURE_CONNECTION_STRING"),
}
