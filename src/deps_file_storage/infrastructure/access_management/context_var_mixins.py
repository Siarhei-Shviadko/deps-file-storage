from typing import Any, Dict, Optional

from .context_vars import user

__all__ = ["CurrentUserMixin"]


class CurrentUserMixin:
    @property
    def current_user(self) -> Optional[Dict[str, Any]]:
        return user.get(None)
