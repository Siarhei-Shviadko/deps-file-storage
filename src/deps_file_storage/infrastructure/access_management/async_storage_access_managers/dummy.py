from deps_file_storage.domain.async_interfaces import IAsyncStorageServiceAccessManager

__all__ = ["AsyncDummyAccessManager"]


class AsyncDummyAccessManager(IAsyncStorageServiceAccessManager):
    async def check_is_accessible_file(self, file: str) -> None:
        return None

    async def grant_file_access(self, file: str) -> None:
        return None

    async def remove_file_access(self, file: str) -> None:
        return None
