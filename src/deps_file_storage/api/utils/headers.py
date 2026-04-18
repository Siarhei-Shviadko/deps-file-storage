import mimetypes
from typing import Dict, Optional


def _get_file_mime_type(filename: str) -> Optional[str]:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type


def get_download_headers(filename: str) -> Dict[str, str]:
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    file_mime_type = _get_file_mime_type(filename)
    if file_mime_type:
        headers["Content-Type"] = file_mime_type
    return headers
