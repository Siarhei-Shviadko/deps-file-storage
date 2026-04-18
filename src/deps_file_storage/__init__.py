__version__ = "0.1.0"

import logging

from .config import get_settings

_settings = get_settings()
logging.basicConfig(
    level=_settings.logger_level,
    format="[%(asctime)s] [%(name)s: %(levelname)s] %(message)s",  # noqa: WPS323
    datefmt="%Y-%m-%d %I:%M:%S",
)
logger = logging.getLogger(__name__)
logging.getLogger("boto3").setLevel(logging.CRITICAL)
