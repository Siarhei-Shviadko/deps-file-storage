from uuid import uuid4

import pytest

from deps_file_storage.infrastructure.repositories import OrganisationHasFileRepository


@pytest.fixture
def organisation_has_file_repository(repositories):
    yield repositories.organisation_has_file_repository()


def test_add_file_to_user_and_organisation_and_remove_it(organisation_has_file_repository: OrganisationHasFileRepository, faker):
    user_pk, organisation_name, filename = uuid4().hex, uuid4().hex, faker.file_name()
    organisation_has_file_repository.add_file_to_user_and_organisation(filename, user_pk, organisation_name)

    filenames = organisation_has_file_repository.get_organisation_files(organisation_name)
    assert filename in filenames

    organisation_has_file_repository.remove_file_from_users_and_organisation(filename)
    filenames = organisation_has_file_repository.get_organisation_files(organisation_name)
    assert filename not in filenames


def test_add_file_to_user_and_organisation__same_user_different_orgs(
    organisation_has_file_repository: OrganisationHasFileRepository, faker
):
    user_pk = uuid4().hex
    organisation1_name, organisation2_name = uuid4().hex, uuid4().hex
    filename1, filename2 = faker.file_name(), faker.file_name()

    organisation_has_file_repository.add_file_to_user_and_organisation(filename1, user_pk, organisation1_name)
    organisation_has_file_repository.add_file_to_user_and_organisation(filename2, user_pk, organisation2_name)

    filenames = organisation_has_file_repository.get_organisation_files(organisation1_name)
    assert 1 == len(filenames)
    assert filename1 in filenames

    filenames = organisation_has_file_repository.get_organisation_files(organisation2_name)
    assert 1 == len(filenames)
    assert filename2 in filenames

    filenames = organisation_has_file_repository.get_user_files(user_pk)
    assert 2 == len(filenames)
    assert [filename1, filename2] == filenames


def test_add_file_to_user_and_organisation__different_users_same_org(
    organisation_has_file_repository: OrganisationHasFileRepository, faker
):
    user1_pk, user2_pk = uuid4().hex, uuid4().hex
    organisation_name = uuid4().hex
    filename1, filename2 = faker.file_name(), faker.file_name()

    organisation_has_file_repository.add_file_to_user_and_organisation(filename1, user1_pk, organisation_name)
    organisation_has_file_repository.add_file_to_user_and_organisation(filename2, user2_pk, organisation_name)

    filenames = organisation_has_file_repository.get_organisation_files(organisation_name)
    assert 2 == len(filenames)
    assert [filename1, filename2] == filenames

    filenames = organisation_has_file_repository.get_user_files(user1_pk)
    assert filename1 in filenames and filename2 not in filenames
