from uuid import uuid4

import pytest

from deps_file_storage.exceptions import ForbiddenError


@pytest.fixture
def org_access_manager(storage_service_access_manager):
    return storage_service_access_manager.organisation()


@pytest.fixture
def org_repo(repositories):
    return repositories.organisation_has_file_repository()


@pytest.fixture
def add_file_to_org(org_repo, test_user):
    filename = uuid4().hex
    org_repo.add_file_to_user_and_organisation(filename, test_user["subject"], test_user["groups"][0])
    return filename


def test_check_access__positive(add_file_to_org, org_access_manager, set_test_user):
    org_access_manager.check_is_accessible_file(add_file_to_org)


def test_check_access__negative(org_access_manager, set_test_user):
    filename = uuid4().hex

    with pytest.raises(ForbiddenError) as excinfo:
        org_access_manager.check_is_accessible_file(filename)

    assert f"User has no access to file {filename}" == str(excinfo.value)
