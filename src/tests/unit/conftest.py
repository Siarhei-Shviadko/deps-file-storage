import contextlib

import pytest
import pytest_asyncio
from dependency_injector.providers import Configuration, DependenciesContainer, Self

DO_NOT_OVERRIDE_OBJS = Self, DependenciesContainer, Configuration


@pytest.fixture(autouse=True)
def mock_repositories(repositories, mocker):
    with contextlib.ExitStack() as context:
        repository_providers = (x for x in repositories.providers.values() if not isinstance(x, DO_NOT_OVERRIDE_OBJS))
        for repository_provider in repository_providers:
            context.enter_context(repository_provider.override(mocker.Mock(repository_provider.cls)))

        yield repositories

    repositories.reset_override()


@pytest.fixture(autouse=True)
def services(services, mock_repositories):
    with services.repositories.override(mock_repositories):
        yield services


@pytest.fixture
def storage_service_mock(services, mocker):
    with services.storage_service.override(mocker.Mock(services.storage_service.cls)):
        yield services.storage_service()


@pytest.fixture
def storage_service_accessor_mock(services, mocker):
    with services.storage_service_accessor.override(mocker.Mock(services.storage_service_accessor.cls)):
        yield services.storage_service_accessor()


@pytest.fixture
def valid_decoded_token():
    return {"groups": ["Test group"]}


@pytest.fixture(params=[[], ["Test group 1", "Test group 2"]])
def invalid_decoded_token(request):
    return {"groups": request.param}


@pytest.fixture
def async_storage_access_manager_mock(services, mocker):
    mock = mocker.Mock(services.async_storage_service_access_manager.providers["none"].cls)
    with services.async_storage_service_access_manager.providers["none"].override(mock):
        yield services.async_storage_service_access_manager()


@pytest.fixture
def async_storage_service_mock(services, mocker):
    with services.async_storage_service.override(mocker.Mock(services.async_storage_service.cls)):
        yield services.async_storage_service()


@pytest_asyncio.fixture
def async_user_has_file_repository_mock(services):
    return services.repositories.async_user_has_file_repository()


@pytest.fixture
def async_organisation_has_file_repository_mock(services):
    return services.repositories.async_organisation_has_file_repository()
